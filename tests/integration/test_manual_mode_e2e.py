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

from src.core.schema import StyleJSONSchema
from src.core.engine import StyleEngine
from src.core.prompt_generator import PromptGenerator
from src.pipeline.manual_mode import ManualModePipeline


@pytest.fixture
def sample_style():
    """Create a valid style JSON"""
    return {
        "palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"],
        "color_temperature": "warm",
        "color_harmony": "analogous",
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


class TestManualModeE2E:
    """End-to-end tests for Manual Mode"""
    
    def test_complete_manual_workflow(self, sample_style):
        """Test complete manual mode workflow"""
        # Step 1: Validate style
        schema = StyleJSONSchema()
        is_valid, errors = schema.validate(sample_style)
        assert is_valid, f"Style validation failed: {errors}"
        
        # Step 2: Normalize style
        engine = StyleEngine()
        normalized_style = engine.normalize(sample_style)
        assert normalized_style is not None
        
        # Step 3: Generate prompt
        prompt_gen = PromptGenerator()
        prompt = prompt_gen.generate(normalized_style, subject="a serene landscape")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "landscape" in prompt.lower()
        
        # Step 4: Verify prompt contains style elements
        assert any(color.lower().replace("#", "") in prompt.lower() 
                   for color in sample_style["palette"][:3])
    
    def test_manual_mode_pipeline_generate_prompt(self, sample_style):
        """Test ManualModePipeline prompt generation"""
        pipeline = ManualModePipeline()
        
        result = pipeline.generate_prompt_for_manual_use(
            style=sample_style,
            subject="a cat in a garden"
        )
        
        assert "prompt" in result
        assert "instructions" in result
        assert "tips" in result
        assert isinstance(result["prompt"], str)
        assert "cat" in result["prompt"].lower()
    
    def test_manual_mode_save_and_load_prompt(self, sample_style):
        """Test saving and loading prompts"""
        pipeline = ManualModePipeline()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "test_prompt.txt"
            
            # Generate and save
            result = pipeline.generate_prompt_for_manual_use(
                style=sample_style,
                subject="a mountain"
            )
            pipeline.save_prompt_to_file(result, save_path)
            
            # Verify file exists
            assert save_path.exists()
            
            # Load and verify
            loaded = pipeline.load_prompt_from_file(save_path)
            assert loaded["prompt"] == result["prompt"]
            assert loaded["subject"] == result["subject"]
    
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
        
        prompt1 = prompt_gen.generate(normalized, subject="a tree")
        prompt2 = prompt_gen.generate(normalized, subject="a tree")
        
        # Should be identical (deterministic)
        assert prompt1 == prompt2
    
    def test_invalid_style_handling(self):
        """Test handling of invalid style JSON"""
        invalid_style = {
            "palette": ["#FF0000"],  # Too few colors
            "color_temperature": "invalid_value",  # Invalid enum
            "saturation_level": 1.5  # Out of range
        }
        
        schema = StyleJSONSchema()
        is_valid, errors = schema.validate(invalid_style)
        
        assert not is_valid
        assert len(errors) > 0
    
    def test_partial_style_completion(self):
        """Test that engine can complete partial styles"""
        partial_style = {
            "palette": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"],
            "color_temperature": "warm"
            # Missing many fields
        }
        
        engine = StyleEngine()
        completed = engine.normalize(partial_style)
        
        # Should have all required fields
        schema = StyleJSONSchema()
        is_valid, errors = schema.validate(completed)
        assert is_valid, f"Completed style invalid: {errors}"
    
    def test_multiple_subjects(self, sample_style):
        """Test generating prompts for different subjects"""
        engine = StyleEngine()
        prompt_gen = PromptGenerator()
        
        normalized = engine.normalize(sample_style)
        subjects = ["a cat", "a landscape", "abstract art"]
        
        prompts = []
        for subject in subjects:
            prompt = prompt_gen.generate(normalized, subject=subject)
            prompts.append(prompt)
            assert subject.lower() in prompt.lower()
        
        # All prompts should be different
        assert len(set(prompts)) == len(prompts)
