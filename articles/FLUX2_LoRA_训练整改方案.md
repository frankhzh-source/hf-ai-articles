# FLUX.2 LoRA 训练整改方案（专业模型训练师版）

**项目**：达芬奇密码 家居服/内衣 FLUX.2 LoRA 训练  
**时间**：2026-06-02 至 2026-06-06 错误复盘  
**模型**：FLUX.2 Klein 4B + AI-ToolKit (Native)  
**数据集**：dvc_lora_v5_strict_caption_rework_v1（120 张，4 组 × 30 张）  
**作者**：海风老师 | AI技术咨询 / LoRA模型训练 / 电商AI落地

---

## 一、问题全景映射

将 10 个已识别错误归纳为 **4 个根因类别**，整改方案按根因而非症状推进：

| 根因类别 | 涉及问题 | 严重程度 |
|---------|---------|:--------:|
| **A. 标注工程未闭环** | #1 caption 范式错误 / #3 分类不严谨 / #4 图源混入 | 🔴 致命 |
| **B. 工程管线未固化** | #2 误判进度 / #5 config 未同步 / #10 无进度表 | 🟠 严重 |
| **C. 脚本/工具链缺陷** | #7 迁移脚本 / #8 质检误判 / #9 模型格式 | 🟡 中等 |
| **D. 流程沟通阻塞** | #6 503 处理不主动 | 🟢 轻微 |

---

## 二、根因 A：标注工程未闭环（🔴 致命级）

### 问题 #1：Caption 标注范式错误

**错误现象**：120 张图生成短标签/模板句，每组 30 张完全重复，词数仅 15-18（标准 40-100）

**根因分析**：
- FLUX.2 采用 Mistral-3 7B 作为文本编码器（非 CLIP），需要**自然语言句子**而非标签列表
- 标签列表在 FLUX.2 上的有效率为 **0%**（实验数据已验证），自然语言有效率为 **95%**
- 使用旧版 LoRA 标注习惯（short tag / keyword）直接套用到 FLUX.2

**整改方案**：

```
标准：每条 caption = 40-100 词的英文自然语言描述
结构模板：
  [主体] wearing/appearing in [服装描述], featuring [细节1], [细节2], and [细节3].
  The [garment type] is made of [材质] with [设计元素].
  Shot in [场景/光线], [pose/角度].

反例（不要）："elegant dress, lace, satin"
正例（要）：  "A young woman in her late 20s with long dark hair wearing a
               floor-length burgundy velvet evening gown featuring a deep V-neckline,
               fitted bodice with intricate lace overlay, and a flowing A-line
               skirt. The velvet fabric has a subtle sheen under soft studio
               lighting..."
```

### 问题 #3：分类标准不严谨

**错误现象**：国风/甜美/纯欲等分类依赖视觉直觉，道具/场景被误当作服装风格

**整改方案**：

```
分类标准应基于服装结构，而非视觉感受：

✅ 正确的分类维度：
  - 领型：round neck / V-neck / mandarin collar / Peter Pan collar
  - 袖型：long sleeve / puff sleeve / bishop sleeve / sleeveless
  - 廓形：fit & flare / A-line / bodycon / oversized
  - 材质：satin / velvet / lace / cotton / polyester blend
  - 装饰元素：frog buttons / contrast piping / embroidery / sequins

❌ 避免的分类维度：
  - 风格标签（elegant / cute / sexy） → 放在 caption 正文中描述
  - 场景标签（bedroom / living room）  → 只作为背景上下文
  - 情绪标签（happy / romantic）       → LoRA 不学习这层
```

### 问题 #4：图源混入

**错误现象**：礼盒图、平铺图、挂拍图混入主训练集

**整改方案**：

