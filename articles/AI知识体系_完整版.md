# AI 知识体系 · 2026 完整版

> 版本：v2.0 | 更新：2026-06-29 | 类型：全量知识体系

---

## 一、产业全景总览

AI产业由四层构成：基础层（40%价值占比）→ 技术层（30%）→ 中间层（10%）→ 应用层（20%）。底层为上层提供能力，每层独立成产业。

---

## 二、基础层：算力与数据底座

### 2.1 AI芯片

#### 通用GPU（训练/推理主力）
- **英伟达 NVIDIA**：H100（训练主力）、B200（新一代）、GB200（Grace Hopper超级芯片）、A100（上一代主力）— 训练市场份额约77%
- **AMD**：MI300X（性价比路线）、MI250
- **Intel**：Gaudi 3（数据中心推理场景）
- **海风部署**：RTX 5090D（24GB显存，本地推理主力）

#### 国产替代GPU
- **华为**：昇腾910B（训练级）、昇腾310P（推理级）、昇腾系列完整解决方案
- **寒武纪**：MLU370、MLU290
- **海光信息**：DCU（深算系列）
- **壁仞科技**：BR100
- **天数智芯**：天垓100
- **摩尔线程**：MTT S系列
- **燧原科技**：云燧系列

#### 端侧/边缘AI芯片
- **高通**：骁龙8 Elite（NPU）
- **苹果**：M4 / M3（Neural Engine）
- **联发科**：天玑9400（APU）
- **瑞芯微**：RK3588
- **地平线**：征程6（自动驾驶/车载）
- **华为**：麒麟NPU
- **Google**：Tensor G系列（Pixel手机）
- **三星**：Exynos NPU

#### 专用ASIC（互联网自研）
- **Google**：TPU v5 / v5p
- **Amazon**：Trainium2（训练）、Inferentia（推理）
- **阿里**：含光800
- **百度**：昆仑芯2 / 3
- **微软**：Maia 100
- **特斯拉**：Dojo D1（自动驾驶训练）
- **Meta**：MTIA系列

### 2.2 AI服务器

- **浪潮信息**：NF5688M6（营收同比+90%）
- **工业富联**（营收同比+60%）
- **超微电脑 Supermicro**：液冷方案领先
- **戴尔 Dell**：PowerEdge系列
- **联想 Lenovo**：ThinkSystem SR系列
- **华为**：Atlas系列
- **新华三 H3C**：UniServer R系列

### 2.3 智算中心/数据中心

- **阿里云**：灵骏智算集群
- **腾讯云**：星脉智算
- **华为云**：昇腾AI集群
- **火山引擎**：GPU集群
- **百度**：百舸AI平台
- **商汤**：AIDC（亚洲最大智算中心之一）
- **润泽科技**、**万国数据**、**世纪互联**（第三方IDC）

### 2.4 云服务三层

#### IaaS（基础设施即服务）
- 阿里云 ECS / GPU实例
- 腾讯云 CVM / GPU云服务器
- 华为云 ECS / GPU加速型
- AWS EC2 / GPU实例
- Azure VM / GPU系列
- Google Cloud Compute Engine / GPU

#### PaaS/MaaS（模型即服务）
- **阿里云**：百炼大模型平台
- **腾讯云**：TokenHub
- **火山引擎**：火山方舟
- **百度云**：千帆大模型平台
- **华为云**：ModelArts
- **AWS**：Bedrock
- **Azure**：Azure OpenAI Service
- **Google**：Vertex AI

#### SaaS（应用即服务）
- **钉钉**AI助手
- **飞书**智能伙伴
- **企业微信**AI
- **腾讯**元宝
- **百度**如流
- **Notion** AI
- **微软**Copilot / M365 Copilot
- **Google** Workspace AI

### 2.5 数据基础设施全链路

- **数据采集**：爬虫框架（Scrapy/Selenium）、API网关、IoT传感器、日志采集（Fluentd/Logstash）
- **数据标注**：Scale AI、龙猫数据、标注基地、Label Studio（开源）
- **数据合成**：Stable Diffusion生成、LLM生成、仿真环境（Unity/Unreal）
- **数据清洗**：Apache Spark、Flink、Pandas、Dask
- **数据治理**：数据湖（Delta Lake/Iceberg/Hudi）、数据仓库（Snowflake/Redshift/ClickHouse）
- **ETL**：Airflow、dbt、Fivetran
- **向量存储**：FAISS（Meta）、Milvus（Zilliz）、Chroma（轻量）、Qdrant、Pinecone（托管）、Weaviate、PGVector（PostgreSQL扩展）

