# Prompt Generator Deep Specification v1.0

---

## 1. Module Definition

**Module Name:** Prompt Generator
**Type:** Deterministic Compiler

### Purpose

Convert normalized Style JSON into a fixed-format text prompt.

---

## 2. Function Signature

```python
def generate_prompt(style: dict, content: str) -> str
```

---

## 3. Output Structure (Strict)

The output MUST follow exactly this structure:

```
{CONTENT},

{COMPOSITION},
{LINE},
{COLOR},
{MATERIAL},
{LIGHTING},
{DETAIL},

style consistency, unified visual language

--negative:
{NEGATIVE}
```

---

## 4. Global Rules

* Deterministic output (same input → identical string)
* No free text generation
* All phrases must come from mapping rules
* Fixed ordering (no reordering allowed)
* No synonyms allowed
* No omitted commas except last line in block
* No trailing spaces

---

## 5. Section Ordering (Strict)

```
composition → line → color → material → lighting → detail
```

---

## 6. Numeric Formatting

* All numeric values must be rounded to **1 decimal place (round half up)**

Example:

```
1.26 → 1.3
1.24 → 1.2
```

---

## 7. Field Mapping Rules

---

### 7.1 Composition

#### perspective

```
top_down → top-down view
isometric → isometric view
eye_level → eye-level view
low_angle → low angle view
high_angle → high angle view
```

#### layout

```
centered → centered composition
rule_of_thirds → rule of thirds composition
symmetrical → symmetrical composition
asymmetrical → asymmetrical composition
```

#### depth

```
0.0 ≤ x < 0.3 → flat depth
0.3 ≤ x < 0.7 → moderate depth
0.7 ≤ x ≤ 1.0 → strong depth
```

---

### 7.2 Line

#### type

```
none → no visible linework
clean → clean lineart
sketch → sketchy lines
ink → ink linework
```

#### width

```
→ line weight {value}
```

(value must be formatted to 1 decimal place)

#### variation

```
0.0 ≤ x < 0.3 → uniform lines
0.3 ≤ x < 0.7 → slight line variation
0.7 ≤ x ≤ 1.0 → high line variation
```

---

### 7.3 Color

#### palette

```
color palette: {comma-separated list}
```

* Preserve order
* Lowercase only
* No trailing comma

---

#### saturation

```
0.0 ≤ x < 0.3 → low saturation
0.3 ≤ x < 0.7 → moderate saturation
0.7 ≤ x ≤ 1.0 → high saturation
```

---

#### contrast

```
0.0 ≤ x < 0.3 → low contrast
0.3 ≤ x < 0.7 → moderate contrast
0.7 ≤ x ≤ 1.0 → high contrast
```

---

#### temperature

```
warm → warm color tone
cool → cool color tone
neutral → neutral color tone
```

---

### 7.4 Material

#### type

```
flat → flat color rendering
watercolor → watercolor rendering
oil → oil painting style
ink → ink illustration
digital_paint → digital painting
```

---

#### texture_strength

```
0.0 ≤ x < 0.3 → minimal texture
0.3 ≤ x < 0.7 → visible texture
0.7 ≤ x ≤ 1.0 → strong texture
```

---

### 7.5 Lighting

#### type

```
ambient → ambient lighting
directional → directional lighting
soft_global → soft global illumination
studio → studio lighting
```

---

#### direction

```
none → (omit field)
left → light from left
right → light from right
top → top lighting
top_left → light from top-left
top_right → light from top-right
```

---

#### intensity

```
0.0 ≤ x < 0.3 → very soft lighting
0.3 ≤ x < 0.7 → moderate lighting
0.7 ≤ x ≤ 1.0 → strong lighting
```

---

### 7.6 Detail Density

#### foreground

```
0.0 ≤ x < 0.3 → minimal foreground detail
0.3 ≤ x < 0.7 → moderate foreground detail
0.7 ≤ x ≤ 1.0 → high foreground detail
```

---

#### background

Same mapping as foreground.

---

### 7.7 Negative Constraints

```
{constraint1}, {constraint2}, ...
```

* Must preserve order
* Lowercase
* Comma-separated
* No trailing comma

---

## 8. Omission Rules

* If a field produces empty string → omit it
* Do NOT leave empty commas

Example:

```
ambient lighting, very soft lighting
```

(not:)

```
ambient lighting, , very soft lighting
```

---

## 9. Formatting Rules

* Each block is comma-separated
* Each line ends with comma except:

  * last line before empty line
* One blank line before style consistency line
* One blank line before --negative block

---

## 10. Changes Forbidden

```
- Do not reorder phrases
- Do not introduce synonyms
- Do not merge fields
- Do not split fields
- Do not infer missing content
```

---

## 11. Determinism Guarantee

Given identical input:

```
generate_prompt(x) MUST always return identical string
```

---

## 12. Validation Rules

### Test 1: Determinism

Same input → identical output string

---

### Test 2: Structural Integrity

Output must contain:

* CONTENT line
* 6 style lines
* style consistency line
* negative block

---

### Test 3: No Drift

Repeated generation must not change wording

---

## 13. Example

### Input

(See JSON example in system spec)

---

### Output

```
cozy rooftop terrace scene,

isometric view, centered composition, moderate depth,
clean lineart, line weight 1.2, uniform lines,
color palette: beige, olive, brown, moderate saturation, moderate contrast, warm color tone,
watercolor rendering, visible texture,
soft global illumination, light from top-left, very soft lighting,
high foreground detail, moderate background detail,

style consistency, unified visual language

--negative:
no photorealism, no harsh shadows
```

---

## 14. Core Principle

```
Prompt Generator is a compiler, not a writer.
```

---