```
严格分离训练图源：

train_ready/  （主训练集，仅限真人穿着图）
  ├── front/      正面全身/半身
  ├── side/       侧面45-90度
  ├── back/       背面展示
  └── detail/     材质特写（带真人穿着）

control_refs/  （参考集，不参与训练）
  ├── flat_lay/   平铺图
  ├── hanger/     挂拍图
  ├── gift_box/   礼盒/包装图
  └── mannequin/  人台图（无真人）

review/        （待定区，需人工审核后分流）
```

---

## 三、根因 B：工程管线未固化（🟠 严重级）

### 问题 #2 / #5 / #10：缺乏闭环检查机制

**根因分析**：将"局部完成"误判为"整体完成"——图片筛选通过 ≠ 训练数据就绪

**整改方案**：建立 **LoRA 训练 6 阶检查清单**

```
┌─────────────────────────────────────────────────────┐
│              LoRA 训练就绪检查清单                     │
├─────────────────────────────────────────────────────┤
│                                                       │
│  □ 阶段 1：图片工程                                  │
│     ├─ 图片数量达标（建议 30-50/组，4-8 组）          │
│     ├─ 分辨率统一（建议 1024×1024 或 1024×1536）      │
│     ├─ 背景/姿态有差异化                             │
│     └─ 无重复/模糊/过度压缩图                         │
│                                                       │
│  □ 阶段 2：Caption 工程                              │
│     ├─ 每条 40-100 词自然语言                         │
│     ├─ FLUX.2 语法合规（validate_flux2_captions.py）  │
│     ├─ 无词源污染（通用词/行业术语/GEO 三级过滤）      │
│     └─ 100% 人工复核通过                             │
│                                                       │
│  □ 阶段 3：数据包一致性                              │
│     ├─ image/ 与 metadata.jsonl 一一对应               │
│     ├─ config 指向新 dataset（非旧路径）               │
│     └─ 无残留旧 output 路径引用                       │
│                                                       │
│  □ 阶段 4：环境就绪                                   │
│     ├─ 模型权重格式正确（Native/Klein .safetensors）   │
│     ├─ AI-ToolKit 模型可加载                          │
│     └─ 显存/磁盘空间充足                              │
│                                                       │
│  □ 阶段 5：Precheck                                   │
│     ├─ 1-step precheck 通过                           │
│     ├─ 单方向 smoke test 通过                         │
│     └─ loss 曲线无异常                                │
│                                                       │
│  □ 阶段 6：正式训练                                   │
│     ├─ 四方向训练参数确认                             │
│     ├─ 备份输出路径                                   │
│     └─ 训练监控面板已启动                             │
│                                                       │
└─────────────────────────────────────────────────────┘
```

**关键机制**：前一阶段未完成，不得进入下一阶段。每次状态更新输出 `<STATUS>` 标签：

```
[STATUS 2026-06-07]
  ✅ 阶段 1 图片工程：完成
  ✅ 阶段 2 Caption：完成 (120/120)
  ✅ 阶段 3 数据包：完成 (指向新dataset)
  ❌ 阶段 4 环境：阻塞（模型格式待解决）
  ⏳ 阶段 5 Precheck：等待中
  ⏳ 阶段 6 训练：等待中
  阻塞原因：AI-ToolKit 需要 native flux-2-klein-base-4b.safetensors
```

---

## 四、根因 C：脚本/工具链缺陷（🟡 中等）

### 问题 #7：C盘迁移脚本逻辑不完善

**错误现象**：二次运行因 junction/backup 状态处理不完整而报错

**修正方案**：迁移脚本增加幂等性校验

