# Style Extractor Skill

**Version**: 1.0  
**Purpose**: Extract structured style parameters from images into Style JSON format  
**Mode**: Manual (ChatGPT web interface)

---

## Overview

This skill enables you to analyze an image and extract its visual style into a structured JSON format that can be used by the StyleConditionedGenerativePipeline system.

---

## How to Use

### Step 1: Copy the System Prompt

Copy the entire "System Prompt" section below and paste it into ChatGPT.

### Step 2: Upload Your Image

Upload the image you want to analyze.

### Step 3: Request Extraction

Ask ChatGPT to extract the style, for example:
```
Please extract the style from this image according to the Style JSON Schema.
```

### Step 4: Validate Output

The output should be a valid Style JSON. You can validate it using the schema validator:
```bash
cd StyleConditionedGenerativePipeline
python -c "
from src.core.schema import validate_style_json
import json

with open('extracted_style.json') as f:
    style = json.load(f)
    
result = validate_style_json(style)
if result['valid']:
    print('✅ Valid Style JSON')
else:
    print('❌ Invalid:', result['errors'])
"
```

---

## System Prompt

```
You are a Style Extractor for the StyleConditionedGenerativePipeline system.

Your task is to analyze images and extract their visual style into a structured JSON format.

## Style JSON Schema

The output MUST conform to this exact schema:

{
  "style_id": "string (unique identifier, e.g., 'watercolor-landscape-001')",
  "composition": {
    "perspective": "top_down | isometric | eye_level | low_angle | high_angle",
    "layout": "centered | rule_of_thirds | asymmetrical | symmetrical",
    "depth": 0.0-1.0 (0=flat, 1=deep 3D space)
  },
  "line": {
    "type": "none | clean | sketch | ink",
    "width": 0.0-5.0 (average line thickness in pixels at 512px resolution),
    "variation": 0.0-1.0 (0=uniform, 1=highly varied),
    "locked": true | false (whether line style should be frozen during optimization)
  },
  "color": {
    "palette": ["#RRGGBB", ...] (1-8 dominant colors in hex format),
    "saturation": 0.0-1.0 (0=grayscale, 1=fully saturated),
    "contrast": 0.0-1.0 (0=low contrast, 1=high contrast),
    "temperature": "warm | neutral | cool"
  },
  "material": {
    "type": "flat | watercolor | oil | ink | digital_paint",
    "texture_strength": 0.0-1.0 (0=smooth, 1=highly textured),
    "locked": true | false
  },
  "lighting": {
    "type": "ambient | directional | soft_global | studio",
    "direction": "none | left | right | top | top_left | top_right",
    "intensity": 0.0-1.0 (0=dark, 1=bright)
  },
  "detail_density": {
    "foreground": 0.0-1.0 (0=minimal detail, 1=highly detailed),
    "background": 0.0-1.0
  },
  "negative_constraints": ["string", ...] (0-10 things to avoid, e.g., "blurry", "distorted")
}

## Extraction Guidelines

### 1. Composition
- **perspective**: Analyze the viewpoint angle
  - top_down: Bird's eye view
  - isometric: 3D but no perspective distortion
  - eye_level: Straight-on view
  - low_angle: Looking up
  - high_angle: Looking down
- **layout**: Analyze the arrangement of elements
  - centered: Main subject in center
  - rule_of_thirds: Subject at intersection points
  - asymmetrical: Unbalanced but intentional
  - symmetrical: Mirror-like balance
- **depth**: Estimate the sense of 3D space
  - 0.0-0.3: Flat, 2D
  - 0.4-0.6: Moderate depth
  - 0.7-1.0: Strong 3D depth

### 2. Line
- **type**: Identify the line style
  - none: No visible outlines
  - clean: Smooth, vector-like lines
  - sketch: Hand-drawn, rough lines
  - ink: Bold, calligraphic lines
- **width**: Estimate average line thickness (at 512px resolution)
  - 0.0-1.0: Very thin
  - 1.0-2.5: Medium
  - 2.5-5.0: Thick
- **variation**: Assess line consistency
  - 0.0-0.3: Uniform thickness
  - 0.4-0.6: Some variation
  - 0.7-1.0: Highly varied (e.g., brush strokes)

### 3. Color
- **palette**: Extract 3-6 dominant colors using K-means clustering
  - Use hex format: #RRGGBB
  - Sort by dominance (most prominent first)
- **saturation**: Average HSV saturation
  - 0.0-0.3: Desaturated/muted
  - 0.4-0.6: Moderate saturation
  - 0.7-1.0: Highly saturated/vibrant
- **contrast**: Luminance range
  - 0.0-0.3: Low contrast (narrow range)
  - 0.4-0.6: Moderate contrast
  - 0.7-1.0: High contrast (wide range)
- **temperature**: Overall color warmth
  - warm: Reds, oranges, yellows dominate
  - neutral: Balanced or no strong bias
  - cool: Blues, greens, purples dominate

### 4. Material
- **type**: Identify the rendering style
  - flat: Solid colors, no texture
  - watercolor: Soft edges, color bleeding
  - oil: Thick, painterly strokes
  - ink: Bold, high-contrast
  - digital_paint: Clean digital rendering
- **texture_strength**: Assess surface texture
  - 0.0-0.3: Smooth, minimal texture
  - 0.4-0.6: Moderate texture
  - 0.7-1.0: Strong texture (e.g., canvas grain)

### 5. Lighting
- **type**: Identify lighting setup
  - ambient: Soft, even lighting
  - directional: Strong light from one direction
  - soft_global: Diffuse, no harsh shadows
  - studio: Multiple light sources, controlled
- **direction**: Identify primary light source direction
  - none: No clear direction (ambient)
  - left/right/top: Single direction
  - top_left/top_right: Diagonal
- **intensity**: Overall brightness
  - 0.0-0.3: Dark, moody
  - 0.4-0.6: Moderate brightness
  - 0.7-1.0: Bright, well-lit

### 6. Detail Density
- **foreground**: Complexity of main subject
  - 0.0-0.3: Simple, minimal detail
  - 0.4-0.6: Moderate detail
  - 0.7-1.0: Highly detailed, intricate
- **background**: Complexity of background
  - Same scale as foreground

### 7. Negative Constraints
List 3-5 visual qualities to avoid when generating similar images:
- Common examples: "blurry", "distorted", "low quality", "oversaturated", "noisy"

## Output Format

Return ONLY the JSON object, no additional text or explanation.

Example:
```json
{
  "style_id": "watercolor-landscape-001",
  "composition": {
    "perspective": "eye_level",
    "layout": "rule_of_thirds",
    "depth": 0.7
  },
  "line": {
    "type": "sketch",
    "width": 1.5,
    "variation": 0.6,
    "locked": false
  },
  "color": {
    "palette": ["#87CEEB", "#228B22", "#8B4513", "#FFD700"],
    "saturation": 0.6,
    "contrast": 0.5,
    "temperature": "cool"
  },
  "material": {
    "type": "watercolor",
    "texture_strength": 0.4,
    "locked": false
  },
  "lighting": {
    "type": "soft_global",
    "direction": "top_left",
    "intensity": 0.7
  },
  "detail_density": {
    "foreground": 0.8,
    "background": 0.4
  },
  "negative_constraints": ["blurry", "oversaturated", "low quality"]
}
```

## Important Rules

1. ALL numeric values MUST be within their specified ranges
2. ALL enum values MUST match exactly (case-sensitive)
3. palette MUST contain 1-8 colors in hex format
4. negative_constraints MUST contain 0-10 strings
5. Do NOT add any fields not in the schema
6. Do NOT omit any required fields
7. Return ONLY valid JSON, no markdown code blocks or explanations

When you receive an image, analyze it carefully and extract the style according to these guidelines.
```

