"""
CLIP 零样本分类 V2：126K 张 PCS 图片 → 5 大家居服消费者品类
改进：多prompt投票 + 更精准的视觉差异化描述
"""

import torch
import numpy as np
import os
import json
import time
from transformers import ChineseCLIPModel, ChineseCLIPProcessor

# ── 路径 ──
DATA_DIR = r"E:/AI电商工作创建/LORA训练数据集"
EMB_FILE = os.path.join(DATA_DIR, "05_clip_embeddings.npy")
PATHS_FILE = os.path.join(DATA_DIR, "05_clip_paths.txt")
OUT_CSV = os.path.join(DATA_DIR, "09_zeroshot_classify_v2.csv")
OUT_NPY = os.path.join(DATA_DIR, "09_zeroshot_scores_v2.npy")
OUT_JSON = os.path.join(DATA_DIR, "09_zeroshot_result_v2.json")

# ── 5 大品类 ← 每个品类配多个差异化 prompt ──
CATEGORIES = ["少女甜系", "纯欲性感", "知性简约", "新中式国风", "老娘客"]

# 每品类 3 个 prompt，每个聚焦不同视觉特征
PROMPTS_PER_CAT = {
    "少女甜系": [
        "粉嫩色系蝴蝶结娃娃领，可爱甜美家居服",
        "粉色满印卡通图案，少女风格可爱睡衣",
        "蕾丝花边娃娃领睡裙，粉红甜美少女感",
    ],
    "纯欲性感": [
        "冰丝吊带睡裙，V领蕾丝镶边性感纯欲",
        "吊带外披两件套，微透蕾丝面料性感家居服",
        "冰丝吊带深V领，蕾丝美背性感睡裙",
    ],
    "知性简约": [
        "纯色莫兰迪色系，简约舒适宽松家居服",
        "素色无图案极简风格，慵懒随性居家套装",
        "纯棉纯色基础款，简约大方舒适家居",
    ],
    "新中式国风": [
        "盘扣立领改良旗袍，水墨印花新中式家居服",
        "碎花格纹传统元素，国风改良中式睡衣",
        "水墨画印花盘扣设计，中国风传统美学家居服",
    ],
    "老娘客": [
        "真丝缎面光泽，法式精致高端奢华睡袍",
        "丝绒质感深色调，贵气优雅高品质家居服",
        "奢华丝绸面料，精致刺绣高端家居服",
    ],
}

print("=" * 60)
print("CLIP 零样本分类 V2 — 126K PCS → 5 大品类")
print("(每个品类 3 个差异化 prompt，取最高分)")
print("=" * 60)

# 1. 加载模型
print("\n[1/5] 加载 Chinese-CLIP ViT-H/14...")
t0 = time.time()
device = "cuda" if torch.cuda.is_available() else "cpu"
model = ChineseCLIPModel.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14").to(device).eval()
processor = ChineseCLIPProcessor.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14")
print(f"  设备: {device}, VRAM: {torch.cuda.memory_allocated()/1024**2:.0f} MB, 耗时: {time.time()-t0:.1f}s")

# 2. 生成所有 prompt 的文本向量（共 15 个）
print("\n[2/5] 生成 15 个品类文本向量（5品类 × 3prompt）...")
t0 = time.time()
all_prompts = []
for cat in CATEGORIES:
    all_prompts.extend(PROMPTS_PER_CAT[cat])

text_inputs = processor(text=all_prompts, padding=True, return_tensors="pt").to(device)
with torch.no_grad():
    outputs = model.get_text_features(**text_inputs)
    text_features = outputs.pooler_output
    text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
all_text_np = text_features.cpu().numpy()  # (15, 1024)
print(f"  文本向量形状: {all_text_np.shape}, 耗时: {time.time()-t0:.1f}s")

# 3. 加载图片向量
print("\n[3/5] 加载图片向量...")
t0 = time.time()
emb = np.load(EMB_FILE, mmap_mode='r')
print(f"  图片向量: {emb.shape}, 耗时: {time.time()-t0:.1f}s")