### 2.6 网络互联

- **InfiniBand**：NDR 400Gb/s（英伟达/Mellanox），HPC/AI集群事实标准
- **RoCE v2**：以太网RDMA方案（成本更低，生态兼容）
- **NVLink / NVSwitch**：英伟达GPU间直连互联
- **CPO / 硅光互连**：下一代数据中心互联方案
- **光模块**：400G / 800G 主流部署

---

## 三、技术层：智能引擎

### 3.1 大语言模型

#### 通用闭源模型
- **OpenAI**：GPT-4o（综合最强）、GPT-4.5（改进版）、GPT-4 Turbo、o1/o3（推理系列）
- **Anthropic**：Claude Opus 4（最聪明）、Claude Sonnet 4（速度与质量平衡）、Claude 3.5 Haiku（轻量）
- **Google**：Gemini 2.0 Pro（原生多模态）、Gemini 2.0 Flash（轻量）
- **月之暗面**：Kimi k2.5（200万字超长上下文）、Kimi K1.5（长思考）
- **字节跳动**：豆包2.1 Pro（256K上下文，国内MaaS Token份额49.5%）、豆包2.1 Turbo（半价，更快）
- **阿里**：Qwen-Max
- **腾讯**：混元大模型
- **百度**：文心4.0 / 文心4.5
- **智谱AI**：GLM-4.5
- **零一万物**：Yi-Large

#### 开源模型
- **Meta**：Llama 4（社区最活跃，生态最丰富）
- **阿里**：Qwen2.5-72B / Qwen2.5-110B（中文最强开源）
- **深度求索**：DeepSeek-V3（性价比极高，API价格远低于GPT）
- **Mistral AI（法国）**：Mistral Large 2、Mixtral 8x22B
- **智谱AI**：GLM-4-9B Chat
- **微软**：Phi-4（小型高精度）
- **Google**：Gemma 2

#### 推理/长思考模型（擅长复杂推理）
- **DeepSeek-R1**（开源推理模型标杆）
- **OpenAI**：o3-mini（快速推理）、o1-preview / o1-mini
- **Anthropic**：Claude 3.7 Sonnet Thinking
- **月之暗面**：Kimi K1.5（长思考）
- **阶跃星辰**：Step R-mini
- **Google**：Gemini 2.0 Flash Thinking

#### 行业垂类模型
- **华为**：盘古大模型（工业/气象/矿山/药物分子）
- **阿里**：通义行业版（医疗/法律/金融）
- **百度**：灵医大模型（医疗）
- **科大讯飞**：星火大模型（教育/医疗）
- **蚂蚁集团**：AntFin大模型（金融）
- **度小满**：轩辕大模型（金融）
- **腾讯**：混元广告/游戏版

#### 端侧小模型（可在手机/本地运行）
- **微软**：Phi-4（3.8B参数）
- **Meta**：Llama 3.2 1B / 3B
- **阿里**：Qwen2.5-3B / 7B
- **深度求索**：DeepSeek-R1-Distill 1.5B / 7B
- **Google**：Gemma 2 2B / 9B
- **苹果**：OpenELM
- **HuggingFace**：SmolLM 135M / 360M / 1.7B

### 3.2 多模态模型

- **OpenAI**：GPT-4o（原生多模态：文本+视觉+语音）
- **Google**：Gemini 2.0（原生多模态：文本+视觉+音频+视频）
- **Anthropic**：Claude 3.7（图文理解）
- **阿里**：Qwen-VL-Max（视觉语言模型）
- **零一万物**：Yi-VL
- **商汤**：InternVL / InternLM-XComposer

### 3.3 Agent框架