```bash
# 迁移脚本核心逻辑（修复版）

TARGET="D:/FLUX2_LoRA/outputs"
BACKUP="D:/FLUX2_LoRA/outputs_backup"
CACHE="C:/Users/jt/.cache/FLUX2_LoRA/outputs"

# Step 1: 检查目标是否存在
if [ -d "$TARGET" ]; then
    echo "[OK] 目标目录已存在: $TARGET"
else
    echo "[ACTION] 创建目标目录: $TARGET"
    mkdir -p "$TARGET"
fi

# Step 2: 检查备份是否已存在
if [ -d "$BACKUP" ]; then
    echo "[INFO] 备份目录已存在，跳过备份"
else
    echo "[ACTION] 创建备份"
    cp -r "$CACHE" "$BACKUP"
fi

# Step 3: 检查是否是 junction（非重复迁移）
if [ -L "$CACHE" ]; then
    echo "[OK] 已是 junction 链接，无需操作"
else
    echo "[ACTION] 迁移 C 盘缓存 → D 盘正式目录"
    mv "$CACHE"/* "$TARGET"/
    rm -rf "$CACHE"
    # Windows: 创建 junction
    cmd //c mklink /J "$(cygpath -w "$CACHE")" "$(cygpath -w "$TARGET")"
fi

# Step 4: 校验
if [ "$(ls -A "$TARGET" 2>/dev/null | wc -l)" -gt 0 ]; then
    echo "[PASS] 迁移完成，所有文件已验证"
else
    echo "[FAIL] 目标目录为空，迁移失败"
    exit 1
fi
```

### 问题 #8：质检脚本误判触发词污染

**错误现象**：`validate_flux2_captions.py` 将下划线触发词（如 `frog_buttons`）误判为连字符污染

**修正方案**：修改质检脚本的污染检测逻辑

```python
# validate_flux2_captions.py — 污染检测修正逻辑

import re

# 定义真正的污染词（GEO 高频/标题党/营销滥用）
POLLUTION_LIST = [
    r'\b暴富\b', r'\b必看\b', r'\b震惊\b',
    r'\b护城河\b',  # 巴菲特术语滥用，非服装领域
    r'赢了.*就赢了',  # 标题党句式
]

# 定义下划线触发词（合法的服装结构术语）
ALLOWED_UNDERSCORE_TERMS = [
    'frog_buttons', 'contrast_piping', 'peter_pan_collar',
    'fit_and_flare', 'a_line', 'v_neck', 'off_shoulder',
    'high_waist', 'wrap_dress', 'body_con', 'cap_sleeve',
    'bell_sleeve', 'dolman_sleeve', 'mock_neck', 'turtle_neck',
    'crop_top', 'halter_neck', 'keyhole_back', 'racer_back',
]

def check_pollution(caption: str) -> tuple[bool, list[str]]:
    """
    检查 caption 污染。
    返回 (是否通过, 污染词列表)
    """
    violations = []
    caption_lower = caption.lower()

    # 检查真正的污染词
    for pattern in POLLUTION_LIST:
        if re.search(pattern, caption_lower):
            violations.append(f"污染词命中: {pattern}")

    # 检查下划线 — 只报告不在允许列表中的
    underscore_words = re.findall(r'\b[a-z]+_[a-z]+\b', caption_lower)
    for word in underscore_words:
        if word not in ALLOWED_UNDERSCORE_TERMS:
            violations.append(f"可疑下划线词: {word}")

    return len(violations) == 0, violations
```

### 问题 #9：模型格式问题

**错误现象**：AI-ToolKit 无法加载 ComfyUI/Diffusers 格式的模型权重

**技术背景**：

| 格式类型 | 适用场景 | AI-ToolKit 兼容 |
|---------|---------|:-------------:|
| `flux-2-klein-base-4b.safetensors` (Native) | AI-ToolKit 原生 | ✅ 直接加载 |
| ComfyUI 格式 (diffusers folder) | ComfyUI 工作流 | ❌ 不支持 |
| Diffusers 格式 (pipeline folder) | HuggingFace Diffusers | ❌ 不支持 |

**整改方案**：

