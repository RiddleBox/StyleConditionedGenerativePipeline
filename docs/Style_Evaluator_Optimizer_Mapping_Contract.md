# Style-Evaluator-Optimizer 三向映射表 v1.0

**文档版本**: v1.0  
**创建日期**: 2026-05-06  
**状态**: 正式版

---

## 🎯 文档目的

这是整个 StyleConditionedGenerativePipeline 系统的**核心契约**，定义了：
1. Style JSON 参数空间
2. Evaluator 如何评估每个维度
3. Optimizer 如何调整每个参数

**这张表决定了系统是"可控生成系统"还是"调参黑箱"。**

---

## 🧠 核心原则

```
Evaluator ≠ 看图打分
Evaluator = Style JSON 参数误差函数

Optimizer ≠ 调 prompt
Optimizer = 在 Style 参数空间做有方向的更新
```

---

## 📊 完整映射表

### 1. COLOR（颜色系统）

#### Style JSON 定义
```json
{
  "color": {
    "palette": ["#RRGGBB", "#RRGGBB", ...],
    "saturation": 0.0-1.0,
    "contrast": 0.0-1.0,
    "temperature": "warm | neutral | cool"
  }
}
```

#### Evaluator 实现
```python
# 1. 提取调色板（K-means，k=5-8）
current_palette = extract_palette(generated_image, k=8)
reference_palette = style_json["color"]["palette"]

# 2. 计算调色板距离（Wasserstein distance）
palette_dist = wasserstein_distance(current_palette, reference_palette)

# 3. 计算饱和度差异
current_sat = compute_saturation(generated_image)
ref_sat = style_json["color"]["saturation"]
sat_diff = abs(current_sat - ref_sat)

# 4. 计算对比度差异
current_contrast = compute_contrast(generated_image)
ref_contrast = style_json["color"]["contrast"]
contrast_diff = abs(current_contrast - ref_contrast)

# 5. 计算色温匹配
current_temp = classify_temperature(generated_image)
ref_temp = style_json["color"]["temperature"]
temp_match = 1.0 if current_temp == ref_temp else 0.5

# 6. 综合评分
color_score = 1.0 - normalize(
    0.4 * palette_dist + 
    0.3 * sat_diff + 
    0.2 * contrast_diff + 
    0.1 * (1 - temp_match)
)
```

#### Optimizer 调整
```python
adjustments = {
    "color.saturation": (ref_sat - current_sat) * step_scale,
    "color.contrast": (ref_contrast - current_contrast) * step_scale
}

# 注意：
# - palette 不可调整（由 Extractor 固定）
# - temperature 是枚举字段，不可调整
```

---

### 2. LINE（线条/边缘）

#### Style JSON 定义
```json
{
  "line": {
    "type": "none | clean | sketch | ink",
    "width": 0.0-5.0,
    "variation": 0.0-1.0,
    "locked": false
  }
}
```

#### Evaluator 实现
```python
# 1. 边缘检测（Canny）
edges = cv2.Canny(generated_image, threshold1=50, threshold2=150)

# 2. 计算边缘密度
edge_density = np.sum(edges > 0) / edges.size
ref_density = infer_density_from_line_width(style_json["line"]["width"])
density_diff = abs(edge_density - ref_density)

# 3. 计算边缘宽度
edge_width = compute_edge_thickness(edges)
ref_width = style_json["line"]["width"]
width_diff = abs(edge_width - ref_width)

# 4. 计算边缘变化（一致性）
edge_variation = compute_edge_consistency(edges)
ref_variation = style_json["line"]["variation"]
variation_diff = abs(edge_variation - ref_variation)

# 5. 综合评分
line_score = 1.0 - normalize(
    0.4 * width_diff + 
    0.3 * density_diff + 
    0.3 * variation_diff
)
```

#### Optimizer 调整
```python
adjustments = {
    "line.width": (ref_width - edge_width) * step_scale,
    "line.variation": (ref_variation - edge_variation) * step_scale
}

# 注意：
# - line.type 是枚举字段，不可调整
# - 如果 line.locked == true，跳过所有调整
```

---

### 3. LIGHTING（光照）

#### Style JSON 定义
```json
{
  "lighting": {
    "type": "ambient | directional | soft_global | studio",
    "direction": "none | left | right | top | top_left | top_right",
    "intensity": 0.0-1.0
  }
}
```