#### 编排框架
- **LangGraph**（LangChain）：最主流的Agent编排框架，图结构多Agent协作，支持状态持久化、断点续跑
- **CrewAI**：多Agent协作，像组团队一样配置Agent（角色+任务+工具）
- **AutoGen**（微软）：多Agent对话框架，灵活组合
- **OpenAI Agents SDK**：官方Agent开发套件
- **Dify**（开源）：可视化拖拽搭建AI应用，适合非技术用户
- **Coze / 扣子**（字节）：Agent搭建平台
- **HiAgent 3.0**（火山引擎）：企业级Agent工作站，1+N+X架构，300+零代码连接器，支持万级Agent集群
- **百度 AppBuilder**：百度Agent搭建平台

#### 垂直Agent
- **MetaGPT**：软件开发多Agent
- **Devin**：全栈工程师Agent
- **SWE-Agent**：代码修复Agent
- **OpenHands**：通用编码Agent
- **HuggingFace smolagents**：轻量Agent

### 3.4 Agent通信协议

- **MCP Model Context Protocol**（Anthropic）：当前事实标准，让模型安全地调用外部工具和访问数据
- **A2A Agent-to-Agent**（Google）：Agent之间的通信协议
- **Function Calling**（OpenAI）：原生函数调用
- **Tool Use**（通用）：工具调用标准接口

### 3.5 计算机视觉

#### 检测/分割
- YOLOv8 / v9 / v10（Ultralytics：实时目标检测）
- SAM 2（Meta：通用分割）
- RT-DETR（百度：实时检测Transformer）
- DETR（Meta：端到端检测）

#### 识别/理解
- CLIP（OpenAI：图文对齐）
- BLIP-2（Salesforce：图像描述）
- DINO v2（Meta：自监督视觉特征）

#### 生成
- Stable Diffusion 3 / SDXL（Stability AI）
- ControlNet（可控生成）
- Midjourney（闭源，效果领先）
- DALL-E 3（OpenAI）

### 3.6 语音技术

#### 语音识别 ASR
- Whisper（OpenAI：多语言开源）
- FunASR（阿里：中文最优）
- 科大讯飞（中文商业最优）
- 百度语音
- Google Cloud Speech

#### 语音合成 TTS
- **CosyVoice**（阿里：海风选型 ✓）
- **F5-TTS**（海风备选）
- 豆包语音（字节）
- DiaMoE-TTS
- FishSpeech
- GPT-SoVITS（海风排除）
- ElevenLabs（英语最优）

#### 声音克隆
- CosyVoice SFT 微调
- F5-TTS zero-shot
- OpenVoice（开源）
- 讯飞声音复刻

### 3.7 视频生成

#### 图生视频
- **可灵AI 1.6**（快手：国内领先）
- **CogVideoX-5B**（智谱：海风备选）
- **海螺AI**（MiniMax）
- **PixVerse**（爱诗科技）
- **Wan 2.1 14B**（阿里：海风选型 ✓）
- Runway Gen-3 / Gen-3 Alpha
- Pika 2.0

#### 文生视频
- **Seedance 2.5**（字节跳动：⭐ 最大亮点—原生30秒连贯视频/50份参考素材并行/无损局部编辑/3D白模预演/4K输出）
- Sora（OpenAI：首个文生视频）
- Veo 3（Google）
- 可灵AI（文生视频）
- 通义万相视频（阿里）
- Luma Dream Machine

### 3.8 数字人/虚拟人

- **HeyGen**（口型同步领先，海风关注）
- D-ID（面部驱动）
- SiliconFlow
- Sadtalker（开源）
- EMO（阿里）
- 硅基智能
- 小冰

### 3.9 代码生成工具

- **Cursor**（AI IDE，海风可用）
- **Claude Code**（Anthropic终端编码）
- GitHub Copilot（微软）
- Windsurf
- Trae（字节）
- 通义灵码（阿里）
- Codeium

### 3.10 NLP技术栈

- **BERT / RoBERTa**：文本理解基准
- **T5 / BART**：翻译/摘要
- **GPT系列**：文本生成
- **长文本技术**：Kimi 200万字 / Claude 200K / Gemini 1M / GPT-4 128K
- **子任务**：情感分析、命名实体识别NER、关系抽取RE、文本分类

---

## 四、中间层：协议与工具链

### 4.1 LLMOps

