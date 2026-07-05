#!/usr/bin/env python3
"""
video_dissect.py — AI视频拆解分析管线

将原始视频拆解为8维度结构化数据：
  镜号 | 时间轴 | 景别 | 运镜 | 人物状态 | 服装材质 | 灯光氛围 | 参考帧

用法:
  python video_dissect.py 视频路径.mp4
  python video_dissect.py 视频路径.mp4 --api-key sk-xxx --api-base https://api.openai.com/v1
  python video_dissect.py 视频路径.mp4 --scene-only          # 只拆镜头，不调LLM
  python video_dissect.py 视频路径.mp4 --output result.json

依赖:
  pip install opencv-python openai tqdm
"""

import argparse
import base64
import json
import os
import sys
import tempfile
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

try:
    import cv2
except ImportError:
    print("❌ 需要 opencv-python: pip install opencv-python")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# ─── 配置 ─────────────────────────────────────────────

# LLM API配置（可通过命令行参数覆盖）
DEFAULT_API_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o"
DEFAULT_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# 场景检测参数
SCENE_THRESHOLD = 30.0       # 直方图差异阈值（越大越不敏感）
MIN_SCENE_SECONDS = 1.0      # 最短镜头长度（秒）
MAX_KEYFRAMES_PER_SCENE = 3  # 每镜最多提取关键帧数

# ─── 步骤1：镜头检测 ──────────────────────────────────

def detect_scenes(video_path, threshold=SCENE_THRESHOLD, min_scene_sec=MIN_SCENE_SECONDS):
    """使用OpenCV直方图差异检测场景切换。返回 [(start_sec, end_sec), ...]"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    min_scene_frames = int(min_scene_sec * fps)

    print(f"  分辨率: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}×{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    print(f"  帧率: {fps:.2f} fps, 总帧数: {total_frames}, 时长: {duration:.1f}s")

    scenes = []
    scene_start = 0
    prev_hist = None
    frame_idx = 0

    progress = tqdm(total=total_frames, desc="  检测镜头", unit="帧") if tqdm else None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        if progress:
            progress.update(1)

        # 计算当前帧的HSV直方图
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)

        if prev_hist is not None:
            diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CHISQR)
            if diff > threshold:
                scene_end = frame_idx / fps
                if scene_end - scene_start >= min_scene_sec:
                    scenes.append((scene_start, scene_end))
                scene_start = scene_end

        prev_hist = hist

    cap.release()
    if progress:
        progress.close()

    # 最后一个镜头
    if duration - scene_start >= min_scene_sec:
        scenes.append((scene_start, duration))

    print(f"  检测到 {len(scenes)} 个镜头")
    return scenes, fps, duration


# ─── 步骤2：关键帧提取 ────────────────────────────────

def extract_keyframes(video_path, scenes, fps, max_per_scene=MAX_KEYFRAMES_PER_SCENE):
    """从每个镜头中提取关键帧，保存为临时文件。返回 [{scene_idx, time, path}, ...]"""
    cap = cv2.VideoCapture(video_path)
    keyframes = []

    temp_dir = tempfile.mkdtemp(prefix="dissect_")
    print(f"  关键帧目录: {temp_dir}")

    for si, (start, end) in enumerate(scenes):
        duration = end - start
        # 均匀取 max_per_scene 帧
        mid_times = []
        if duration <= 2:
            mid_times = [(start + end) / 2]
        else:
            step = duration / (max_per_scene + 1)
            for i in range(1, max_per_scene + 1):
                mid_times.append(start + step * i)

        for ti, t in enumerate(mid_times):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
            ret, frame = cap.read()
            if not ret:
                continue

            fname = f"shot_{si+1:03d}_frame_{ti+1}.jpg"
            fpath = os.path.join(temp_dir, fname)
            cv2.imwrite(fpath, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            keyframes.append({
                "scene_idx": si,
                "time_sec": round(t, 1),
                "path": fpath,
            })

    cap.release()
    print(f"  提取 {len(keyframes)} 张关键帧")
    return keyframes, temp_dir


# ─── 步骤3：LLM视觉分析 ──────────────────────────────

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def build_analysis_prompt(scene_count, shot_num, total_shots):
    """构造8维度分析Prompt"""
    return f"""你是电商AI视频分析专家。分析这张关键帧图片，按以下8个维度输出JSON（不要其他文字）：

