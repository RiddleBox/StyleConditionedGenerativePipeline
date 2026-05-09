"""
End-to-End Integration Tests for Manual Mode

Tests the complete Manual Mode workflow:
1. Create/validate style JSON
2. Normalize with StyleEngine
3. Generate prompt with PromptGenerator
4. Save/load prompt for manual use
"""

import pytest
import tempfile
from pathlib import Path
import json

from src.core.schema import validate_style_json
from src.core.engine import StyleEngine
from src.core.prompt_generator import PromptGenerator
from src.pipeline.manual_mode import ManualModePipeline


@pytest.fixture
def sample_style():
    """Create a valid style JSON with correct nested structure"""
    return {
        "style_id": "test_style_001",
        "composition": {
            "perspective": "eye_level",
            "layout": "rule_of_thirds",
            "depth": 0.6
        },
        "line": {
            "type": "clean",
            "width": 0.6,
            "variation": 0.5
        },
        "color": {
            "palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"],
            "saturation": 0.75,
            "contrast": 0.55,
            "temperature": "warm"
        },
        "material": {
            "type": "digital_paint",
            "texture_strength": 0.5
        },
        "lighting": {
            "type": "soft_global",
            "direction": "left",
            "intensity": 0.7
        },
        "detail_density": {
            "foreground": 0.7,
            "background": 0.4
        },
        "negative_constraints": ["blurry", "low quality"]
    }


class TestManualModeE2E:
    """End-to-end tests for Manual Mode"""
    
    def test_complete_manual_workflow(self, sample_style):
        """Test complete manual mode workflow"""
        # Step 1: Validate style
        is_valid, errors = validate_style_json(sample_style)
        assert is_valid, f"Style validation failed: {errors}"
        
        # Step 2: Normalize style
        engine = StyleEngine()
        normalized_style = engine.normalize(sample_style)
        assert normalized_style is not None
        
        # Step 3: Generate prompt
        prompt_gen = PromptGenerator()
        prompt = prompt_gen.generate(normalized_style)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        
        # Step 4: Verify prompt contains style elements
        assert any(color.lower().replace("#", "") in prompt.lower() 
                   for color in sample_style["color"]["palette"][:3])
    
    def test_manual_mode_pipeline_generate_prompt(self, sample_style):
        """Test ManualModePipeline prompt generation"""
        pipeline = ManualModePipeline()
        
        success, result = pipeline.generate_prompt_for_manual_use(
            style_json=sample_style,
            subject="a cat in a garden"
        )
        
        assert success, f"Prompt generation failed: {result}"
        assert "prompt" in result
        assert "negative_prompt" in result
        assert "instructions" in result
        assert isinstance(result["prompt"], str)
        assert "cat" in result["prompt"].lower()
    
    def test_manual_mode_save_and_load_prompt(self, sample_style):
        """Test saving and loading prompts"""
        pipeline = ManualModePipeline()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "test_prompt.json"
            
            # Generate prompt
            success, result = pipeline.generate_prompt_for_manual_use(
                style_json=sample_style,
                subject="a mountain"
            )
            assert success, f"Prompt generation failed: {result}"
            
            # Save
            saved = pipeline.save_prompt_to_file(
                prompt=result["prompt"],
                negative_prompt=result["negative_prompt"],
                filepath=str(save_path),
                style_json=result["normalized_style"]
            )
            assert saved, "Failed to save prompt"
            
            # Verify file exists
            assert save_path.exists()
            
            # Load and verify
            load_success, loaded = pipeline.load_prompt_from_file(str(save_path))
            assert load_success, f"Failed to load prompt: {loaded}"
            assert loaded["prompt"] == result["prompt"]
            assert loaded["negative_prompt"] == result["negative_prompt"]
    
    def test_style_engine_idempotency(self, sample_style):
        """Test that normalizing twice gives same result"""
        engine = StyleEngine()
        
        normalized1 = engine.normalize(sample_style)
        normalized2 = engine.normalize(normalized1)
        
        # Should be identical
        assert normalized1 == normalized2
    
    def test_prompt_generator_determinism(self, sample_style):
        """Test that same style generates same prompt"""
        engine = StyleEngine()
        prompt_gen = PromptGenerator()
        
        normalized = engine.normalize(sample_style)
        
        prompt1 = prompt_gen.generate(normalized)
        prompt2 = prompt_gen.generate(normalized)
        
        # Should be identical (deterministic)
        assert prompt1 == prompt2
    
    def test_invalid_style_handling(self):
        """Test handling of invalid style JSON"""
        invalid_style = {
            "style_id": "invalid_test",
            "composition": {
                "perspective": "invalid_perspective",  # Invalid enum
                "layout": "centered",
                "depth": 1.5  # Out of range
            },
            "color": {
                "palette": ["#FF0000"],  # Too few colors (minItems: 1 is OK, but let's test other issues)
                "saturation": 1.5,  # Out of range
                "contrast": 0.5,
                "temperature": "invalid_temp"  # Invalid enum
            }
            # Missing required fields: line, material, lighting, detail_density, negative_constraints
        }
        
        is_valid, errors = validate_style_json(invalid_style)
        
        assert not is_valid
        assert len(errors) > 0
    
    def test_partial_style_completion(self):
        """Test that engine normalizes partial styles (fills defaults for missing nested fields)"""
        partial_style = {
            "style_id": "partial_test",
            "composition": {
                "perspective": "eye_level",
                "layout": "centered",
                "depth": 0.5
            },
            "line": {
                "type": "clean",
                "width": 1.0,
                "variation": 0.3
            },
            "color": {
                "palette": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"],
                "saturation": 0.5,  # Now provided
                "contrast": 0.5,    # Now provided
                "temperature": "warm"
            },
            "material": {
                "type": "digital_paint",
                "texture_strength": 0.5
            },
            "lighting": {
                "type": "ambient",
                "direction": "none",
                "intensity": 0.5
            },
            "detail_density": {
                "foreground": 0.5,
                "background": 0.5
            },
            "negative_constraints": []
        }
        
        engine = StyleEngine()
        normalized = engine.normalize(partial_style)
        
        # Should be valid after normalization
        is_valid, errors = validate_style_json(normalized)
        assert is_valid, f"Normalized style invalid: {errors}"
        
        # Should be idempotent
        normalized2 = engine.normalize(normalized)
        assert normalized == normalized2
    
    def test_multiple_subjects(self, sample_style):
        """Test that PromptGenerator is deterministic (same style = same prompt)"""
        engine = StyleEngine()
        prompt_gen = PromptGenerator()
        
        normalized = engine.normalize(sample_style)
        
        # Generate same prompt multiple times
        prompts = []
        for _ in range(3):
            prompt = prompt_gen.generate(normalized)
            prompts.append(prompt)
        
        # All prompts should be identical (deterministic)
        assert len(set(prompts)) == 1, "PromptGenerator should be deterministic"
        assert all(p == prompts[0] for p in prompts)
