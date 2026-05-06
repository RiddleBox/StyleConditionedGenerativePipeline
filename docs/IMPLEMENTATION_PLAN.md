# StyleConditionedGenerativePipeline 统一实现方案 v1.0

**文档版本**: v1.0  
**创建日期**: 2026-05-06  
**最后更新**: 2026-05-06  
**状态**: 规划中

---

## 📋 文档目的

本文档是 StyleConditionedGenerativePipeline 项目的**唯一权威实现方案**，整合了：
1. 9 个核心设计文档的技术规范
2. OpenClaw 的工程实施建议
3. ChatGPT 的架构优化方案（三向映射表）
4. 所有后续的计划更新和进度追踪

**所有实现、进度确认、计划调整都在此文档中处理。**

---

## 🎯 项目核心定位

### 系统本质
这不是一个"提示词工程工具"，而是一个**风格条件化的优化系统**：

```
视觉风格 → 结构化参数空间（Style JSON） → 可优化的生成系统
```

### 两大核心功能

#### 1. Learning Mode（风格学习模式）
```
输入图片 → 提取 Style JSON → 迭代优化 → 生成符合风格的新图片
```
- **目标**: 最小化生成图像与参考风格的差异
- **核心**: 闭环优化（Extractor → Generator → Evaluator → Optimizer → loop）

#### 2. Production Mode（风格生产模式）
```
加载已保存的 Style JSON → 直接生成图片
```
- **目标**: 忠实再现预定义风格
- **核心**: 确定性生成（无优化循环）

---

## 🧩 系统架构

### 核心模块（6个）

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

### 关键约束

1. **Style JSON 是唯一的中间表示（IR）**
   - 所有模块都基于 Style JSON 通信
   - 提示词只是编译产物，不是核心

2. **确定性要求**
   - 相同输入 → 相同输出（数值容差 ±0.02）
   - 所有模块必须可复现

3. **Reference Style 不变性**
   - Learning Mode 中，`reference_style` 在初始归一化后固定
   - 迭代过程中只更新 `current_style`，但评估始终对比 `reference_style`

---

## 🔥 关键设计决策（修正版）

### 修正 1：Evaluator 必须绑定 Style JSON

**问题**: 原方案中 Evaluator 的 6 个维度是"视觉特征"，未明确映射到 Style JSON 字段

**后果**: Optimizer 不知道如何将评估反馈转换为参数调整

**解决方案**: 建立 **Style JSON ↔ Evaluator ↔ Optimizer 三向映射表**（见下文）

---

### 修正 2：Optimizer 输入必须是完整结构

**问题**: 原方案中 Optimizer 只接收 `score`，丢失了结构化信息

**后果**: Optimizer 只能做黑盒搜索，无法做定向调整

**解决方案**:
```python
# ❌ 错误
result = optimize_style(
    current_style=current_style,
    evaluation=score,  # 只有分数
)

# ✔ 正确
result = optimize_style(
    current_style=current_style,
    evaluation=evaluation,  # 完整的评估结构
    iteration=iteration,
    history=history
)
```

---

### 修正 3：adjustments 必须是结构化的参数 delta

**问题**: 原方案中 adjustments 定义太抽象（`style_delta` / `prompt_delta`）

**后果**: Optimizer 不知道如何使用

**解决方案**:
```python
# ✔ 正确格式
adjustments = {
    "color.saturation": -0.2,      # 减少饱和度
    "lighting.intensity": 0.1,     # 增加光照强度
    "line.width": -0.15            # 减少线条宽度
}
```

---

### 修正 4：CLIP 权重降低

**问题**: CLIP 偏向语义一致性，而非风格一致性

**解决方案**:
```python
# 推荐权重
score = 0.2 * clip_score + 0.8 * mean(style_scores)

# 或更激进（风格已接近时忽略 CLIP 漂移）
if mean(style_scores) > 0.85:
    score = mean(style_scores)
else:
    score = 0.2 * clip_score + 0.8 * mean(style_scores)
```

---

## 📊 Style-Evaluator-Optimizer 三向映射表

这是整个系统的**核心契约**，决定了系统是"可控生成"还是"调参黑箱"。

### 映射原则

```
Evaluator ≠ 看图打分
Evaluator = Style JSON 参数误差函数

Optimizer ≠ 调 prompt
Optimizer = 在 Style 参数空间做有方向的更新
```

### 完整映射表

