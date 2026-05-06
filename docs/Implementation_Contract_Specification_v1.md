# Implementation Contract Specification v1.0

---

## 1. Purpose

Define strict implementation-level contracts for all modules in the Style Pipeline system.

This document ensures:

* All modules communicate with identical data formats
* No ambiguity in inputs / outputs
* Deterministic and reproducible behavior

---

## 2. Global Data Types

---

### 2.1 Image Type

```json id="img_type"
{
  "type": "string",
  "description": "Image input must be either base64 string or URL"
}
```

---

### 2.2 Style JSON

Must strictly conform to:

```text id="style_ref"
Style JSON Schema v1.0
```

---

### 2.3 Prompt Type

```json id="prompt_type"
{
  "type": "string"
}
```

---

### 2.4 Generated Image Output

```json id="gen_img"
{
  "image": "string (base64 or URL)",
  "metadata": {
    "model": "string",
    "seed": "number"
  }
}
```

---

## 3. Module Interface Contracts

---

## 3.1 Extractor

### Input

```json id="ext_in"
{
  "image": "string"
}
```

---

### Output

```json id="ext_out"
{
  "style": {Style JSON}
}
```

---

### Errors

```json id="ext_err"
{
  "error": "INVALID_JSON | SCHEMA_VIOLATION | EXTRACTION_FAILED"
}
```

---

## 3.2 Style Engine

### Input

```json id="eng_in"
{
  "style": {Style JSON},
  "mode": "strict"
}
```

---

### Output

```json id="eng_out"
{
  "normalized_style": {Style JSON},
  "changes": ["string"],
  "warnings": ["string"]
}
```

---

## 3.3 Prompt Generator

### Input

```json id="pg_in"
{
  "style": {Style JSON},
  "content": "string"
}
```

---

### Output

```json id="pg_out"
{
  "prompt": "string"
}
```

---

## 3.4 Image Generator

### Input

```json id="ig_in"
{
  "prompt": "string",
  "seed": "number (optional)"
}
```

---

### Output

```json id="ig_out"
{
  "image": "string",
  "metadata": {
    "seed": "number",
    "model": "string"
  }
}
```

---

## 3.5 Evaluator

### Input

```json id="eval_in"
{
  "reference_style": {Style JSON},
  "generated_image": "string",
  "original_image": "string"
}
```

---

### Output

```json id="eval_out"
{
  "similarity_score": 0.0,
  "dimension_scores": {},
  "deviations": [],
  "adjustments": {}
}
```

---

## 3.6 Optimizer

### Input

```json id="opt_in"
{
  "current_style": {Style JSON},
  "evaluation": {Evaluator Output},
  "iteration": 0,
  "history": []
}
```

---

### Output

```json id="opt_out"
{
  "new_style": {Style JSON},
  "changes": ["string"],
  "meta": {
    "frozen_fields": [],
    "applied_adjustments": {}
  }
}
```

---

## 4. Pipeline Contract

---

### Input

```json id="pipe_in"
{
  "image": "string",
  "content": "string"
}
```

---

### Output

```json id="pipe_out"
{
  "final_style": {Style JSON},
  "final_prompt": "string",
  "final_image": "string",
  "final_score": 0.0,
  "history": [
    {
      "iteration": 0,
      "score": 0.0,
      "prompt": "string"
    }
  ]
}
```

---

## 5. Execution Order (Strict)

```text id="exec_order"
Extractor → Style Engine → Prompt Generator → Image Generator → Evaluator → Optimizer → Style Engine → loop
```

---

## 6. Retry Policy

---

### Extractor

```text id="retry_ext"
max_retries = 3
```

---

### Image Generator

```text id="retry_gen"
retry if image generation fails
```

---

### Evaluator

```text id="retry_eval"
no retry, fallback to last valid result
```

---

## 7. Error Handling Standard

---

### Unified Error Format

```json id="err_format"
{
  "module": "string",
  "error_code": "string",
  "message": "string"
}
```

---

### Fatal Errors

```text id="fatal_err"
- Extractor fails all retries
- Schema validation fails after retries
```

---

### Recoverable Errors

```text id="rec_err"
- Image generation failure
- Minor evaluation issues
```

---

## 8. Determinism Requirements

* Same input → same output (within tolerance)
* Numeric tolerance: ±0.02 (post-optimization)
* Enum values must be identical

---

## 9. Logging Contract

---

### Log Structure

```json id="log_struct"
{
  "pipeline_id": "string",
  "steps": [
    {
      "module": "extractor",
      "input": {},
      "output": {}
    }
  ]
}
```

---

## 10. Configuration Contract

```json id="config"
{
  "max_iterations": 5,
  "target_score": 0.9,
  "step_scale": 0.5,
  "retry_limit": 3
}
```

---

## 11. Environment Assumptions

* Image generator must support text prompt input
* Evaluator must support image + style comparison
* JSON Schema validator must be available

---

## 12. Forbidden Behavior

```text id="forbid"
- Passing invalid JSON between modules
- Skipping validation steps
- Modifying locked fields
- Using non-deterministic randomness
```

---

## 13. Integration Example

```python id="integration_example"
pipeline(input_image, content):
    style = extractor(image)
    style = engine(style)

    for i in range(max_iterations):
        prompt = generator(style, content)
        image = image_gen(prompt)
        eval = evaluator(style, image, input_image)

        if eval.score > target:
            break

        style = optimizer(style, eval)
        style = engine(style)

    return result
```

---

## 14. Core Principle

```text id="core_principle"
All modules must behave as pure functions with strict I/O contracts.
```

---
