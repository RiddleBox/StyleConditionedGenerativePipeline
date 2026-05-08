# StyleConditionedGenerativePipeline

A deterministic, style-conditioned image generation pipeline that extracts, optimizes, and applies visual styles.

## Features

- **Style Extraction**: Extract visual style parameters from reference images
- **Style Optimization**: Iteratively optimize styles to match reference quality
- **Multiple Modes**: Manual, Learning, Auto, and Production modes
- **Deterministic**: Same input → same output (where possible)
- **Modular**: Use individual components or complete pipelines

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Core Modules                              │
├─────────────────────────────────────────────────────────────┤
│ Schema → Engine → Prompt Generator → Style Library          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Pipeline Modes                             │
├─────────────────────────────────────────────────────────────┤
│ Manual Mode    → Generate prompts for manual use            │
│ Learning Mode  → Optimize style through iteration           │
│ Auto Mode      → Fully automated (LLM + DALL-E 3)          │
│ Production Mode→ Fast generation from library               │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone repository
git clone https://github.com/RiddleBox/StyleConditionedGenerativePipeline.git
cd StyleConditionedGenerativePipeline

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Manual Mode (No API Required)

```python
from src.pipeline.manual_mode import ManualModePipeline

# Define style
style = {
    "palette": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
    "color_temperature": "warm",
    "saturation_level": 0.75,
    # ... other parameters
}

# Generate prompt
pipeline = ManualModePipeline()
result = pipeline.generate_prompt_for_manual_use(
    style=style,
    subject="a serene landscape"
)

# Save and use in ChatGPT
pipeline.save_prompt_to_file(result, "prompt.txt")
```

### Auto Mode (Fully Automated)

```python
from src.pipeline.auto_mode import AutoModePipeline
from PIL import Image

# Set API key
import os
os.environ["OPENAI_API_KEY"] = "your-key-here"

# Load reference image
reference = Image.open("reference.jpg")

# Create pipeline
pipeline = AutoModePipeline()

# Learn from reference
result = pipeline.learn_from_reference(
    reference_image=reference,
    style_name="my_style",
    subject="abstract art",
    max_iterations=5,
    target_score=0.85
)

# Generate new images
image = pipeline.generate_from_library(
    style_name="my_style",
    subject="a cat in a garden"
)
```

## Pipeline Modes

### 1. Manual Mode
- **Use case**: Generate prompts for manual use in ChatGPT/Midjourney
- **Requirements**: None (no API needed)
- **Workflow**: Style JSON → Prompt → Manual generation

### 2. Learning Mode
- **Use case**: Optimize style through iterative refinement
- **Requirements**: Manual image generation per iteration
- **Workflow**: Initial style → Generate → Evaluate → Optimize → Repeat

### 3. Auto Mode
- **Use case**: Fully automated style learning and generation
- **Requirements**: OpenAI API key (GPT-4V + DALL-E 3)
- **Workflow**: Reference image → LLM extraction → Auto generation → Optimization

### 4. Production Mode
- **Use case**: Fast generation using pre-saved styles
- **Requirements**: OpenAI API key (DALL-E 3)
- **Workflow**: Load from library → Generate

## Style JSON Format

```json
{
  "palette": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"],
  "color_temperature": "warm",
  "color_harmony": "complementary",
  "saturation_level": 0.75,
  "brightness_level": 0.65,
  "contrast_level": 0.55,
  "line_style": "smooth",
  "line_weight": 0.6,
  "line_density": 0.5,
  "lighting_direction": "side",
  "lighting_quality": "soft",
  "shadow_intensity": 0.4,
  "composition_rule": "rule_of_thirds",
  "focal_point": "center",
  "depth_of_field": 0.6,
  "material_finish": "matte",
  "texture_scale": 0.5,
  "detail_level": 0.7
}
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/test_*.py -v

# Run integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Project Structure

```
StyleConditionedGenerativePipeline/
├── src/
│   ├── core/              # Core modules
│   │   ├── schema.py      # Style JSON validation
│   │   ├── engine.py      # Style normalization
│   │   ├── prompt_generator.py
│   │   └── library.py     # Style storage (SQLite)
│   ├── extractor/         # Style extraction
│   │   └── llm_extractor.py
│   ├── generator/         # Image generation
│   │   └── dalle_generator.py
│   ├── evaluator/         # Quality evaluation
│   │   ├── clip_evaluator.py
│   │   ├── structured_metrics.py
│   │   └── evaluator_v2.py
│   ├── optimizer/         # Style optimization
│   │   └── optimizer.py
│   └── pipeline/          # Complete pipelines
│       ├── manual_mode.py
│       ├── learning_mode.py
│       ├── auto_mode.py
│       └── production_mode.py
├── tests/
│   ├── test_*.py          # Unit tests
│   └── integration/       # Integration tests
├── examples/
│   └── usage_examples.py
└── data/
    └── style_library.db   # Saved styles
```

## Development Status

- ✅ Phase 1: Core modules (Schema, Engine, Prompt Generator, Library)
- ✅ Phase 2: Extractor Skill (prompt-based)
- ✅ Phase 3: Manual Mode Pipeline
- ✅ Phase 4: Evaluator v2 (CLIP + structured metrics)
- ✅ Phase 5: Optimizer + Learning Mode
- ✅ Phase 6: Auto Mode (LLM + DALL-E 3)
- 🔄 Phase 7: End-to-end integration tests

## API Costs (Estimated)

### Learning Mode (5 iterations)
- LLM extraction: ~$0.03 (3 samples × GPT-4V)
- DALL-E 3 generation: $0.20 (5 iterations × $0.04)
- **Total**: ~$0.23 per style

### Production Mode
- DALL-E 3 standard 1024×1024: $0.04 per image
- DALL-E 3 HD 1024×1024: $0.08 per image
- DALL-E 3 standard 1792×1024: $0.08 per image
- DALL-E 3 HD 1792×1024: $0.12 per image

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or PR.

## Acknowledgments

- OpenAI CLIP for semantic similarity
- OpenAI DALL-E 3 for image generation
- Anthropic Claude for vision understanding