| Evaluator 维度 | Style JSON 字段 | Evaluator 指标 | Optimizer 调整 |
|---------------|----------------|---------------|---------------|
| **color** | `color.palette` | Wasserstein 距离 | 不可调整（由 Extractor 固定） |
| | `color.saturation` | HSV 饱和度差异 | `saturation ± delta` |
| | `color.contrast` | 亮度范围差异 | `contrast ± delta` |
| | `color.temperature` | 色温匹配 | 枚举字段，不可调整 |
| **line** | `line.type` | 边缘类型匹配 | 枚举字段，不可调整 |
| | `line.width` | 边缘宽度差异 | `width ± delta` |
| | `line.variation` | 边缘一致性差异 | `variation ± delta` |
| **lighting** | `lighting.type` | 光照类型匹配 | 枚举字段，不可调整 |
| | `lighting.direction` | 光照方向匹配 | 枚举字段，不可调整 |
| | `lighting.intensity` | 亮度直方图距离 | `intensity ± delta` |
| **composition** | `composition.perspective` | 空间特征相似度 | 枚举字段，不可调整 |
| | `composition.layout` | 布局相似度 | 枚举字段，不可调整 |
| | `composition.depth` | 深度感知差异 | `depth ± delta` |
| **material** | `material.type` | 材质类型匹配 | 枚举字段，不可调整 |
| | `material.texture_strength` | 纹理强度差异（Gabor） | `texture_strength ± delta` |
| **detail_density** | `detail_density.foreground` | 前景复杂度差异 | `foreground ± delta` |
| | `detail_density.background` | 背景复杂度差异 | `background ± delta` |

### 关键约束

1. **枚举字段不可调整**: 由 Extractor 固定，Optimizer 不能修改
2. **数值字段可调整**: 9 个数值字段可以通过 Optimizer 更新
3. **palette 不可调整**: 调色板由 Extractor 提取，Optimizer 只能调整 saturation 和 contrast

### Evaluator 输出格式（标准）

```json
{
    "similarity_score": 0.82,
    "global_score": 0.76,
    "style_scores": {
        "color": 0.88,
        "line": 0.72,
        "lighting": 0.81,
        "composition": 0.79,
        "material": 0.69,
        "detail_density": 0.85
    },
    "deviations": [
        "line.width too high",
        "color.saturation too low",
        "lighting.intensity too weak"
    ],
    "adjustments": {
        "line.width": -0.2,
        "color.saturation": 0.15,
        "lighting.intensity": 0.1
    }
}
```

---

## 🚀 实施计划（7个阶段）

### Phase 1: 核心模块（纯逻辑，无外部依赖）

**目标**: 实现确定性的核心模块，确保幂等性和可测试性

**任务**:
1. ✅ Style JSON Schema 验证器
   - 实现 JSON Schema 验证
   - 单元测试：验证所有边界情况
   - 交付物：`src/core/schema.py`

2. ✅ Style Engine
   - 实现 9 步归一化流程
   - 单元测试：验证幂等性（`normalize(normalize(x)) == normalize(x)`）
   - 交付物：`src/core/engine.py`

3. ✅ Prompt Generator
   - 实现确定性编译器
   - 单元测试：验证确定性（相同输入 → 相同输出）
   - 交付物：`src/core/prompt_generator.py`

4. ✅ Style Library
   - 实现 SQLite 持久化存储
   - 单元测试：验证 CRUD 操作
   - 交付物：`src/core/library.py`

5. ✅ **新增：三向映射表文档**
   - 创建 `docs/Style_Evaluator_Optimizer_Mapping_Contract.md`
   - 定义完整的映射规则

**验收标准**:
- 所有单元测试通过
- 确定性测试通过（相同输入 → 相同输出）
- 幂等性测试通过（Style Engine）

**预计时间**: 1-2 周

---

### Phase 2: Extractor（方式 1：Skill 模式）

**目标**: 快速验证 Extractor 的可行性，无需编写代码

**任务**:
6. ✅ 创建 Extractor Skill
   - 编写 `skills/extractor/SKILL.md`
   - 包含完整的系统提示词和 Style JSON Schema
   - 用户手动在 ChatGPT 中使用

7. ✅ 手动测试
   - 用 3-5 张不同风格的图片测试
   - 验证输出的 Style JSON 是否符合 Schema
   - 验证 Style Engine 能否正确归一化

