# Style Engine Deep Specification v1.0

---

## 1. Module Definition

**Module Name:** Style Engine
**Type:** Deterministic Transformer

### Input

```json
{
  "style": {Style JSON v1.0},
  "mode": "strict"
}
```

### Output

```json
{
  "normalized_style": {Style JSON v1.0},
  "changes": ["string"],
  "warnings": ["string"]
}
```

---

## 2. Function Signature

```python
def normalize_style(style: dict) -> dict
```

Return structure:

```json
{
  "normalized_style": {},
  "changes": [],
  "warnings": []
}
```

---

## 3. Execution Order (Strict)

The following steps MUST be executed in order:

```
1. Schema Validate
2. Clamp
3. Canonicalize
4. Fill Defaults
5. Conflict Resolution
6. Lock Enforcement
7. Structural Fixes
8. Negative Constraints Normalize
9. Final Validation
```

---

## 4. Global Rules

* No reinterpretation of style
* No new style invention
* Only correction and normalization allowed
* Locked fields MUST NOT be modified
* All modifications MUST be recorded in `changes`
* System MUST be deterministic

---

## 5. Determinism Guarantee

Given identical input:

```
normalize_style(x) MUST always produce identical output
```

Forbidden:

* randomness
* time-based logic
* unordered iteration

---

## 6. Schema Validation

### Behavior

* If schema invalid → throw exception
* Do not continue execution

### Error

```
Exception("Invalid Style JSON")
```

---

## 7. Clamp Rules

### Ranges

```
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

### Behavior

```
if value > max → set to max
if value < min → set to min
```

### Precision

* All float values must be rounded to **2 decimal places (round half up)**

---

## 8. Canonicalization

### Palette Processing

Steps:

1. Convert to lowercase
2. Remove modifiers:

```
light, soft, pale, bright, dark, muted, slightly, very
```

3. Normalize words:

```
olive green → olive
light brown → brown
off white → white
```

4. Remove duplicates (preserve order)

### Constraints

* Must NOT introduce new colors
* Must NOT remove last remaining color

---

## 9. Default Filling

### Condition

* Field missing OR null

### Defaults

```json
{
  "lighting": {
    "type": "ambient",
    "direction": "none",
    "intensity": 0.3
  },
  "detail_density": {
    "foreground": 0.6,
    "background": 0.3
  },
  "color": {
    "saturation": 0.5,
    "contrast": 0.5
  },
  "line": {
    "variation": 0.3
  }
}
```

### Constraints

* Do not overwrite existing values
* Do not fill enum fields

---

## 10. Conflict Resolution

### Priority Order

```
1. locked fields
2. material.type
3. line.type
4. lighting.type
5. numeric fields
```

---

### Rules

#### Rule 1: Watercolor

```
IF material.type == watercolor AND contrast > 0.6:
  contrast = 0.6
  add warning
```

---

#### Rule 2: Flat Material

```
IF material.type == flat:
  texture_strength = 0.0
```

---

#### Rule 3: Line None

```
IF line.type == none:
  line.width = 0.0
  line.variation = 0.0
```

---

#### Rule 4: Ambient Lighting

```
IF lighting.type == ambient AND intensity > 0.4:
  intensity = 0.4
```

---

### Constraints

* Only modify numeric fields
* Do not modify enum fields unless invalid
* Respect lock rules

---

## 11. Lock Enforcement

### Rule

```
IF module.locked == true:
  do not modify any field under that module
```

---

### Conflict Handling

```
IF conflict involves locked field:
  modify other fields only
```

---

### Unresolvable Conflict

```
Keep original values
Add warning: "unresolved conflict"
```

---

## 12. Structural Fixes

### Detail Density

Rule:

```
foreground ≥ background
```

Fix:

```
IF background > foreground:
  background = max(0, foreground - 0.2)
```

Edge case:

```
IF foreground < 0.2:
  background = 0
```

---

## 13. Negative Constraints

### Rules

* Convert to lowercase
* Remove duplicates
* Length must be 2–5

---

### Fill

```
IF length < 2:
  add:
    "no photorealism"
    "no harsh shadows"
```

---

### Trim

```
IF length > 5:
  keep first 5
```

---

## 14. Changes Format

### Format

```
"path: old → new"
```

### Path Rules

* Dot notation
* Full path required

Examples:

```
color.saturation: 1.2 → 1.0
lighting.intensity: 0.8 → 0.4
```

---

## 15. Warnings

Triggered when:

* Conflict adjustment applied
* Conflict unresolved

---

## 16. Final Validation

### Required

```
validate_style_json(normalized_style)
```

### Failure

```
throw Exception("Normalization produced invalid schema")
```

---

## 17. Idempotency

Must satisfy:

```
normalize(normalize(x)) == normalize(x)
```

---

## 18. Forbidden Operations

```
- Modify material.type
- Modify palette content (except normalization)
- Modify composition enums
- Introduce new fields
- Introduce randomness
```

---