1. shotNumber: 镜号（当前是第{shot_num}镜/共{total_shots}镜）
2. timeRange: 时间范围（该镜头的起止秒数，格式 "Xs-Ys"）
3. shotSize: 景别（远景/全景/中全景/中景/中近景/近景/特写）
4. cameraMove: 运镜（固定/缓推/缓拉/左摇/右摇/上摇/下摇/跟随/呼吸感/无法判断）
5. characterState: 人物状态（人物在做什么、什么表情、看向哪里，详细描述）
6. clothingDetail: 服装材质（服装类型、颜色、印花/纹理、面料质感、版型细节，详细描述）
7. lighting: 灯光氛围（光源方向、主光位置、色温冷暖、光质软硬、环境氛围）
8. referenceFrame: 参考帧描述（这一帧的关键特征描述，用于后续复刻时的参考）

输出格式（严格JSON，不要markdown代码标记）：
{{"shotNumber":{shot_num},"timeRange":"","shotSize":"","cameraMove":"","characterState":"","clothingDetail":"","lighting":"","referenceFrame":""}}"""


def analyze_keyframes(keyframes, scenes, api_key, api_base, model, progress_desc="分析"):
    """逐帧调用LLM Vision API，返回结构化数据"""
    if not api_key:
        print("  ⚠️ 未设置API Key，跳过LLM分析，仅输出镜头结构")
        return None

    try:
        import urllib.request
        import urllib.error
    except ImportError:
        print("  ❌ 无法导入urllib")
        return None

    # 按scene分组
    from collections import defaultdict
    scene_frames = defaultdict(list)
    for kf in keyframes:
        scene_frames[kf["scene_idx"]].append(kf)

    results = []
    total = len(scenes)

    iterator = tqdm(scene_frames.items(), desc=progress_desc, total=len(scene_frames)) if tqdm else scene_frames.items()

    for scene_idx, frames in iterator:
        shot_num = scene_idx + 1
        start_s, end_s = scenes[scene_idx]
        time_range = f"{start_s:.1f}s-{end_s:.1f}s"

        # 取第一帧做LLM分析
        frame = frames[0]
        if not os.path.exists(frame["path"]):
            continue

        prompt = build_analysis_prompt(len(scenes), shot_num, total)

        # 构建API请求
        try:
            b64 = encode_image(frame["path"])
            payload = {
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "low"}}
                    ]
                }],
                "max_tokens": 800,
                "temperature": 0.1,
            }

            req = urllib.request.Request(
                f"{api_base}/chat/completions",
                data=json.dumps(payload).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
            )

            resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
            content = resp["choices"][0]["message"]["content"]

            # 提取JSON
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            if content.startswith("json"):
                content = content[4:].strip()

            parsed = json.loads(content)
            parsed["timeRange"] = time_range
            results.append(parsed)

        except Exception as e:
            results.append({
                "shotNumber": shot_num,
                "timeRange": time_range,
                "shotSize": "分析失败",
                "cameraMove": "分析失败",
                "characterState": f"LLM Error: {str(e)[:60]}",
                "clothingDetail": "",
                "lighting": "",
                "referenceFrame": "",
            })

        # API限速保护
        time.sleep(0.5)

    return results


# ─── 步骤4：输出 ──────────────────────────────────────

def export_json(scenes, analysis, keyframes, output_path):
    """导出为完整拆解表JSON"""
    result = {
        "videoInfo": {
            "filePath": args.video,
            "totalShots": len(scenes),
        },
        "shots": [],
    }

    for si, (start, end) in enumerate(scenes):
        shot = {
            "shotNumber": si + 1,
            "timeRange": f"{start:.1f}s-{end:.1f}s",
            "durationSec": round(end - start, 1),
        }

        # 从LLM分析结果中取数据
        if analysis and si < len(analysis):
            a = analysis[si]
            shot["shotSize"] = a.get("shotSize", "")
            shot["cameraMove"] = a.get("cameraMove", "")
            shot["characterState"] = a.get("characterState", "")
            shot["clothingDetail"] = a.get("clothingDetail", "")
            shot["lighting"] = a.get("lighting", "")
            shot["referenceFrame"] = a.get("referenceFrame", "")
        else:
            shot["shotSize"] = ""
            shot["cameraMove"] = ""
            shot["characterState"] = ""
            shot["clothingDetail"] = ""
            shot["lighting"] = ""
            shot["referenceFrame"] = ""

        # 关联关键帧路径
        shot["keyframes"] = [kf["path"] for kf in keyframes if kf["scene_idx"] == si]

        result["shots"].append(shot)

    # 写入文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 拆解表已导出: {output_path}")
    return result


# ─── 节奏模板提取 ─────────────────────────────────────

def extract_rhythm_template(analysis):
    """从分析结果中提取节奏范式"""
    if not analysis:
        return ""

    pattern = []
    for a in analysis:
        shot_size = a.get("shotSize", "")
        character = a.get("characterState", "")[:20]

        # 简化分类
        if "特写" in shot_size:
            tag = "特写"
        elif "近景" in shot_size:
            tag = "近景"
        elif "中近" in shot_size or "中景" in shot_size:
            tag = "中景"
        elif "全" in shot_size or "远" in shot_size:
            tag = "全景"
        else:
            tag = shot_size or "?"

        pattern.append(f"[{tag}] {character}")

    return " → ".join(pattern)


# ─── 主流程 ───────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI视频拆解分析管线 — 输出8维度结构化数据")
    parser.add_argument("video", help="视频文件路径")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="LLM API Key")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="LLM API地址")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="LLM模型名")
    parser.add_argument("--output", default=None, help="输出JSON路径（默认: 视频名_dissect.json）")
    parser.add_argument("--scene-only", action="store_true", help="只拆镜头，不调LLM")
    parser.add_argument("--threshold", type=float, default=SCENE_THRESHOLD, help=f"场景检测阈值（默认{SCENE_THRESHOLD}，越大越不敏感）")
    global args
    args = parser.parse_args()

    video_path = args.video
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        sys.exit(1)

    output_path = args.output or os.path.splitext(video_path)[0] + "_dissect.json"

    print(f"\n🎬 AI视频拆解分析")
    print(f"{'='*50}")
    print(f"  视频: {video_path}")

    # Step 1: 镜头检测
    print(f"\n📹 步骤1/3：镜头检测")
    scenes, fps, duration = detect_scenes(video_path, args.threshold)

    # Step 2: 关键帧提取
    print(f"\n🖼️  步骤2/3：关键帧提取")
    keyframes, temp_dir = extract_keyframes(video_path, scenes, fps)

    # Step 3: LLM分析
    analysis = None
    if not args.scene_only:
        print(f"\n🤖 步骤3/3：LLM视觉分析")
        analysis = analyze_keyframes(keyframes, scenes, args.api_key, args.api_base, args.model)

    # 输出
    result = export_json(scenes, analysis, keyframes, output_path)

    # 节奏模板
    if analysis:
        rhythm = extract_rhythm_template(analysis)
        print(f"\n📋 节奏模板: {rhythm}")

    print(f"\n{'='*50}")
    print(f"✅ 完成！ 共 {len(scenes)} 个镜头")
    if analysis:
        print(f"  其中 {len(analysis)} 个完成AI分析")
    print(f"  输出: {output_path}")
    print(f"  关键帧: {temp_dir}")
    print()


if __name__ == "__main__":
    main()