**交付物**:
- `skills/extractor/SKILL.md`
- `docs/extractor_manual_test_results.md`

**验收标准**:
- Extractor 能输出符合 Schema 的 Style JSON
- Style Engine 能成功归一化输出

**预计时间**: 3-5 天

---

### Phase 3: Image Generator（形态 1：手动模式）

**目标**: 验证 Prompt Generator 的输出质量

**任务**:
8. ✅ 实现手动模式
   - Pipeline 在生成 Prompt 后暂停
   - 输出 Prompt 和下一步指令
   - 用户手动在 ChatGPT 生成图片

9. ✅ 手动测试
   - 用 Phase 2 的 Style JSON 生成 Prompt
   - 在 ChatGPT 中生成图片
   - 验证图片是否符合预期风格

**交付物**:
- `src/pipeline/manual_mode.py`
- `docs/prompt_quality_test_results.md`

**验收标准**:
- Prompt Generator 输出格式正确
- 生成的图片基本符合预期风格

**预计时间**: 3-5 天

---

### Phase 4: Evaluator v2（结构化评估器）

**目标**: 实现确定性的结构化评估器

**任务**:
10. ✅ 实现 Level 1：CLIP global similarity
    - 使用 `openai/clip-vit-base-patch32` 模型
    - 计算 cosine similarity
    - 交付物：`src/evaluator/clip_evaluator.py`

11. ✅ 实现 Level 2：Structured style metrics
    - **严格按照三向映射表实现**
    - color: K-means 提取调色板 + Wasserstein 距离
    - line: Canny 边缘检测
    - lighting: 亮度直方图距离
    - composition: CLIP 空间特征
    - material: Gabor 滤波器（纹理）
    - detail_density: 高频分量
    - 交付物：`src/evaluator/structured_metrics.py`

12. ✅ 实现 Level 3：Score aggregation
    - 加权平均：`score = 0.2 * global_score + 0.8 * mean(style_scores)`
    - 交付物：`src/evaluator/aggregator.py`

13. ✅ 实现 Level 4：Deterministic adjustments
    - 根据维度差异生成结构化的 adjustments
    - 格式：`{"field_path": delta_value}`
    - 交付物：`src/evaluator/adjustments.py`

**交付物**:
- `src/evaluator/clip_evaluator.py`
- `src/evaluator/structured_metrics.py`
- `src/evaluator/aggregator.py`
- `src/evaluator/adjustments.py`
- `tests/test_evaluator.py`

**验收标准**:
- 确定性测试通过（相同输入 → 相同输出 ±0.02）
- 6 个维度分数都能正确计算
- adjustments 格式符合规范

**预计时间**: 1-2 周

---

### Phase 5: Optimizer + Pipeline（Learning Mode）

**目标**: 实现完整的优化循环

**任务**:
14. ✅ 实现 Optimizer
    - **输入必须是完整的 `evaluation` 结构**
    - 根据 `evaluation.adjustments` 更新 Style JSON
    - 只更新数值字段，跳过枚举字段
    - 实现冻结规则（连续 3 次变化 < 0.02 则冻结）
    - 交付物：`src/optimizer/optimizer.py`

15. ✅ 实现 Pipeline Orchestrator（Learning Mode）
    - 实现迭代循环（最多 5 次）
    - 实现早停机制（score ≥ 0.9）
    - 实现 Reference Style 不变性
    - 交付物：`src/pipeline/learning_mode.py`

16. ✅ 端到端测试（手动模式）
    - 用户手动提供图片（每次迭代）
    - 验证 score 是否收敛
    - 交付物：`docs/learning_mode_test_results.md`

**交付物**:
- `src/optimizer/optimizer.py`
- `src/pipeline/learning_mode.py`
- `docs/learning_mode_test_results.md`

**验收标准**:
- Optimizer 能正确更新 Style JSON
- Pipeline 能完成完整的迭代循环
- score 能收敛到目标值（或达到最大迭代次数）

**预计时间**: 1-2 周

---

### Phase 6: 自动化（方式 2 + 形态 2）

**目标**: 实现全自动 Pipeline

**任务**:
17. ✅ 实现 Extractor（方式 2：可配置 LLM）
    - 支持 OpenAI / Anthropic API
    - 实现重试机制（最多 3 次）
    - 实现稳定性采样（可选，运行 3 次取平均）
    - 交付物：`src/extractor/llm_extractor.py`

