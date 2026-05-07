"""
Unit tests for Manual Mode Pipeline
"""

import json
import pytest
from pathlib import Path
from src.pipeline.manual_mode import ManualModePipeline


@pytest.fixture
def valid_style_json():
    """A valid Style JSON for testing"""
    return {
        "style_id": "test-style-001",
        "composition": {
            "perspective": "isometric",
            "layout": "centered",
            "depth": 0.3
        },
        "line": {
            "type": "clean",
            "width": 0.4,
            "variation": 0.1,
            "locked": False
        },
        "color": {
            "palette": ["#FF5733", "#33FF57", "#3357FF"],
            "saturation": 0.8,
            "contrast": 0.6,
            "temperature": "warm"
        },
        "material": {
            "type": "flat",
            "texture_strength": 0.3,
            "locked": False
        },
        "lighting": {
            "type": "ambient",
            "direction": "top",
            "intensity": 0.7
        },
        "detail_density": {
            "foreground": 0.7,
            "background": 0.3
        },
        "negative_constraints": ["blurry", "noisy"]
    }


@pytest.fixture
def pipeline():
    """Create a ManualModePipeline instance"""
    return ManualModePipeline()


class TestManualModePipeline:
    """Test suite for ManualModePipeline"""
    
    def test_initialization(self, pipeline):
        """Test pipeline initialization"""
        assert pipeline.engine is not None
        assert pipeline.prompt_generator is not None
    
    def test_generate_prompt_success(self, pipeline, valid_style_json):
        """Test successful prompt generation"""
        success, result = pipeline.generate_prompt_for_manual_use(
            valid_style_json,
            subject="a mountain landscape"
        )
        
        assert success is True
        assert 'prompt' in result
        assert 'negative_prompt' in result
        assert 'instructions' in result
        assert 'normalized_style' in result
        
        # Check prompt is not empty
        assert len(result['prompt']) > 0
        assert isinstance(result['prompt'], str)
        
        # Check negative prompt is not empty
        assert len(result['negative_prompt']) > 0
        assert isinstance(result['negative_prompt'], str)
        
        # Check instructions contain key phrases
        instructions = result['instructions']
        assert 'ChatGPT' in instructions
        assert 'PROMPT START' in instructions
        assert 'PROMPT END' in instructions
    
    def test_generate_prompt_invalid_json(self, pipeline):
        """Test prompt generation with invalid Style JSON"""
        invalid_json = {"composition": {}}  # Missing required fields
        
        success, result = pipeline.generate_prompt_for_manual_use(
            invalid_json,
            validate=True
        )
        
        assert success is False
        assert 'error' in result
        assert result['error'] == 'Invalid Style JSON'
    
    def test_generate_prompt_skip_validation(self, pipeline):
        """Test prompt generation with validation skipped"""
        # Note: StyleEngine.normalize() is very tolerant and will fill defaults
        # So even invalid JSON may succeed. This test verifies that skipping
        # validation allows the process to continue to normalization.
        incomplete_json = {"composition": {}}
        
        success, result = pipeline.generate_prompt_for_manual_use(
            incomplete_json,
            validate=False
        )
        
        # With validation skipped, normalize() will fill defaults and succeed
        assert success is True
        assert 'prompt' in result
    
    def test_generate_prompt_custom_subject(self, pipeline, valid_style_json):
        """Test prompt generation with custom subject"""
        subject = "a futuristic city"
        
        success, result = pipeline.generate_prompt_for_manual_use(
            valid_style_json,
            subject=subject
        )
        
        assert success is True
        # The subject should appear in the prompt
        assert subject in result['prompt']
    
    def test_generate_prompt_deterministic(self, pipeline, valid_style_json):
        """Test that prompt generation is deterministic"""
        success1, result1 = pipeline.generate_prompt_for_manual_use(valid_style_json)
        success2, result2 = pipeline.generate_prompt_for_manual_use(valid_style_json)
        
        assert success1 is True
        assert success2 is True
        
        # Same input should produce same output
        assert result1['prompt'] == result2['prompt']
        assert result1['negative_prompt'] == result2['negative_prompt']
    
    def test_save_prompt_to_file(self, pipeline, valid_style_json, tmp_path):
        """Test saving prompt to file"""
        success, result = pipeline.generate_prompt_for_manual_use(valid_style_json)
        assert success is True
        
        output_path = tmp_path / "test_prompt.json"
        
        saved = pipeline.save_prompt_to_file(
            result['prompt'],
            result['negative_prompt'],
            output_path,
            style_json=result['normalized_style']
        )
        
        assert saved is True
        assert output_path.exists()
        
        # Verify file content
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        assert data['prompt'] == result['prompt']
        assert data['negative_prompt'] == result['negative_prompt']
        assert 'style_json' in data
    
    def test_save_prompt_without_style_json(self, pipeline, valid_style_json, tmp_path):
        """Test saving prompt without Style JSON"""
        success, result = pipeline.generate_prompt_for_manual_use(valid_style_json)
        assert success is True
        
        output_path = tmp_path / "test_prompt_no_style.json"
        
        saved = pipeline.save_prompt_to_file(
            result['prompt'],
            result['negative_prompt'],
            output_path
        )
        
        assert saved is True
        
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        assert 'style_json' not in data
    
    def test_load_prompt_from_file(self, pipeline, valid_style_json, tmp_path):
        """Test loading prompt from file"""
        # First save a prompt
        success, result = pipeline.generate_prompt_for_manual_use(valid_style_json)
        output_path = tmp_path / "test_prompt.json"
        pipeline.save_prompt_to_file(
            result['prompt'],
            result['negative_prompt'],
            output_path,
            style_json=result['normalized_style']
        )
        
        # Then load it
        success, loaded_data = pipeline.load_prompt_from_file(output_path)
        
        assert success is True
        assert loaded_data['prompt'] == result['prompt']
        assert loaded_data['negative_prompt'] == result['negative_prompt']
        assert 'style_json' in loaded_data
    
    def test_load_prompt_from_nonexistent_file(self, pipeline, tmp_path):
        """Test loading from non-existent file"""
        nonexistent_path = tmp_path / "nonexistent.json"
        
        success, result = pipeline.load_prompt_from_file(nonexistent_path)
        
        assert success is False
        assert 'error' in result
    
    def test_load_prompt_from_invalid_file(self, pipeline, tmp_path):
        """Test loading from invalid JSON file"""
        invalid_path = tmp_path / "invalid.json"
        
        # Write invalid JSON
        with open(invalid_path, 'w') as f:
            f.write("not valid json")
        
        success, result = pipeline.load_prompt_from_file(invalid_path)
        
        assert success is False
        assert 'error' in result
    
    def test_instructions_format(self, pipeline, valid_style_json):
        """Test that instructions have proper format"""
        success, result = pipeline.generate_prompt_for_manual_use(valid_style_json)
        
        instructions = result['instructions']
        
        # Check for key sections
        assert '=== Manual Image Generation Instructions ===' in instructions
        assert '---PROMPT START---' in instructions
        assert '---PROMPT END---' in instructions
        assert '---NEGATIVE PROMPT START---' in instructions
        assert '---NEGATIVE PROMPT END---' in instructions
        assert '=== Tips ===' in instructions
        assert '=== Next Steps ===' in instructions
        
        # Check that actual prompts are embedded
        assert result['prompt'] in instructions
        assert result['negative_prompt'] in instructions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
