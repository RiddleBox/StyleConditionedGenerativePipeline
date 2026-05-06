# Style Optimizer Deep Specification v1.0

---

## 1. Module Definition

**Module Name:** Style Optimizer
**Type:** Deterministic Parameter Updater

### Purpose

Update Style JSON parameters using evaluation feedback to reduce style error iteratively.

---

## 2. Function Signature

```python
def optimize_style(current_style: dict, evaluation: dict, iteration: int, history: list) -> dict
```

---

## 3. Input Specification

```json
{
  "current_style": {Style JSON v1.0},
  "evaluation": {
    "similarity_score": 0.0,
    "dimension_scores": {},
    "deviations": [],
    "adjustments": {
      "path.to.field": 0.0
    }
  },
  "iteration": 1,
  "history": [
    {"iteration": 0, "score": 0.65}
  ]
}
```

---

## 4. Output Specification

```json
{
  "new_style": {Style JSON v1.0},
  "changes": ["string"],
  "meta": {
    "frozen_fields": ["path"],
    "applied_adjustments": {
      "path": 0.0
    }
  }
}
```

---

## 5. Global Rules

* Deterministic (same input → same output)
* No schema modification
* No enum modification (unless explicitly allowed)
* No modification of locked fields
* Only numeric fields may be updated
* All updates must be recorded

---

## 6. Core Algorithm

---

### Step 1: Read Adjustments

```python
adjustments = evaluation["adjustments"]
```

---

### Step 2: Apply Step Scaling

```python
step_scale = 0.5
applied_delta = raw_delta * step_scale
```

---

### Step 3: Apply Updates

```python
new_value = current_value + applied_delta
```

---

### Step 4: Clamp Values

```text
color.saturation ∈ [0.0, 1.0]
color.contrast ∈ [0.0, 1.0]
material.texture_strength ∈ [0.0, 1.0]
lighting.intensity ∈ [0.0, 1.0]
detail_density.foreground ∈ [0.0, 1.0]
detail_density.background ∈ [0.0, 1.0]
line.width ∈ [0.0, 5.0]
line.variation ∈ [0.0, 1.0]
composition.depth ∈ [0.0, 1.0]
```

---

### Step 5: Ignore Invalid Updates

Skip update if:

```text
- field is locked
- field is enum
- path does not exist
```

---

### Step 6: Record Changes

Format:

```text
"path: delta_applied"
```

Example:

```text
color.saturation: -0.1
line.width: -0.2
```

---

## 7. Parameter Update Constraints

---

### Allowed Fields

```text
color.saturation
color.contrast
material.texture_strength
lighting.intensity
detail_density.foreground
detail_density.background
line.width
line.variation
composition.depth
```

---

### Forbidden Updates

```text
- Any enum field
- palette
- composition.layout
- composition.perspective
```

---

## 8. Convergence Mechanisms

---

### 8.1 Freeze Rule

```text
IF a field changes < 0.02 for 3 consecutive iterations:
  mark as frozen
  skip future updates
```

---

### 8.2 Max Iterations

```text
max_iterations = 5
```

---

### 8.3 Early Stop

```text
IF similarity_score > 0.9:
  stop optimization loop
```

---

## 9. Adjustment Application Rules

---

### General Formula

```python
new_value = current_value + (delta * step_scale)
```

---

### Precision

* All numeric values rounded to **2 decimal places**

---

### Delta Constraints

```text
delta ∈ [-0.5, 0.5]
```

---

## 10. Conflict Handling

If update causes violation:

* Do not resolve here
* Defer to Style Engine

---

## 11. Meta Tracking

---

### Frozen Fields

```json
"frozen_fields": ["color.saturation"]
```

---

### Applied Adjustments

```json
"applied_adjustments": {
  "color.saturation": -0.1
}
```

---

## 12. Determinism Guarantee

```text
optimize_style(x) must always produce identical output
```

---

## 13. Validation Rules

---

### Test 1: Determinism

Same input → same output

---

### Test 2: Bounds Safety

All updated values must remain in valid ranges

---

### Test 3: Lock Respect

Locked fields must remain unchanged

---

### Test 4: Convergence

Repeated runs must not oscillate indefinitely

---

## 14. Example

### Input

```json
{
  "current_style": {
    "color": {
      "saturation": 0.6
    }
  },
  "evaluation": {
    "adjustments": {
      "color.saturation": -0.2
    }
  }
}
```

---

### Process

```text
delta = -0.2
scaled = -0.1
new_value = 0.5
```

---

### Output

```json
{
  "new_style": {
    "color": {
      "saturation": 0.5
    }
  },
  "changes": [
    "color.saturation: -0.1"
  ]
}
```

---

## 15. Core Principle

```text
Optimizer performs controlled, incremental parameter search.
```

---
