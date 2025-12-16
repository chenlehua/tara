# TARA System AI 模型配置

本目录包含 AI 模型配置、提示词模板和微调脚本。

## 目录结构

```
ai-models/
├── configs/                # 模型配置
│   ├── vllm_config.yaml    # vLLM 服务配置
│   ├── qwen3_config.yaml   # Qwen3 模型配置
│   └── embedding_config.yaml # 嵌入模型配置
├── prompts/                # 提示词模板
│   ├── document_analysis.py    # 文档分析提示词
│   ├── asset_discovery.py      # 资产发现提示词
│   ├── threat_analysis.py      # 威胁分析提示词
│   └── report_generation.py    # 报告生成提示词
└── fine-tuning/            # 微调脚本
    ├── prepare_data.py     # 数据准备
    ├── train.py            # 训练脚本
    └── evaluate.py         # 评估脚本
```

## 模型说明

### 1. Qwen3 (文本生成)
- 用途：威胁分析、报告撰写、对话
- 模型：Qwen/Qwen2.5-7B-Instruct
- 部署：vLLM 推理服务

### 2. Qwen3-VL (多模态)
- 用途：文档解析、图表理解
- 模型：Qwen/Qwen2-VL-7B-Instruct
- 部署：vLLM 推理服务

### 3. Embedding Model (向量嵌入)
- 用途：语义搜索、相似度匹配
- 模型：Qwen/Qwen2.5-Embedding-0.6B
- 部署：独立推理服务

### 4. OCRFlux (OCR识别)
- 用途：扫描文档文字识别
- 部署：独立 OCR 服务

## 配置说明

### vLLM 配置
```yaml
model: Qwen/Qwen2.5-7B-Instruct
tensor_parallel_size: 1
max_model_len: 8192
gpu_memory_utilization: 0.9
```

## 微调指南

如需针对特定领域微调模型：

1. 准备训练数据
```bash
python fine-tuning/prepare_data.py --input data/training.jsonl
```

2. 开始训练
```bash
python fine-tuning/train.py --config configs/finetune_config.yaml
```

3. 评估模型
```bash
python fine-tuning/evaluate.py --model output/checkpoint
```
