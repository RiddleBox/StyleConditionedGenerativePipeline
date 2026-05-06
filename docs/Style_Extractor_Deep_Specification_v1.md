# Style Extractor Deep Specification v1.0

---

## 1. Module Definition

**Module Name:** Style Extractor
**Type:** Deterministic Perception-to-IR Converter

### Purpose

Convert an input image into a strictly structured Style JSON (v1.0),
serving as the only entry point from visual data into the style parameter space.

---

## 2. Function Signature

```python
def extract_style(image: Any) -> dict
```

---

## 3. System Prompt (Strict)

```text
You are a Style Extractor.

Your task is to convert an input image into a strictly structured Style JSON.

You MUST follow the exact JSON Schema provided. No deviation is allowed.

---

## Core Rules

1. Output ONLY valid JSON.
   - No explanations
   - No comments
   - No extra text

2. Follow the schema EXACTLY:
   - Do not add new fields
   - Do not remove required fields
   - All fields must exist

3. Use ONLY allowed enum values.
   - If uncertain, choose the closest valid enum
   - Do NOT invent new terms

4. All numeric values must be normalized:
   - Range: 0 to 1 (except line.width: 0–5)
   - No percentages
   - No vague words

5. Be deterministic:
   - Same image → nearly identical JSON
   - Avoid randomness

6. No subjective language:
   - Forbidden: aesthetic descriptions
   - Only measurable or categorical attributes

---

## Field Interpretation Rules

- composition.depth:
  0 = flat
  1 = strong depth

- line.variation:
  0 = uniform
  1 = highly variable

- color.saturation:
  0 = grayscale
  1 = highly saturated

- color.contrast:
  0 = flat
  1 = high contrast

- material.texture_strength:
  0 = no texture
  1 = strong texture

- lighting.intensity:
  0 = soft
  1 = strong

- detail_density:
  foreground ≥ background (default assumption)

---

## Locked Fields Rule

If material or line strongly defines the style:
- Set locked = true

---

## Negative Constraints Rule

You MUST include 2–5 constraints describing what the image is NOT.

---

## Output Format

Return ONLY the Style JSON.
```

---

## 4. Wrapper API Specification

### Input

```json
{
  "image": "<image_data_or_url>",
  "task": "extract_style",
  "schema_version": "v1.0"
}
```

---

### Model Parameters

```json
{
  "temperature": 0.2,
  "top_p": 0.9,
  "max_tokens": 800
}
```

---

## 5. Execution Pipeline

```text
image
 → model inference
 → raw JSON output
 → JSON parse
 → schema validation
 → stability check (optional)
 → final Style JSON
```

---

## 6. Validation Layer (Critical)

---

### 6.1 JSON Validity

* Must be parseable
* No extra text

---

### 6.2 Schema Compliance

* Must pass Style JSON Schema v1.0
* No missing fields
* No invalid enums
* No out-of-range values

---

### 6.3 Semantic Constraints

```text
- palette length ≥ 1
- negative_constraints length ≥ 2
```

---

## 7. Determinism & Stability

---

### 7.1 Repeatability Rule

Same image, multiple runs:

```text
- enum fields: MUST match exactly
- numeric fields: tolerance ≤ ±0.05
```

---

### 7.2 Stability Enforcement (Optional Advanced)

```python
run_extractor(image, n=3)
→ average numeric fields
→ majority vote for enums
```

---

## 8. Retry Mechanism (Mandatory)

---

### Retry Conditions

```text
- invalid JSON
- schema violation
- missing fields
```

---

### Retry Policy

```python
max_retries = 3
```

---

### Fallback Strategy

```text
IF all retries fail:
  return last valid result OR raise error
```

---

## 9. Field-Level Extraction Rules

---

### Composition

* perspective inferred from camera angle
* layout inferred from subject placement
* depth inferred from perspective compression

---

### Line

* detect presence of outlines
* estimate thickness visually
* measure variation consistency

---

### Color

* palette: dominant colors only (≤8)
* saturation: global intensity
* contrast: luminance range
* temperature: dominant hue bias

---

### Material

* based on rendering style (NOT texture only)
* watercolor → soft edges, bleed
* flat → no shading

---

### Lighting

* detect directional vs ambient
* estimate intensity via shadow contrast

---

### Detail Density

* foreground: object complexity
* background: visual noise level

---

## 10. Locked Field Logic

Set locked = true when:

```text
- material defines style identity (watercolor, ink)
- line style is dominant and distinctive
```

---

## 11. Negative Constraints Generation

Rules:

* 2–5 entries
* Must be style-relevant
* Must not contradict positive attributes

Examples:

```text
no photorealism
no 3D rendering
no harsh shadows
```

---

## 12. Error Handling

---

### Hard Fail

```text
- Non-JSON output
- Schema mismatch
```

---

### Soft Fail

```text
- Slight numeric instability
→ allowed within tolerance
```

---

## 13. Validation Tests

---

### Test 1: Determinism

Run extractor 3 times:

* enum identical
* numeric deviation ≤ 0.05

---

### Test 2: Schema Integrity

Pass JSON Schema validator

---

### Test 3: Reconstruction Test

```text
image → JSON → prompt → generated image
```

Expected:

* style consistency preserved

---

### Test 4: Style Recognition

#### Case 1: Watercolor

```text
material.type = watercolor
texture_strength > 0.3
locked = true
```

#### Case 2: Flat Design

```text
material.type = flat
texture_strength ≈ 0
```

#### Case 3: Line Art

```text
line.type ≠ none
```

---

## 14. Forbidden Behavior

```text
- Adding fields not in schema
- Using natural language descriptions
- Outputting partial JSON
- Random variation
```

---

## 15. Core Principle

```text
Extractor maps perception to a fixed parameter space, not description.
```

---