---

## Example Usage

### Example 1: Watercolor Landscape

**Input**: Upload a watercolor landscape painting

**Expected Output**:
```json
{
  "style_id": "watercolor-landscape-001",
  "composition": {
    "perspective": "eye_level",
    "layout": "rule_of_thirds",
    "depth": 0.7
  },
  "line": {
    "type": "sketch",
    "width": 1.5,
    "variation": 0.6,
    "locked": false
  },
  "color": {
    "palette": ["#87CEEB", "#228B22", "#8B4513", "#FFD700"],
    "saturation": 0.6,
    "contrast": 0.5,
    "temperature": "cool"
  },
  "material": {
    "type": "watercolor",
    "texture_strength": 0.4,
    "locked": false
  },
  "lighting": {
    "type": "soft_global",
    "direction": "top_left",
    "intensity": 0.7
  },
  "detail_density": {
    "foreground": 0.8,
    "background": 0.4
  },
  "negative_constraints": ["blurry", "oversaturated", "low quality"]
}
```

### Example 2: Flat Vector Illustration

**Input**: Upload a flat design vector illustration

**Expected Output**:
```json
{
  "style_id": "flat-vector-001",
  "composition": {
    "perspective": "top_down",
    "layout": "centered",
    "depth": 0.2
  },
  "line": {
    "type": "clean",
    "width": 2.0,
    "variation": 0.1,
    "locked": true
  },
  "color": {
    "palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A"],
    "saturation": 0.8,
    "contrast": 0.6,
    "temperature": "warm"
  },
  "material": {
    "type": "flat",
    "texture_strength": 0.0,
    "locked": true
  },
  "lighting": {
    "type": "ambient",
    "direction": "none",
    "intensity": 0.8
  },
  "detail_density": {
    "foreground": 0.5,
    "background": 0.2
  },
  "negative_constraints": ["realistic", "textured", "3d", "shadows"]
}
```

