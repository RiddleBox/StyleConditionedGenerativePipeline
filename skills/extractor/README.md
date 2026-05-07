# Style Extractor - Quick Start Guide

## What is This?

A manual skill for extracting structured style parameters from images using ChatGPT.

## Quick Start (3 Steps)

### 1. Open ChatGPT
Go to https://chat.openai.com

### 2. Copy & Paste System Prompt
Open `SKILL.md` and copy the entire "System Prompt" section (starts with "You are a Style Extractor...").

Paste it into ChatGPT.

### 3. Upload Image & Extract
Upload your image and say:
```
Please extract the style from this image.
```

ChatGPT will return a Style JSON.

## Validate Output

```bash
cd StyleConditionedGenerativePipeline
source venv/bin/activate

# Save ChatGPT output to extracted_style.json
python -c "
from src.core.schema import validate_style_json
import json

with open('extracted_style.json') as f:
    style = json.load(f)
    
result = validate_style_json(style)
print('Valid:', result['valid'])
if not result['valid']:
    print('Errors:', result['errors'])
"
```

## What You Get

A structured JSON describing:
- **Composition**: Perspective, layout, depth
- **Line**: Type, width, variation
- **Color**: Palette, saturation, contrast, temperature
- **Material**: Type, texture strength
- **Lighting**: Type, direction, intensity
- **Detail Density**: Foreground/background complexity
- **Negative Constraints**: Things to avoid

## Example

**Input**: Watercolor landscape image

**Output**:
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

## Next Steps

After extraction:
1. Validate with schema validator
2. Normalize with Style Engine
3. Generate prompts with Prompt Generator
4. Use in image generation pipeline

## Need Help?

See `SKILL.md` for detailed guidelines and troubleshooting.
