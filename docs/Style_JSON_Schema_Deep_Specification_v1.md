# Style JSON Schema Deep Specification v1.0

---

## 1. Module Definition

**Module Name:** Style Schema
**Type:** Structural Contract (Strict Validation Layer)

### Purpose

Define the canonical intermediate representation (IR) for all style-related processing.

---

## 2. JSON Schema (Machine Validation)

```json id="schema_final_v1"
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "style_id",
    "composition",
    "line",
    "color",
    "material",
    "lighting",
    "detail_density",
    "negative_constraints"
  ],
  "properties": {
    "style_id": {
      "type": "string",
      "minLength": 1
    },
    "composition": {
      "type": "object",
      "additionalProperties": false,
      "required": ["perspective", "layout", "depth"],
      "properties": {
        "perspective": {
          "type": "string",
          "enum": ["top_down", "isometric", "eye_level", "low_angle", "high_angle"]
        },
        "layout": {
          "type": "string",
          "enum": ["centered", "rule_of_thirds", "asymmetrical", "symmetrical"]
        },
        "depth": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        }
      }
    },
    "line": {
      "type": "object",
      "additionalProperties": false,
      "required": ["type", "width", "variation"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["none", "clean", "sketch", "ink"]
        },
        "width": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 5.0
        },
        "variation": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "locked": {
          "type": "boolean",
          "default": false
        }
      }
    },
    "color": {
      "type": "object",
      "additionalProperties": false,
      "required": ["palette", "saturation", "contrast", "temperature"],
      "properties": {
        "palette": {
          "type": "array",
          "minItems": 1,
          "maxItems": 8,
          "uniqueItems": true,
          "items": {
            "type": "string",
            "minLength": 1
          }
        },
        "saturation": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "contrast": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "temperature": {
          "type": "string",
          "enum": ["warm", "neutral", "cool"]
        }
      }
    },
    "material": {
      "type": "object",
      "additionalProperties": false,
      "required": ["type", "texture_strength"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["flat", "watercolor", "oil", "ink", "digital_paint"]
        },
        "texture_strength": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "locked": {
          "type": "boolean",
          "default": false
        }
      }
    },
    "lighting": {
      "type": "object",
      "additionalProperties": false,
      "required": ["type", "direction", "intensity"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["ambient", "directional", "soft_global", "studio"]
        },
        "direction": {
          "type": "string",
          "enum": ["none", "left", "right", "top", "top_left", "top_right"]
        },
        "intensity": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        }
      }
    },
    "detail_density": {
      "type": "object",
      "additionalProperties": false,
      "required": ["foreground", "background"],
      "properties": {
        "foreground": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "background": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        }
      }
    },
    "negative_constraints": {
      "type": "array",
      "minItems": 0,
      "maxItems": 10,
      "items": {
        "type": "string",
        "minLength": 1
      }
    }
  }
}
```

---

## 3. Global Structural Rules

* `additionalProperties = false` at all levels
* All required fields MUST exist
* No implicit defaults at schema level (handled by Style Engine)
* All numbers MUST be finite (no NaN / Infinity)

---

## 4. Numeric Conventions

* All normalized numeric fields ∈ [0.0, 1.0]
* Exception: `line.width ∈ [0.0, 5.0]`
* Precision requirement:

```text
All numeric values must support up to 2 decimal places
```

---

## 5. Semantic Boundaries (Critical)

Fields MUST NOT overlap in meaning:

```text
composition → spatial structure only
line → contour representation only
color → chromatic properties only
material → rendering method only
lighting → illumination only
detail_density → complexity only
```

---

## 6. Enum Contract (Closed Vocabulary)

No extension allowed in v1.0.

---

### composition.perspective

```text
top_down | isometric | eye_level | low_angle | high_angle
```

---

### composition.layout

```text
centered | rule_of_thirds | symmetrical | asymmetrical
```

---

### line.type

```text
none | clean | sketch | ink
```

---

### material.type

```text
flat | watercolor | oil | ink | digital_paint
```

---

### lighting.type

```text
ambient | directional | soft_global | studio
```

---

### lighting.direction

```text
none | left | right | top | top_left | top_right
```

---

### color.temperature

```text
warm | neutral | cool
```

---

## 7. Locked Field Semantics

* `locked = true` means:

  * Cannot be modified by Style Engine
  * Cannot be modified by Optimizer
* Only Extractor may set locked fields

---

## 8. Negative Constraints Rules

* Order must be preserved
* Strings must be lowercase (enforced later)
* No semantic validation at schema level

---

## 9. Golden Sample (Reference)

```json id="schema_golden"
{
  "style_id": "arch_watercolor_v1",
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
    "palette": ["beige", "olive", "brown"],
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
    "no harsh shadows",
    "no high contrast"
  ]
}
```

---

## 10. Validation Requirements

### Test 1: Structural Validity

* Must pass JSON Schema validator

---

### Test 2: Deterministic Parsing

* Same JSON → identical parsed structure

---

### Test 3: Pipeline Compatibility

* Must be accepted by:

  * Style Engine
  * Prompt Generator
  * Evaluator
  * Optimizer

---

## 11. Forbidden Cases

```text
- Missing required fields
- Unknown enum values
- Additional unexpected fields
- Invalid numeric ranges
- Empty palette
```

---

## 12. Core Principle

```text
Style JSON is a strictly typed intermediate representation (IR), not descriptive data.
```

---