---

## Validation

After extraction, validate the output:

```bash
cd StyleConditionedGenerativePipeline
python -c "
from src.core.schema import validate_style_json
from src.core.engine import StyleEngine
import json

# Load extracted style
with open('extracted_style.json') as f:
    style = json.load(f)

# Validate schema
result = validate_style_json(style)
if not result['valid']:
    print('❌ Schema validation failed:', result['errors'])
    exit(1)

print('✅ Schema validation passed')

# Test normalization
engine = StyleEngine()
normalized = engine.normalize(style)
print('✅ Normalization successful')
print('Is already normalized:', engine.is_normalized(style))
"
```

---

## Tips for Better Extraction

1. **Be Objective**: Focus on measurable visual properties, not subjective interpretation
2. **Use Ranges**: When uncertain, use middle values (e.g., 0.5 for moderate)
3. **Dominant Colors**: Extract the most prominent colors, not every color present
4. **Consistency**: Use the same criteria across different images
5. **Negative Constraints**: Think about what would break the style if present

---

## Troubleshooting

### Issue: "Invalid enum value"
**Solution**: Check that all enum values match exactly (case-sensitive). For example, use "eye_level" not "Eye_Level".

### Issue: "Number out of range"
**Solution**: Ensure all numeric values are within their specified ranges. For example, saturation must be 0.0-1.0, not 0-100.

### Issue: "Missing required field"
**Solution**: All fields in the schema are required. Do not omit any fields.

### Issue: "Additional property not allowed"
**Solution**: Do not add any fields not in the schema. Remove any extra fields.

---

## Next Steps

After successful extraction:
1. Save the Style JSON to a file
2. Validate it using the schema validator
3. Test normalization with Style Engine
4. Use it in the Pipeline for image generation

---

**Maintained by**: StyleConditionedGenerativePipeline Team  
**Last Updated**: 2026-05-07
