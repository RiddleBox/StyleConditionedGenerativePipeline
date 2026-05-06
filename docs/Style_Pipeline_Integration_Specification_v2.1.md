# Style Pipeline Integration Specification v1.2.1 (Final – Fixed)

---

## 1. Module Definition

**Module Name:** Style Pipeline Orchestrator
**Type:** Deterministic Execution Controller

---

### Purpose

Coordinate all modules into a complete system that supports:

1. **Style Learning Mode**

   - Extract style from an input image
   - Convert it into a normalized Style JSON
   - Iteratively optimize generation parameters

   🎯 Objective:
   Minimize the difference between generated images and the extracted reference style.

   The reference style is defined as:
   → the normalized Style JSON produced by Extractor + Style Engine

   This reference MUST remain fixed throughout the optimization loop.

2. **Style Production Mode**

   - Load a predefined style from Style Library
   - Generate images deterministically without optimization

   🎯 Objective:
   Faithfully reproduce the given style without modification
---

## 2. System Architecture Overview

---

### 2.1 Entry Topology

```text
                ┌──────────────┐
                │   image      │
                └──────┬───────┘
                       ↓
                  [Extractor]
                       ↓
                Raw Style JSON
                       ↓
                  [Style Engine]
                       ↓
             Normalized Style JSON
                       ↓
                       │
                       ▼
                 (Shared Core)
                       ▲
                       │
             [Style Library]
                       ▲
                       │
                  style_id input
```

---

### 2.2 Full Execution Flow (CRITICAL – Learning Mode)

```text
INPUT IMAGE
  ↓
[Extractor]
  ↓
Raw Style JSON
  ↓
[Style Engine]
  ↓
Normalized Style JSON
  ↓
[Prompt Generator]
  ↓
Prompt
  ↓
[Image Generator]
  ↓
Generated Image
  ↓
[Evaluator]
  ↓
Evaluation Result
  ↓
[Optimizer]
  ↓
Updated Style JSON
  ↓
[Style Engine]
  ↓
(loop)
```

---

### 2.3 Core Loop (Abstract)

```text
Style JSON
  ↓
Generate → Image → Evaluate → Optimize → Normalize → loop
```

---

### 2.4 Production Flow (No Loop)

```text
Style Library
  ↓
[Style Engine]
  ↓
Normalized Style JSON
  ↓
[Prompt Generator]
  ↓
Prompt
  ↓
[Image Generator]
  ↓
Generated Image
```

---

## 3. Pipeline Modes (STRICT)

---

### Mode A: Learning Mode

#### Input

```json
{
  "mode": "learning",
  "image": "string",
  "content": "string"
}
```

---

### Mode B: Production Mode

#### Input

```json
{
  "mode": "production",
  "style_id": "string",
  "version": "string",
  "content": "string"
}
```

---

### Content Requirement (CRITICAL)

```text
content MUST be explicitly provided in ALL modes.
Empty or missing content → INVALID INPUT
```

---

## 4. Core Function

```python
def run_style_pipeline(input: dict) -> dict
```

---

## 5. Configuration

```json
{
  "max_iterations": 5,
  "target_score": 0.9,
  "retry_limit": 3,
  "step_scale": 0.5,
  "enable_stability_sampling": false
}
```

---

## 6. Execution Flow (STRICT)

---

## 6.1 Mode Dispatch

```python
if input["mode"] == "learning":
    return run_learning_mode(input)

elif input["mode"] == "production":
    return run_production_mode(input)

else:
    raise Error("INVALID_MODE")
```

---

## 6.2 Learning Mode Implementation

---

### Step 1: Extract Style (with optional stability)
```python

if enable_stability_sampling:
    raw_style = extract_with_stability(input["image"])
else:
    raw_style = extract_style(input["image"])
```

### Step 1.1: Stability Extraction Module
```python
def extract_with_stability(image):
    results = []

    for i in range(3):
        result = extract_style(image)
        if validate_schema(result):
            results.append(result)

    if len(results) == 0:
        return None

    return aggregate(results)

```
aggregation MUST be deterministic:
- numeric fields → mean
- enum fields → majority vote
- palette → union (max 8)
- negative_constraints → union (max 5)

---

### Step 2: Schema Validation (CRITICAL)

```python
if raw_style is None or not validate_schema(raw_style):
    retry extractor up to retry_limit
    if still invalid:
        abort pipeline
```

---

### Step 3: Normalize

```python
reference_style = style_engine(raw_style)  # FIXED reference style
```
Reference Invariant:
reference_style defines the fixed optimization target space

It MUST:
- be computed exactly once
- never change during iteration
- NEVER be optimized directly
---

### Step 3.1: Global Optimization Objective (Single Source of Truth)

Objective:

maximize similarity(generated_image, reference_style)

Formal definition:

evaluation := evaluate_style(...)
score := evaluation["similarity_score"]
maximize(score)