#### Evaluator 实现
```python
# 1. 计算亮度均值
current_brightness = np.mean(cv2.cvtColor(generated_image, cv2.COLOR_RGB2GRAY))
ref_brightness = infer_brightness_from_intensity(style_json["lighting"]["intensity"])
brightness_diff = abs(current_brightness - ref_brightness) / 255.0

# 2. 计算亮度直方图距离
current_hist = cv2.calcHist([generated_image], [0], None, [256], [0, 256])
ref_hist = infer_histogram_from_style(style_json["lighting"])
hist_dist = cv2.compareHist(current_hist, ref_hist, cv2.HISTCMP_BHATTACHARYYA)

# 3. 综合评分
lighting_score = 1.0 - normalize(
    0.5 * brightness_diff + 
    0.5 * hist_dist
)
```

#### Optimizer 调整
```python
adjustments = {
    "lighting.intensity": (ref_brightness - current_brightness) * step_scale
}

# 注意：
# - lighting.type 和 lighting.direction 是枚举字段，不可调整
```

---

### 4. COMPOSITION（构图）

#### Style JSON 定义
```json
{
  "composition": {
    "perspective": "top_down | isometric | eye_level | low_angle | high_angle",
    "layout": "centered | rule_of_thirds | asymmetrical | symmetrical",
    "depth": 0.0-1.0
  }
}
```

#### Evaluator 实现
```python
# 1. 使用 CLIP 提取空间特征
current_spatial_features = clip_model.encode_image(generated_image)
ref_spatial_features = clip_model.encode_image(reference_image)
spatial_sim = cosine_similarity(current_spatial_features, ref_spatial_features)

# 2. 计算深度感知差异（基于边缘梯度）
current_depth = compute_depth_cue(generated_image)
ref_depth = style_json["composition"]["depth"]
depth_diff = abs(current_depth - ref_depth)

# 3. 综合评分
composition_score = 0.7 * spatial_sim + 0.3 * (1.0 - depth_diff)
```

#### Optimizer 调整
```python
adjustments = {
    "composition.depth": (ref_depth - current_depth) * step_scale
}

# 注意：
# - perspective 和 layout 是枚举字段，不可调整
```

---

### 5. MATERIAL / TEXTURE（材质）

#### Style JSON 定义
```json
{
  "material": {
    "type": "flat | watercolor | oil | ink | digital_paint",
    "texture_strength": 0.0-1.0,
    "locked": false
  }
}
```

#### Evaluator 实现
```python
# 1. 使用 Gabor 滤波器提取纹理特征
gabor_features = apply_gabor_filters(generated_image)
texture_energy = np.mean(np.abs(gabor_features))

# 2. 计算纹理强度差异
ref_texture = style_json["material"]["texture_strength"]
texture_diff = abs(texture_energy - ref_texture)

# 3. 综合评分
material_score = 1.0 - texture_diff
```

#### Optimizer 调整
```python
adjustments = {
    "material.texture_strength": (ref_texture - texture_energy) * step_scale
}

# 注意：
# - material.type 是枚举字段，不可调整
# - 如果 material.locked == true，跳过所有调整
```

---

### 6. DETAIL_DENSITY（细节密度）

#### Style JSON 定义
```json
{
  "detail_density": {
    "foreground": 0.0-1.0,
    "background": 0.0-1.0
  }
}
```

#### Evaluator 实现
```python
# 1. 分离前景和背景（简单阈值分割或深度估计）
foreground_mask, background_mask = segment_foreground_background(generated_image)

# 2. 计算前景细节密度（高频分量）
foreground_detail = compute_high_freq_energy(generated_image, foreground_mask)
ref_foreground = style_json["detail_density"]["foreground"]
foreground_diff = abs(foreground_detail - ref_foreground)

# 3. 计算背景细节密度
background_detail = compute_high_freq_energy(generated_image, background_mask)
ref_background = style_json["detail_density"]["background"]
background_diff = abs(background_detail - ref_background)

# 4. 综合评分
detail_score = 1.0 - normalize(
    0.6 * foreground_diff + 
    0.4 * background_diff
)
```

#### Optimizer 调整
```python
adjustments = {
    "detail_density.foreground": (ref_foreground - foreground_detail) * step_scale,
    "detail_density.background": (ref_background - background_detail) * step_scale
}
```

---

## 🧮 Score Aggregation（最终评分）

```python
# 1. 计算 6 个维度的平均分
style_score = np.mean([
    color_score,
    line_score,
    lighting_score,
    composition_score,
    material_score,
    detail_score
])

# 2. 计算 CLIP 全局相似度
clip_score = cosine_similarity(
    clip_model.encode_image(generated_image),
    clip_model.encode_image(reference_image)
)

# 3. 加权聚合
final_score = 0.2 * clip_score + 0.8 * style_score

# 4. 可选：如果风格已经很接近，忽略 CLIP 漂移
if style_score > 0.85:
    final_score = style_score
```