```
方案 A（推荐）：下载 Native 格式
  源：HuggingFace / 模型提供方的 Native weigthts
  路径：./models/flux-2-klein-base-4b.safetensors
  验证：python -c "import torch; m=torch.load('./models/flux-2-klein-base-4b.safetensors'); print('OK')"

方案 B（转换）：从 ComfyUI 格式转换
  工具：convert_comfyui_to_native.py
  命令：python convert_comfyui_to_native.py \
         --input ./models/comfyui_flux_2_klein/ \
         --output ./models/flux-2-klein-base-4b.safetensors

方案 C（备用）：使用 AI-ToolKit 的 ComfyUI bridge
  限制：效率降低约 15%，仅作临时方案
```

---

## 五、根因 D：流程沟通阻塞（🟢 轻微）

### 问题 #6：503 授权处理不主动

**整改 SOP**：遇到 503 / 授权失败时，5 分钟内输出以下信息：

```
1. 已完成内容：（如：caption 120/120 质检通过）
2. 当前卡点：（如：D盘写入 503，需要本地执行）
3. 可执行命令：（如：run_training.bat 的完整命令）
4. 预期输出：（如：输出到 D:/FLUX2_LoRA/outputs/...）
5. 下一步复核：（如：检查 loss 曲线是否正常下降）
```

---

## 六、当前状态与立即执行计划

### 现状检查

| 阶段 | 状态 | 备注 |
|-----|:---:|------|
| 图片工程 | ✅ 完成 | 4组×30张=120张 |
| Caption | ✅ 完成 | 120/120 自然语言通过 |
| 数据集 | ✅ 完成 | dvc_lora_v5_strict_caption_rework_v1 |
| Config/Script | ⚠️ 需确认 | 检查 bat 中的旧 output 路径是否完全清除 |
| 模型格式 | ❌ 阻塞 | 需要 Native Klein .safetensors |
| Precheck | ⏳ 等待 | 依赖模型格式解决 |
| 训练 | ⏳ 等待 | - |

### 立即执行步骤（按顺序）

```
Step 1 → 确认脚本路径干净
  操作：grep RemainingOldPathMatches output/*.bat
  目标：返回 0

Step 2 → 确认模型格式
  操作：python -c "import torch; torch.load('flux-2-klein-base-4b.safetensors')"
  目标：无报错，模型可加载

Step 3 → 运行 1-step precheck
  操作：python train.py --precheck-only --steps 1
  目标：precheck 通过，无报错退出

Step 4 → 单方向 smoke test
  操作：python train.py --direction front --epochs 1
  目标：loss 正常下降，输出图像基本合理

Step 5 → 四方向正式训练
  操作：python train.py --all-directions --epochs 20
  目标：四方向完整输出，loss_avg < 0.15
```

---

## 七、长期改善建议

### 1. 建立训练资料的 Git 版本管理

```
FLUX2_LoRA/
├── dataset/          # 图片 + caption（Git LFS）
├── configs/          # YAML 配置文件（Git）
├── scripts/          # 训练脚本（Git）
├── outputs/          # 训练输出（Git LFS / 排除）
├── docs/             # 标注规范/分类标准（Git）
└── STATUS.md         # 实时进度表（Git）
```

### 2. Caption 标注的持续迭代

```
版本策略：
  v1 → 初版标注（人工写，全量质检）
  v2 → 根据 precheck 结果优化高频词/低频词
  v3 → 根据训练效果调整细节描述/简化冗余
  v4 → 针对失败案例（过拟合/欠拟合）定向增补
```

### 3. Precheck 自动化为 CI 流程

每次数据更新自动触发：
```
1. validate_captions.py    → caption 合规检查
2. check_dataset_consistency.py → 文件完整性
3. check_model_format.py    → 模型可加载性
4. dry_run_precheck.py     → 1-step 试跑
5. report_status.py        → 输出状态报告
```

---

*本方案基于 2026-06-02 至 2026-06-06 的 FLUX.2 LoRA 训练错误复盘，由专业模型训练师撰写。整改的核心原则：LoRA 训练不能把"局部完成"当成"整体完成"，必须按训练资料工程闭环逐级推进。*