18. ✅ 实现 Image Generator（形态 2：自动模式）
    - 支持 DALL-E 3 API
    - 支持 Midjourney API（可选）
    - 交付物：`src/generator/dalle_generator.py`、`src/generator/midjourney_generator.py`

19. ✅ 实现 Production Mode
    - 从 Style Library 加载预定义风格
    - 直接生成图片（无优化循环）
    - 交付物：`src/pipeline/production_mode.py`

20. ✅ 端到端测试（自动模式）
    - 完全自动运行 Learning Mode
    - 验证收敛性和确定性
    - 交付物：`docs/auto_mode_test_results.md`

**交付物**:
- `src/extractor/llm_extractor.py`
- `src/generator/dalle_generator.py`
- `src/generator/midjourney_generator.py`（可选）
- `src/pipeline/production_mode.py`
- `docs/auto_mode_test_results.md`

**验收标准**:
- 全自动 Learning Mode 能成功运行
- Production Mode 能稳定生成图片
- 确定性测试通过

**预计时间**: 1-2 周

---

### Phase 7: OpenClaw 集成（方式 3）

**目标**: 无缝集成到 OpenClaw

**任务**:
21. ✅ 创建 OpenClaw Skill
    - 封装整个 Pipeline
    - 支持图片输入和结果输出
    - 交付物：`skills/style-pipeline/SKILL.md`

22. ✅ OpenClaw 测试
    - 在 OpenClaw 环境中测试
    - 验证用户体验
    - 交付物：`docs/openclaw_integration_guide.md`

**交付物**:
- `skills/style-pipeline/SKILL.md`
- `docs/openclaw_integration_guide.md`

**验收标准**:
- 用户可以通过 OpenClaw 直接使用系统
- 用户体验流畅

**预计时间**: 3-5 天

---

## 📁 项目结构

```
StyleConditionedGenerativePipeline/
├── docs/                                    # 核心设计文档
│   ├── Implementation_Contract_Specification_v1.md
│   ├── Prompt_Generator_Deep_Specification_v1.md
│   ├── Style_Engine_Deep_Specification_v1.md
│   ├── Style_Evaluator_Deep_Specification_v1.md
│   ├── Style_Extractor_Deep_Specification_v1.md
│   ├── Style_JSON_Schema_Deep_Specification_v1.md
│   ├── Style_Library_Specification_v0.md
│   ├── Style_Optimizer_Deep_Specification_v1.md
│   ├── Style_Pipeline_Integration_Specification_v2.1.md
│   ├── Style_Evaluator_Optimizer_Mapping_Contract.md  # 三向映射表
│   └── IMPLEMENTATION_PLAN.md                         # 本文档
├── src/
│   ├── core/                                # Phase 1
│   │   ├── schema.py                        # Style JSON Schema 验证器
│   │   ├── engine.py                        # Style Engine（9 步归一化）
│   │   ├── prompt_generator.py             # Prompt Generator（确定性编译器）
│   │   └── library.py                       # Style Library（SQLite 存储）
│   ├── extractor/                           # Phase 2 & 6
│   │   ├── llm_extractor.py                 # 可配置 LLM Extractor
│   │   └── config.py                        # LLM 配置
│   ├── generator/                           # Phase 3 & 6
│   │   ├── dalle_generator.py               # DALL-E 3 Generator
│   │   └── midjourney_generator.py          # Midjourney Generator（可选）
│   ├── evaluator/                           # Phase 4
│   │   ├── clip_evaluator.py                # CLIP global similarity
│   │   ├── structured_metrics.py            # 6 个维度的结构化评估
│   │   ├── aggregator.py                    # Score aggregation
│   │   └── adjustments.py                   # Deterministic adjustments
│   ├── optimizer/                           # Phase 5
│   │   └── optimizer.py                     # Optimizer（参数更新）
│   └── pipeline/                            # Phase 5 & 6
│       ├── learning_mode.py                 # Learning Mode
│       ├── production_mode.py               # Production Mode
│       └── manual_mode.py                   # 手动模式（Phase 3）
├── skills/                                  # Phase 2 & 7
│   ├── extractor/
│   │   └── SKILL.md                         # Extractor Skill（手动模式）
│   └── style-pipeline/
│       └── SKILL.md                         # OpenClaw 集成 Skill
├── tests/                                   # 单元测试
│   ├── test_core.py
│   ├── test_evaluator.py
│   ├── test_optimizer.py
│   └── test_pipeline.py
├── config/
│   └── config.yaml                          # 配置文件（LLM API、Image Generator API）
├── requirements.txt                         # Python 依赖
├── README.md                                # 项目说明
└── .gitignore
```

