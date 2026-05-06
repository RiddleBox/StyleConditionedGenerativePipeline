# StyleConditionedGenerativePipeline

**风格条件化生成管道系统** - 一个基于结构化参数空间的可控图像风格迁移系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 项目简介

StyleConditionedGenerativePipeline 不是一个"提示词工程工具"，而是一个**风格条件化的优化系统**：

```
视觉风格 → 结构化参数空间（Style JSON） → 可优化的生成系统
```

### 核心功能

#### 1. Learning Mode（风格学习模式）
```
输入图片 → 提取 Style JSON → 迭代优化 → 生成符合风格的新图片
```
- 自动提取图片的风格参数
- 通过闭环优化确保生成图片符合参考风格
- 支持 6 个维度的精确控制（color、line、lighting、composition、material、detail_density）

#### 2. Production Mode（风格生产模式）
```
加载已保存的 Style JSON → 直接生成图片
```
- 从风格库加载预定义风格
- 确定性生成（相同输入 → 相同输出）
- 无需优化循环，快速生成

---

## 🏗️ 系统架构

### 核心模块

```
┌─────────────┐
│  Extractor  │ → 图片 → Style JSON（结构化参数）
└─────────────┘
       ↓
┌─────────────┐
│Style Engine │ → 归一化 Style JSON（9步流程）
└─────────────┘
       ↓
┌─────────────┐
│Prompt Gen   │ → Style JSON → 固定格式文本提示词
└─────────────┘
       ↓
┌─────────────┐
│Image Gen    │ → 提示词 → 生成图片
└─────────────┘
       ↓
┌─────────────┐
│ Evaluator   │ → 对比生成图片与参考风格 → 6维分数 + adjustments
└─────────────┘
       ↓
┌─────────────┐
│ Optimizer   │ → 根据 adjustments 更新 Style JSON
└─────────────┘
       ↓
    （循环）
```

### 关键特性

- **确定性**: 相同输入 → 相同输出（数值容差 ±0.02）
- **可优化性**: 基于结构化参数空间的梯度近似优化
- **可解释性**: 6 个维度独立评分，明确的调整方向
- **可扩展性**: 模块化设计，易于替换和扩展

---

## 📊 Style JSON 示例

```json
{
  "style_id": "watercolor_architecture_v1",
  "composition": {
    "perspective": "isometric",
    "layout": "centered",
    "depth": 0.6
  },
  "line": {
    "type": "clean",
    "width": 1.2,
    "variation": 0.1,
    "locked": true
  },
  "color": {
    "palette": ["#F5E6D3", "#8B9556", "#8B7355"],
    "saturation": 0.35,
    "contrast": 0.4,
    "temperature": "warm"
  },
  "material": {
    "type": "watercolor",
    "texture_strength": 0.5,
    "locked": true
  },
  "lighting": {
    "type": "soft_global",
    "direction": "top_left",
    "intensity": 0.3
  },
  "detail_density": {
    "foreground": 0.8,
    "background": 0.3
  },
  "negative_constraints": [
    "no photorealism",
    "no harsh shadows"
  ]
}
```

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/RiddleBox/StyleConditionedGenerativePipeline.git
cd StyleConditionedGenerativePipeline

# 安装依赖
pip install -r requirements.txt
```

### 使用方式

#### 方式 1：手动模式（推荐入门）
1. 使用 `skills/extractor/SKILL.md` 在 ChatGPT 中提取 Style JSON
2. 运行 Pipeline 生成 Prompt
3. 手动在 ChatGPT 中生成图片

#### 方式 2：自动模式（需要 API）
```python
from src.pipeline.learning_mode import LearningModePipeline

pipeline = LearningModePipeline(
    extractor_api="openai",
    generator_api="dalle3"
)

result = pipeline.run(
    image_path="input.jpg",
    content="cozy rooftop terrace scene"
)
```

#### 方式 3：OpenClaw 集成
```bash
# 在 OpenClaw 中直接使用
@openclaw 用这张图片的风格生成一个新场景
```

---

## 📁 项目结构

```
StyleConditionedGenerativePipeline/
├── docs/                    # 核心设计文档（9个规范 + 实施计划）
├── src/
│   ├── core/                # 核心模块（Schema、Engine、Prompt Generator、Library）
│   ├── extractor/           # 风格提取器
│   ├── generator/           # 图像生成器
│   ├── evaluator/           # 风格评估器
│   ├── optimizer/           # 参数优化器
│   └── pipeline/            # 管道编排
├── skills/                  # OpenClaw Skills
├── tests/                   # 单元测试
└── config/                  # 配置文件
```

---

## 📚 核心文档

1. [统一实施计划](./docs/IMPLEMENTATION_PLAN.md) - **唯一权威实施方案**
2. [三向映射表](./docs/Style_Evaluator_Optimizer_Mapping_Contract.md) - 系统核心契约
3. [Style JSON Schema 规范](./docs/Style_JSON_Schema_Deep_Specification_v1.md)
4. [Pipeline 集成规范](./docs/Style_Pipeline_Integration_Specification_v2.1.md)

完整文档列表见 [docs/](./docs/) 目录。

---

## 🔧 技术栈

- **Extractor**: GPT-4V / Claude 3.5 Sonnet
- **Image Generator**: DALL-E 3 / Midjourney
- **Evaluator**: CLIP + OpenCV + scikit-learn
- **Style Library**: SQLite
- **测试框架**: pytest

---

## 📊 开发进度

| Phase | 任务 | 状态 |
|-------|------|------|
| Phase 0 | 项目初始化 | 🟡 进行中 |
| Phase 1 | 核心模块 | ⚪ 未开始 |
| Phase 2 | Extractor（Skill） | ⚪ 未开始 |
| Phase 3 | Image Generator（手动） | ⚪ 未开始 |
| Phase 4 | Evaluator v2 | ⚪ 未开始 |
| Phase 5 | Optimizer + Pipeline | ⚪ 未开始 |
| Phase 6 | 自动化 | ⚪ 未开始 |
| Phase 7 | OpenClaw 集成 | ⚪ 未开始 |

详细进度见 [IMPLEMENTATION_PLAN.md](./docs/IMPLEMENTATION_PLAN.md)

---

## 🤝 贡献

欢迎贡献！请先阅读 [IMPLEMENTATION_PLAN.md](./docs/IMPLEMENTATION_PLAN.md) 了解项目架构和开发规范。

---

## 📄 许可证

MIT License - 详见 [LICENSE](./LICENSE) 文件

---

## 🙏 致谢

本项目的设计灵感来自：
- 风格迁移领域的经典研究
- 可控生成系统的工程实践
- OpenClaw 社区的反馈和建议

---

**项目状态**: 🚧 开发中 | **最后更新**: 2026-05-06
