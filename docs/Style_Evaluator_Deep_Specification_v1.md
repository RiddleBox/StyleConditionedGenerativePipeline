# Style Evaluator Deep Specification v1.0

---

## 1. Module Definition

**Module Name:** Style Evaluator
**Type:** Deterministic Multi-Dimensional Scorer

### Purpose

Evaluate how closely a generated image matches a reference Style JSON,
and produce actionable parameter adjustments.

---

## 2. Function Signature

```python
def evaluate_style(reference_style: dict, generated_image: Any, original_image: Any = None) -> dict
```

---

## 3. Input Specification

```json
{
  "reference_style": {Style JSON v1.0},
  "generated_image": "<image>",
  "original_image": "<optional>"
}
```

---

## 4. Output Specification

```json
{
  "similarity_score": 0.0,
  "dimension_scores": {
    "composition": 0.0,
    "line": 0.0,
    "color": 0.0,
    "material": 0.0,
    "lighting": 0.0,
    "detail_density": 0.0
  },
  "deviations": ["string"],
  "adjustments": {
    "path.to.field": 0.0
  }
}
```

---

## 5. Global Rules

* Deterministic (same input → same output)
* No subjective language
* No randomness
* All scores must be reproducible
* All deviations must map to adjustments

---

## 6. Scoring System

### 6.1 Score Range

```text
0.0 = completely different
1.0 = perfect match
```

---

### 6.2 Precision

* All scores rounded to **2 decimal places**

---

### 6.3 Overall Score

```python
similarity_score = mean(dimension_scores.values())
```

---

## 7. Dimension Evaluation Rules

---

### 7.1 Composition

Evaluate:

* perspective match
* layout match
* depth similarity

Scoring:

```text
Mismatch in perspective → -0.4
Mismatch in layout → -0.3
Depth difference > 0.3 → -0.3
```

Clamp final score to [0,1]

---

### 7.2 Line

Evaluate:

* presence (none vs exists)
* width deviation
* variation deviation

Scoring:

```text
Type mismatch → -0.5
Width diff > 0.5 → -0.3
Variation diff > 0.3 → -0.2
```

---

### 7.3 Color

Evaluate:

* palette overlap ratio
* saturation diff
* contrast diff
* temperature match

Scoring:

```text
palette similarity < 0.5 → -0.4
saturation diff > 0.2 → -0.2
contrast diff > 0.2 → -0.2
temperature mismatch → -0.2
```

---

### 7.4 Material

Evaluate:

* type match
* texture strength

Scoring:

```text
type mismatch → -0.6
texture diff > 0.3 → -0.4
```

---

### 7.5 Lighting

Evaluate:

* type match
* direction match
* intensity diff

Scoring:

```text
type mismatch → -0.4
direction mismatch → -0.3
intensity diff > 0.3 → -0.3
```

---

### 7.6 Detail Density

Evaluate:

* foreground level
* background level

Scoring:

```text
foreground diff > 0.3 → -0.5
background diff > 0.3 → -0.5
```

---

## 8. Deviation Generation

Each deviation must:

* Be specific
* Map to a parameter
* Use fixed phrasing

### Format

```text
"{field} {issue}"
```

Examples:

```text
line.width too high
color.saturation too low
lighting.direction mismatch
```

---

## 9. Adjustment Generation

---

### 9.1 General Rule

```text
delta = reference_value - observed_value
```

---

### 9.2 Constraints

```text
- delta range: [-0.5, +0.5]
- round to 2 decimals
```

---

### 9.3 Mapping

Each deviation MUST produce one adjustment.

Examples:

```json
{
  "line.width": -0.2,
  "color.saturation": 0.1
}
```

---

### 9.4 Enum Handling

```text
IF enum mismatch:
  do NOT change enum
  adjust related numeric fields instead
```

---

## 10. Deviation → Adjustment Mapping Rules

| Deviation      | Adjustment                   |
| -------------- | ---------------------------- |
| line too thick | line.width: negative         |
| low saturation | color.saturation: positive   |
| high contrast  | color.contrast: negative     |
| weak lighting  | lighting.intensity: positive |

---

## 11. Consistency Rules

* Each deviation must have corresponding adjustment
* No unused adjustments
* No duplicate paths

---

## 12. Determinism Guarantee

```text
evaluate_style(x) must always return identical result
```

---

## 13. Forbidden Behavior

```text
- No vague descriptions
- No missing dimensions
- No extra fields
- No probabilistic scoring
- No language variation
```

---

## 14. Validation Rules

### Test 1: Determinism

Same input → identical JSON output

---

### Test 2: Structural Integrity

Output must contain:

* similarity_score
* 6 dimension_scores
* deviations array
* adjustments object

---

### Test 3: Adjustment Validity

* All deltas within range
* All paths valid
* All values numeric

---

## 15. Core Principle

```text
Evaluator is a numeric error function, not a critic.
```

---