---

## 🔧 技术选型

### Extractor
- **方式 1（手动）**: ChatGPT 网页端 + Skill
- **方式 2（自动）**: GPT-4V API（OpenAI）或 Claude 3.5 Sonnet（Anthropic）
- **方式 3（OpenClaw）**: 集成到 OpenClaw Skill

### Image Generator
- **形态 1（手动）**: ChatGPT 网页端（DALL-E 3）
- **形态 2（自动）**: DALL-E 3 API 或 Midjourney API

### Evaluator
- **Level 1**: CLIP（`openai/clip-vit-base-patch32`）
- **Level 2**: OpenCV + scikit-learn + scipy
- **Level 3**: NumPy
- **Level 4**: 纯逻辑（基于三向映射表）

### 其他
- **Style Library**: SQLite
- **测试框架**: pytest
- **代码风格**: black + flake8

---

## 📊 进度追踪

### 当前状态
- **Phase**: Phase 0（项目初始化）
- **进度**: 10%
- **当前任务**: 创建项目结构和核心文档

### 里程碑

| Phase | 任务 | 状态 | 开始日期 | 完成日期 |
|-------|------|------|---------|---------|
| Phase 0 | 项目初始化 | 🟡 进行中 | 2026-05-06 | - |
| Phase 1 | 核心模块 | ⚪ 未开始 | - | - |
| Phase 2 | Extractor（Skill） | ⚪ 未开始 | - | - |
| Phase 3 | Image Generator（手动） | ⚪ 未开始 | - | - |
| Phase 4 | Evaluator v2 | ⚪ 未开始 | - | - |
| Phase 5 | Optimizer + Pipeline | ⚪ 未开始 | - | - |
| Phase 6 | 自动化 | ⚪ 未开始 | - | - |
| Phase 7 | OpenClaw 集成 | ⚪ 未开始 | - | - |

---

## 🚨 风险与应对

### 风险 1：Evaluator 确定性不足
**影响**: 迭代不可复现，优化不稳定

**应对**:
- 使用固定的随机种子
- CLIP 模型使用确定性推理模式
- 图像预处理标准化

### 风险 2：Optimizer 收敛慢或不收敛
**影响**: 无法达到目标 score

**应对**:
- 调整 step_scale（从 0.5 降到 0.3）
- 增加 max_iterations（从 5 增到 10）
- 实现自适应步长

### 风险 3：API 成本过高
**影响**: 测试和使用成本高

**应对**:
- Phase 2-3 优先使用手动模式
- 使用更便宜的模型（DALL-E 2 代替 DALL-E 3）
- 实现本地 Stable Diffusion 支持

---

## 📝 变更日志

### v1.0 (2026-05-06)
- 初始版本
- 整合 9 个核心设计文档
- 整合 OpenClaw 工程方案
- 整合 ChatGPT 架构优化（三向映射表）
- 修正 3 个关键问题（Evaluator 绑定、Optimizer 输入、adjustments 格式）

---

## 📚 参考文档

1. [Implementation Contract Specification v1.0](./Implementation_Contract_Specification_v1.md)
2. [Prompt Generator Deep Specification v1.0](./Prompt_Generator_Deep_Specification_v1.md)
3. [Style Engine Deep Specification v1.0](./Style_Engine_Deep_Specification_v1.md)
4. [Style Evaluator Deep Specification v1.0](./Style_Evaluator_Deep_Specification_v1.md)
5. [Style Extractor Deep Specification v1.0](./Style_Extractor_Deep_Specification_v1.md)
6. [Style JSON Schema Deep Specification v1.0](./Style_JSON_Schema_Deep_Specification_v1.md)
7. [Style Library Specification v0.1](./Style_Library_Specification_v0.md)
8. [Style Optimizer Deep Specification v1.0](./Style_Optimizer_Deep_Specification_v1.md)
9. [Style Pipeline Integration Specification v1.2.1](./Style_Pipeline_Integration_Specification_v2.1.md)
10. [Style-Evaluator-Optimizer Mapping Contract](./Style_Evaluator_Optimizer_Mapping_Contract.md)

---

**文档维护**: 所有计划更新、进度确认、问题记录都在本文档中处理。