#### 监控/评估平台
- **LangSmith**（LangChain）：全链路追踪，Prompt版本管理，效果评估
- **Langfuse**（开源）：追踪+评估+成本管理
- **Arize Phoenix**（开源）：AI可观测性
- **Weights & Biases**：实验追踪
- **LightField**：基于longfuse开源构建，cdb存储超长文本，存算分离省65-88%
- **Helicone**：API调用监控
- **PromptLayer**：Prompt日志

#### Prompt管理
- LangChain Hub（Prompt共享）
- PromptLayer（版本管理/A/B测试）
- 自定义Prompt模板系统

### 4.2 RAG框架（检索增强生成）

- **LangChain**（Python/JS双版，生态最全）
- **LlamaIndex**（数据索引框架，擅长多数据源）
- **Dify内置RAG**（可视化配置）
- **RAGFlow**（深度求索）
- **EmbedChain**（轻量RAG）
- **Quivr**（个人知识库）
- **Haystack**（deepset）

### 4.3 工作流编排

- **n8n**（开源自动化工作流，海风可用 ✓）
- **Make**（Zapier竞品，可视化编排）
- **Dify**（AI工作流引擎）
- **Coze / 扣子**（字节工作流）
- **Flowise**（可视化LangChain）
- **Zapier**（通用自动化老牌）
- **HuggingFace Spaces**（AI Demo部署）

### 4.4 向量数据库

- **Milvus**（Zilliz开源，专业级分布式）
- **Pinecone**（全托管云服务）
- **Chroma**（轻量级嵌入式）
- **Weaviate**（带GraphQL接口）
- **Qdrant**（Rust编写，高性能）
- **PGVector**（PostgreSQL扩展）
- **Elasticsearch**（传统搜索增强）

### 4.5 模型训练与微调工具链

#### 训练框架
- **PyTorch**（Meta，AI训练事实标准）
- **TensorFlow / JAX**（Google）
- **DeepSpeed**（微软，大规模并行训练）
- **FSDP**（PyTorch Fully Sharded Data Parallel）
- **ColossalAI**（潞晨科技）

#### 微调框架
- **LoRA / QLoRA**（低秩适配微调）
- **kohya_ss**（SD LoRA训练）
- **LLaMA-Factory**（一站式微调，支持LoRA/全参）
- **Unsloth**（微调加速2x）
- **Axolotl**（开源微调工具）

#### 推理框架
- **vLLM**（PagedAttention推理加速）
- **TensorRT-LLM**（英伟达，最佳推理优化）
- **llama.cpp**（本地CPU/GPU推理）
- **Ollama**（一键本地模型部署）
- **MLC LLM**（端侧推理）
- **TGI**（HuggingFace Text Generation Inference）
- **SGLang**（结构化生成语言）

#### 模型评估/对齐
- 基准测试：HumanEval（代码）、MMLU（知识）、TruthfulQA（诚实）、GSM8K（数学）、Arena ELO（对战）
- 对齐技术：RLHF（人工反馈强化学习）、DPO（直接偏好优化）、PPO（近端策略优化）、Constitutional AI（宪法AI）

---

## 五、应用层：垂直场景出口

### 5.1 制造业AI
- 智能排产 APS、视觉质检 AOI、预测性维护 PHM、供应链优化、数字孪生
- 工业机器人 / 协作机器人
- **代表**：华为盘古工业、奇智孔明、百度飞桨工业

### 5.2 电商零售AI
- **运营**：智能客服（售前/售后/工单）、个性化推荐引擎、动态定价、AIGC商品主图、AIGC产品视频、智能广告投放（千川/磁力）
- **直播**：数字人主播 / 无人直播、AI话术生成、实时弹幕智能回复、直播数据分析、赛马机制优化

### 5.3 金融科技AI
- 智能风控 / 反欺诈、投研分析 / 财报解读、智能投顾、量化交易、智能合规
- **代表**：蚂蚁金融大模型、妙想金融、度小满轩辕

### 5.4 医疗健康AI
- 医学影像诊断（CT/X光/病理）、辅助诊疗、药物研发（AlphaFold3）、健康管理、手术导航
- **代表**：百度灵医、讯飞晓医、医联MedGPT

