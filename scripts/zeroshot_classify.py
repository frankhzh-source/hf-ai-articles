"""
CLIP 零样本分类：126K 张 PCS 图片 → 5 大家居服消费者品类
用 Chinese-CLIP ViT-H/14 做零样本文本-图片匹配
"""

import torch
import numpy as np
import os
import json
import time
from PIL import Image
from transformers import ChineseCLIPModel, ChineseCLIPProcessor

# ── 路径 ──
DATA_DIR = r"E:/AI电商工作创建/LORA训练数据集"
EMB_FILE = os.path.join(DATA_DIR, "05_clip_embeddings.npy")
PATHS_FILE = os.path.join(DATA_DIR, "05_clip_paths.txt")
OUT_CSV = os.path.join(DATA_DIR, "09_zeroshot_classify.csv")
OUT_NPY = os.path.join(DATA_DIR, "09_zeroshot_scores.npy")
OUT_JSON = os.path.join(DATA_DIR, "09_zeroshot_result.json")

# ── 5 大品类 + 品类描述（与文档一致） ──
CATEGORIES = [
    "少女甜系",
    "纯欲性感", 
    "知性简约",
    "新中式国风",
    "老娘客",
]

# 品类描述（用于 CLIP 文本编码，覆盖文档中的核心关键词）
CATEGORY_PROMPTS = [
    "家居服，少女甜系风格：蝴蝶结、娃娃领、蕾丝花边、粉嫩色系、卡通萌趣、可爱甜美",
    "家居服，纯欲性感风格：冰丝吊带睡裙、微透蕾丝、V领深领、两件套外披、性感迷人",
    "家居服，知性简约风格：纯色莫兰迪色系、Oversize宽松慵懒、运动功能、舒适松弛、极简设计",
    "家居服，新中式国风风格：盘扣立领、碎花格纹、改良旗袍、水墨印花、传统国潮元素",
    "家居服，老娘客高端奢华风格：真丝丝绒、法式精致、贵气自信、深色背景、高端品质感",
]

print("=" * 60)
print("CLIP 零样本分类 — 126K PCS 图片 → 5 大品类")
print("=" * 60)

# 1. 加载模型
print("\n[1/5] 加载 Chinese-CLIP ViT-H/14...")
t0 = time.time()
device = "cuda" if torch.cuda.is_available() else "cpu"
model = ChineseCLIPModel.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14").to(device).eval()
processor = ChineseCLIPProcessor.from_pretrained("OFA-Sys/chinese-clip-vit-huge-patch14")
print(f"  设备: {device}")
print(f"  VRAM: {torch.cuda.memory_allocated()/1024**2:.0f} MB")
print(f"  耗时: {time.time()-t0:.1f}s")

# 2. 生成文本向量
print("\n[2/5] 生成 5 个品类文本向量...")
t0 = time.time()
text_inputs = processor(text=CATEGORY_PROMPTS, padding=True, return_tensors="pt").to(device)
with torch.no_grad():
    outputs = model.get_text_features(**text_inputs)
    text_features = outputs.pooler_output
    text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
text_features_np = text_features.cpu().numpy()
print(f"  文本向量形状: {text_features_np.shape}")
print(f"  耗时: {time.time()-t0:.1f}s")

# 3. 加载图片向量 + 路径
print("\n[3/5] 加载图片向量...")
t0 = time.time()
emb = np.load(EMB_FILE, mmap_mode='r')
print(f"  图片向量: {emb.shape}")
print(f"  耗时: {time.time()-t0:.1f}s")

# 加载路径
with open(PATHS_FILE, 'r', encoding='utf-8') as f:
    paths = [line.strip() for line in f if line.strip()]
print(f"  路径数: {len(paths):,}")

# 4. 计算相似度
print("\n[4/5] 计算 126K × 5 相似度矩阵...")
t0 = time.time()

# 分块计算，避免显存/内存爆
batch_size = 4096
n = emb.shape[0]
n_cat = len(CATEGORIES)
all_scores = np.zeros((n, n_cat), dtype=np.float16)
labels = np.empty(n, dtype=np.int32)
max_scores = np.empty(n, dtype=np.float16)

for start in range(0, n, batch_size):
    end = min(start + batch_size, n)
    batch = emb[start:end]
    # 图片向量已经是 L2 归一化的，可以直接点积
    scores = batch @ text_features_np.T  # (B, 5)
    all_scores[start:end] = scores.astype(np.float16)
    labels[start:end] = scores.argmax(axis=1)
    max_scores[start:end] = scores.max(axis=1)
    
    if (start // batch_size + 1) % 8 == 0:
        print(f"  进度: {end:,}/{n:,} ({end/n*100:.1f}%)")

print(f"  完成! 耗时: {time.time()-t0:.1f}s")

# 5. 统计 + 输出
print("\n[5/5] 统计结果...")
from collections import Counter
label_counts = Counter(labels)
cat_dist = {CATEGORIES[i]: int(cnt) for i, cnt in label_counts.items()}

print(f"\n=== 零样本分类结果分布 ===")
for i, cnt in label_counts.most_common():
    print(f"  {CATEGORIES[i]:12s}  {cnt:>7,d}  ({cnt/n*100:.1f}%)")
print(f"  其他(低置信度)  剩余为各品类分类结果")

# 置信度统计
p50 = np.median(max_scores)
p75 = np.percentile(max_scores, 75)
p90 = np.percentile(max_scores, 90)
print(f"\n  置信度中位数: {p50:.4f}")
print(f"  置信度 P75:  {p75:.4f}")
print(f"  置信度 P90:  {p90:.4f}")

# 输出 CSV
import csv
with open(OUT_CSV, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(["file_path", "category", "confidence", "scores_5class"])
    for i in range(n):
        scores_str = ",".join([f"{s:.4f}" for s in all_scores[i]])
        writer.writerow([paths[i], CATEGORIES[labels[i]], f"{max_scores[i]:.4f}", scores_str])
print(f"\n  CSV: {OUT_CSV}")

# 保存分数矩阵
np.save(OUT_NPY, all_scores)
print(f"  分数矩阵: {OUT_NPY}")

# 保存结果元数据
result = {
    "total": n,
    "categories": CATEGORIES,
    "distribution": cat_dist,
    "confidence_median": float(p50),
    "confidence_p75": float(p75),
    "confidence_p90": float(p90),
}
with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"  结果 JSON: {OUT_JSON}")

print(f"\n{'='*60}")
print(f"✅ 零样本分类完成！总耗时: {time.time()-t0:.0f}s")
print(f"{'='*60}")