---

## 📋 Evaluator 输出标准格式

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

## ⚙️ Optimizer 规则

### Rule 1: 只根据 delta 更新
```python
new_value = current_value + step_scale * delta
```

### Rule 2: 不能修改 reference_style
```python
# ❌ 错误
reference_style["color"]["saturation"] += delta

# ✔ 正确
current_style["color"]["saturation"] += delta
```

### Rule 3: 必须 clamp
```python
new_value = np.clip(new_value, min_value, max_value)
```

### Rule 4: 小步收敛（防震荡）
```python
# 随迭代次数衰减步长
step_scale = 0.5 * (0.8 ** iteration)
```

### Rule 5: 冻结规则
```python
# 如果字段连续 3 次变化 < 0.02，标记为冻结
if abs(delta) < 0.02 for 3 consecutive iterations:
    frozen_fields.append(field_path)
```

---

## 🚫 明确禁止

### ❌ 不允许的操作

1. **Evaluator 输出自然语言**
   ```python
   # ❌ 错误
   deviations = ["The image looks too bright"]
   
   # ✔ 正确
   deviations = ["lighting.intensity too high"]
   ```

2. **Optimizer 解析文本**
   ```python
   # ❌ 错误
   if "too bright" in deviation:
       adjust_brightness()
   
   # ✔ 正确
   delta = adjustments["lighting.intensity"]
   new_value = current_value + delta
   ```

3. **用 LLM 做 adjustments**
   ```python
   # ❌ 错误
   adjustments = llm.generate_adjustments(evaluation)
   
   # ✔ 正确
   adjustments = compute_deterministic_deltas(
       current_metrics, 
       reference_metrics
   )
   ```

4. **用单一 score 驱动优化**
   ```python
   # ❌ 错误
   optimize_style(current_style, score=0.75)
   
   # ✔ 正确
   optimize_style(current_style, evaluation={
       "similarity_score": 0.75,
       "style_scores": {...},
       "adjustments": {...}
   })
   ```

---

## 📊 可调整字段汇总

| 字段路径 | 类型 | 范围 | 可调整 | 备注 |
|---------|------|------|--------|------|
| `color.palette` | array | - | ❌ | 由 Extractor 固定 |
| `color.saturation` | float | 0.0-1.0 | ✅ | |
| `color.contrast` | float | 0.0-1.0 | ✅ | |
| `color.temperature` | enum | - | ❌ | 枚举字段 |
| `line.type` | enum | - | ❌ | 枚举字段 |
| `line.width` | float | 0.0-5.0 | ✅ | |
| `line.variation` | float | 0.0-1.0 | ✅ | |
| `lighting.type` | enum | - | ❌ | 枚举字段 |
| `lighting.direction` | enum | - | ❌ | 枚举字段 |
| `lighting.intensity` | float | 0.0-1.0 | ✅ | |
| `composition.perspective` | enum | - | ❌ | 枚举字段 |
| `composition.layout` | enum | - | ❌ | 枚举字段 |
| `composition.depth` | float | 0.0-1.0 | ✅ | |
| `material.type` | enum | - | ❌ | 枚举字段 |
| `material.texture_strength` | float | 0.0-1.0 | ✅ | |
| `detail_density.foreground` | float | 0.0-1.0 | ✅ | |
| `detail_density.background` | float | 0.0-1.0 | ✅ | |

**可调整字段总数**: 9 个

---

## 🧠 核心洞察

### 为什么需要这张表？

1. **确定性**: 明确定义了每个维度的计算方法，确保可复现
2. **可优化性**: 明确定义了哪些参数可以调整，如何调整
3. **可解释性**: 明确定义了每个分数的含义和计算依据
4. **可扩展性**: 新增维度时只需扩展此表

### 这张表的本质

```
把"视觉风格"变成"可微（近似）参数空间"
```

---

## 📚 参考文档

1. [Style JSON Schema Deep Specification v1.0](./Style_JSON_Schema_Deep_Specification_v1.md)
2. [Style Evaluator Deep Specification v1.0](./Style_Evaluator_Deep_Specification_v1.md)
3. [Style Optimizer Deep Specification v1.0](./Style_Optimizer_Deep_Specification_v1.md)
4. [Implementation Plan](./IMPLEMENTATION_PLAN.md)

---

**文档维护**: 此文档是系统的核心契约，任何修改必须同步更新 Evaluator 和 Optimizer 的实现。