### 5.5 教育AI
- 个性化学习路径、AI助教/答疑、作业批改/作文评分、语言学习/口语评测、虚拟教师/数字人讲师
- **代表**：MathGPT、子曰（网易有道）、作业帮

### 5.6 法律AI
- 合同审查、案例检索/类案推荐、合规检查、法律文书生成、法律问答
- **代表**：ChatLaw、得理法搜

### 5.7 自动驾驶
- 端到端大模型（特斯拉FSD）、BEV感知、Occupancy Network、高精地图/众包地图、仿真测试
- **代表**：百度Apollo、华为ADS、小鹏XNGP、蔚来NAD

### 5.8 游戏/娱乐AI
- NPC智能（行为/对话）、剧情生成、美术资产生成、反作弊
- **代表**：网易伏羲、腾讯AI Lab、米哈游

### 5.9 内容创作AI
- AI写作/文案（营销/新闻/小说）、AI绘画/海报、AI视频/剪辑、AI音乐/音效、AI播客
- **代表**：Canva AI、剪映AI、Jasper、Copy.ai

### 5.10 通用提效AI
- 日常问答：ChatGPT、Claude、Kimi、豆包、元宝
- 编程：Cursor、Claude Code、GitHub Copilot
- 办公：钉钉AI、飞书智能伙伴、Microsoft Copilot
- 知识管理：Notion AI、Obsidian AI

---

## 六、2026年五大产业趋势

| # | 趋势 | 核心变化 | 内涵 |
|---|------|---------|------|
| 1 | Agent替代Chatbot | AI从"回答"到"执行" | 企业开始用Agent处理完整业务闭环，不再只是问答 |
| 2 | 推理算力爆发 | 推理占算力70-80%，成本两年降95% | 推理优化、vLLM等框架使推理效率大幅提升 |
| 3 | 开源生态成熟 | 开源模型逼近闭源水平 | Llama/Qwen/DeepSeek使中小企业也能用上顶级能力 |
| 4 | 多模态标配化 | 文/图/音/视频统一生成 | GPT-4o/Gemini原生多模态，一个模型搞定所有内容形式 |
| 5 | Agent商用元年 | 88%部署企业获正ROI | 制造/电商/金融头部企业已跑通Agent投资回报 |

---

## 七、术语与概念

| 术语 | 解释 |
|------|------|
| GPU | 图形处理器，并行计算能力强，AI训练和推理的核心硬件 |
| Token | LLM处理文本的最小单位，中文约1-2字/Token |
| LLM | 大语言模型，基于海量文本训练的语言理解和生成模型 |
| 多模态 | 能同时处理文字/图片/音频/视频中多种形式的AI |
| RAG | 检索增强生成，让模型先查知识库再回答，减少幻觉 |
| Agent | 能自主规划任务、调用工具、执行并验证的智能体 |
| Prompt | 用户给AI的指令/提示词，质量直接影响输出效果 |
| Embedding | 将文字/图像转为向量，用于语义检索和相似度匹配 |
| Fine-tune | 在预训练模型上用特定数据微调，使其适配特定业务 |
| LoRA | 低秩适配，一种低成本微调方法，只需训练少量参数 |
| 幻觉 Hallucination | 模型生成看似合理但事实上错误的内容 |
| MCP | Model Context Protocol，Anthropic提出的模型-工具通信标准 |
| FP8/FP16/FP32 | 浮点数精度格式，越低精度推理速度越快、显存占用越少 |
| A100/H100/B200 | 英伟达GPU代际：A100→H100→B200，性能逐代翻倍 |

---

## 八、行业关键数据

- 英伟达训练市场份额：约77%
- 国内MaaS Token市场份额：火山引擎49.5%（豆包）
- 字节TRAE团队代码AI生成率：超90%
- 人均需求吞吐率提升：约60%（AI写代码后）
- 企业部署Agent获正ROI比例：88%
- 推理算力成本两年降幅：约95%
- 豆包大模型日均调用量：180万亿Token（同比增10倍+）
- 安踏虚拟试衣退货率降幅：从30-40%降至15-20%
- 海底捞门店Agent人工跟进时长减少：70%
- 赛力斯HMI设计研发周期压缩：从"天"到"分钟"

---

*制图：Kiwi-KK 🥝 | 2026-06-29*