Evaluation Contract
evaluate_style MUST internally approximate similarity between:
generated_image ↔ reference_style

---

### Step 4: Initialize

```python
current_style = reference_style
iteration = 0
history = []
best_score = 0.0
```

---

### Step 5: Iteration Loop

```python
while iteration < max_iterations:
```

---

#### 5.1 Generate Prompt

```python
prompt = generate_prompt(current_style, input["content"])
```

---

#### 5.2 Generate Image

```python
generated_image = generate_image(prompt)
```

---

#### 5.3 Evaluate

```python
evaluation = evaluate_style(
    reference_style=reference_style,
    generated_image=generated_image,
    original_image=input["image"]
)

score = evaluation["similarity_score"]
```

---

#### 5.4 Record History

```python
history.append({
    "iteration": iteration,
    "score": score,
    "prompt": prompt,
    "adjustments": evaluation.get("adjustments", {})    
})
```
Adjustments Contract 
adjustments = deterministic optimization trace metadata only

Allowed fields (optional):
- style_delta
- prompt_delta
- weight_delta
---

#### 5.5 Track Best

```python
if score > best_score:
    best_score = score
```

---

#### 5.6 Early Stop

```python
if score >= target_score:
    break
```

---

#### 5.7 Optimize

```python
result = optimize_style(
    current_style=current_style,
    evaluation=score,
    iteration=iteration,
    history=history
)
```

---

#### 5.8 Update Style

```python
previous_style = current_style

candidate_style = style_engine(result["new_style"])

if validate_schema(candidate_style):
    current_style = candidate_style
else:
    current_style = previous_style
```

---

#### 5.9 Increment

```python
iteration += 1
```

---

### Step 6: Final Generation

```python
final_prompt = generate_prompt(current_style, input["content"])
final_image = generate_image(final_prompt)
```

---

## 6.3 Production Mode Implementation

---

### Step 1: Load Style

```json
{
  "style_id": "xxx",
  "version": "v1.0"
}
```

```python
style = style_library.get_style(
    style_id=input["style_id"],
    version=input["version"]
)
```

---

### Step 2: Schema Validation

```python
if not validate_schema(style):
    raise Error("INVALID_STYLE")
```

---

### Step 3: Normalize

```python
current_style = style_engine(style)
```

---

### Step 4: Generate Prompt

```python
final_prompt = generate_prompt(current_style, input["content"])
```

---

### Step 5: Generate Image

```python
final_image = generate_image(final_prompt)
```

---

## 6.4 Reference Style Invariant (CRITICAL)

In Learning Mode:

- reference_style MUST be defined once after initial normalization
- reference_style MUST NOT change during iterations

All evaluations MUST compare generated images against this fixed reference_style
---

## 7. Final Output (Unified)


```json
{
  "final_style": {},
  "final_prompt": "",
  "final_image": "",
  "final_score": 0.0,
  "history": []
}
```
learning mode → final_score = best_score
production mode → final_score = null

---

## 8. Error Handling

---

### Extractor Failure

* Retry up to retry_limit
* Fail → abort pipeline

---

### Schema Failure

```text
Reject invalid JSON → retry extractor
```

---

### Style Not Found

```json
{
  "error": "STYLE_NOT_FOUND"
}
```

---

### Generator Failure

* Retry once
* If fail → return last valid state

---

### Evaluator Failure

* Abort iteration
* Return last valid state

---

## 9. Stability Mode

```text
If enabled:

- Run extractor multiple times
- Average numeric values
- Majority vote enum fields

Purpose:
Improve consistency and reduce randomness
```

---

## 10. Determinism Rules

* Same input → same output (within tolerance)
* Numeric tolerance: ±0.02
* Enum must match exactly
* No randomness allowed in pipeline logic

---

## 11. Logging Contract

```json
{
  "pipeline_id": "string",
  "mode": "learning | production",
  "iterations": [
    {
      "iteration": 0,
      "prompt": "",
      "score": 0.0,
      "adjustments": {}
    }
  ],
  "final_score": 0.0
}
```
iterations MUST mirror history entries from the pipeline execution
---

## 12. Invariants

* Style must always pass schema validation
* Style must always be normalized before generation
* Locked fields must never change
* Values must remain within valid ranges

---

## 13. Forbidden Behavior

* Mixing learning and production logic
* Skipping Style Engine
* Running optimizer in production mode
* Using raw extractor output directly
* Generating image without normalized style

---

## 14. Loop Termination Conditions

```text
- iteration >= max_iterations
- similarity_score >= target_score
```

---

## 15. System Principle (Final)

```text
The system is a deterministic dual-mode pipeline:

1. Style Learning:
   Closed-loop optimization over a fixed parameter space

2. Style Production:
   Deterministic generation from validated style presets

Both operate on a shared Style JSON representation
```

---