with open(PATHS_FILE, 'r', encoding='utf-8') as f:
    paths = [line.strip() for line in f if line.strip()]
print(f"  路径数: {len(paths):,}")

# 4. 计算相似度 + 跨prompt投票
print("\n[4/5] 计算 126K × 15 相似度 + 跨prompt投票...")
t0 = time.time()

batch_size = 4096
n = emb.shape[0]
n_cat = len(CATEGORIES)
all_scores = np.zeros((n, n_cat), dtype=np.float32)
labels = np.empty(n, dtype=np.int32)
max_scores = np.empty(n, dtype=np.float32)

for start in range(0, n, batch_size):
    end = min(start + batch_size, n)
    batch = emb[start:end]  # (B, 1024)
    # 所有 15 个 prompt 的分数
    all_sim = batch @ all_text_np.T  # (B, 15)
    # 按品类投票：每组 3 个 prompt，取 max
    for ci in range(n_cat):
        cat_scores = all_sim[:, ci*3:(ci+1)*3]  # (B, 3)
        all_scores[start:end, ci] = cat_scores.max(axis=1)
    
    labels[start:end] = all_scores[start:end].argmax(axis=1)
    max_scores[start:end] = all_scores[start:end].max(axis=1)

    if (start // batch_size + 1) % 16 == 0:
        elapsed = time.time() - t0
        rate = end / elapsed
        eta = (n - end) / rate if rate > 0 else 0
        print(f"  进度: {end:,}/{n:,} ({end/n*100:.0f}%)  速率: {rate:.0f}张/秒  ETA: {eta:.0f}s")

# 归一化分数（softmax-like normalization to [0,1] per row）
row_max = all_scores.max(axis=1, keepdims=True)
row_min = all_scores.min(axis=1, keepdims=True)
range_ = row_max - row_min
range_[range_ == 0] = 1
scores_norm = (all_scores - row_min) / range_

# 重新计算归一化后的标签
labels_norm = scores_norm.argmax(axis=1)

print(f"  完成! 耗时: {time.time()-t0:.0f}s")

# 5. 统计 + 输出
print("\n[5/5] 统计结果...")
from collections import Counter
label_counts = Counter(labels_norm)
cat_dist = {CATEGORIES[int(i)]: int(cnt) for i, cnt in label_counts.items()}

print(f"\n{'='*60}")
print(f"          零样本分类 V2 结果分布")
print(f"{'='*60}")
for i, cnt in label_counts.most_common():
    print(f"  {CATEGORIES[int(i)]:12s}  {cnt:>7,d}  ({cnt/n*100:.1f}%)")

print(f"\n  置信度中位数: {np.median(max_scores):.4f}")
print(f"  置信度均值:   {max_scores.mean():.4f}")

# 找出高置信度边界（>0.7 的占比高说明分类可靠）
high_conf = (max_scores > 0.35).mean()
print(f"  高置信度占比(>0.35): {high_conf*100:.1f}%")

# CSV 输出
import csv
with open(OUT_CSV, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(["file_path", "category", "confidence", "scores_5cat"])
    for i in range(n):
        s_str = ",".join([f"{scores_norm[i][j]:.4f}" for j in range(n_cat)])
        writer.writerow([paths[i], CATEGORIES[int(labels_norm[i])], f"{max_scores[i]:.4f}", s_str])
print(f"\n  CSV: {OUT_CSV}")

# 保存归一化分数
np.save(OUT_NPY, scores_norm)
print(f"  分数矩阵: {OUT_NPY}")

result = {
    "total": n,
    "version": "v2",
    "categories": CATEGORIES,
    "prompts_per_category": 3,
    "scoring": "max-of-3-prompts + row-normalized",
    "distribution": cat_dist,
    "confidence_median": float(np.median(max_scores)),
    "confidence_mean": float(max_scores.mean()),
}
with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"  结果 JSON: {OUT_JSON}")

print(f"\n{'='*60}")
print(f"✅ V2 完成！总耗时: {time.time()-t0:.0f}s")
print(f"{'='*60}")
