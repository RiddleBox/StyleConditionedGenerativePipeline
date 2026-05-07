"""
Unit tests for Prompt Generator.

Tests deterministic prompt compilation from normalized style JSON.
"""

import pytest
from src.core.prompt_generator import PromptGenerator


class TestPromptGenerator:
    """Test PromptGenerator initialization and basic functionality."""
    
    def test_generator_initialization(self):
        """Test that PromptGenerator can be instantiated."""
        generator = PromptGenerator()
        assert generator is not None
    
    def test_generate_returns_string(self):
        """Test that generate() returns a string."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        result = generator.generate(style)
        assert isinstance(result, str)
    
    def test_generate_non_empty(self):
        """Test that generate() returns non-empty string."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        result = generator.generate(style)
        assert len(result) > 0
    
    def _get_normalized_style(self):
        """Helper: Return a normalized style JSON for testing."""
        return {
            "style_id": "test-style-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            },
            "line": {
                "type": "clean",
                "width": 2.5,
                "variation": 0.1,
                "locked": True
            },
            "color": {
                "palette": ["#3357FF", "#33FF57", "#FF5733"],
                "saturation": 0.8,
                "temperature": "warm"
            },
            "material": {
                "type": "matte",
                "texture_strength": 0.3
            },
            "lighting": {
                "type": "soft",
                "direction": "top-left",
                "intensity": 0.7
            },
            "detail_density": {
                "foreground": 0.9,
                "background": 0.3
            },
            "negative_constraints": ["blurry", "distorted", "low quality"]
        }


class TestDeterminism:
    """Test that prompt generation is deterministic."""
    
    def test_determinism_same_input_same_output(self):
        """Test that same input produces same output."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        
        result1 = generator.generate(style)
        result2 = generator.generate(style)
        
        assert result1 == result2
    
    def test_determinism_multiple_runs(self):
        """Test determinism across multiple runs."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        
        results = [generator.generate(style) for _ in range(10)]
        
        # All results should be identical
        for result in results[1:]:
            assert result == results[0]
    
    def test_determinism_different_instances(self):
        """Test determinism across different generator instances."""
        style = self._get_normalized_style()
        
        generator1 = PromptGenerator()
        generator2 = PromptGenerator()
        
        result1 = generator1.generate(style)
        result2 = generator2.generate(style)
        
        assert result1 == result2
    
    def _get_normalized_style(self):
        """Helper: Return a normalized style JSON for testing."""
        return {
            "style_id": "test-style-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            },
            "line": {
                "type": "clean",
                "width": 2.5,
                "variation": 0.1,
                "locked": True
            },
            "color": {
                "palette": ["#3357FF", "#33FF57", "#FF5733"],
                "saturation": 0.8,
                "temperature": "warm"
            },
            "material": {
                "type": "matte",
                "texture_strength": 0.3
            },
            "lighting": {
                "type": "soft",
                "direction": "top-left",
                "intensity": 0.7
            },
            "detail_density": {
                "foreground": 0.9,
                "background": 0.3
            },
            "negative_constraints": ["blurry", "distorted", "low quality"]
        }


class TestPromptContent:
    """Test that generated prompts contain expected content."""
    
    def test_composition_in_prompt(self):
        """Test that composition parameters appear in prompt."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        
        result = generator.generate(style)
        
        assert "isometric perspective" in result
        assert "centered composition" in result
    
    def test_line_in_prompt(self):
        """Test that line parameters appear in prompt."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        
        result = generator.generate(style)
        
        assert "clean lines" in result
        assert "medium strokes" in result
    
    def test_color_in_prompt(self):
        """Test that color parameters appear in prompt."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        
        result = generator.generate(style)
        
        assert "color palette" in result
        assert "warm color temperature" in result
    
    def test_material_in_prompt(self):
        """Test that material parameters appear in prompt."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        
        result = generator.generate(style)
        
        assert "matte material" in result
    
    def test_lighting_in_prompt(self):
        """Test that lighting parameters appear in prompt."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        
        result = generator.generate(style)
        
        assert "soft lighting" in result
        assert "top-left" in result
    
    def test_detail_density_in_prompt(self):
        """Test that detail density parameters appear in prompt."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        
        result = generator.generate(style)
        
        assert "foreground detail" in result
        assert "background detail" in result
    
    def test_negative_constraints_in_prompt(self):
        """Test that negative constraints appear in prompt."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        
        result = generator.generate(style)
        
        assert "avoid:" in result
        assert "blurry" in result
    
    def _get_normalized_style(self):
        """Helper: Return a normalized style JSON for testing."""
        return {
            "style_id": "test-style-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            },
            "line": {
                "type": "clean",
                "width": 2.5,
                "variation": 0.1,
                "locked": True
            },
            "color": {
                "palette": ["#3357FF", "#33FF57", "#FF5733"],
                "saturation": 0.8,
                "temperature": "warm"
            },
            "material": {
                "type": "matte",
                "texture_strength": 0.3
            },
            "lighting": {
                "type": "soft",
                "direction": "top-left",
                "intensity": 0.7
            },
            "detail_density": {
                "foreground": 0.9,
                "background": 0.3
            },
            "negative_constraints": ["blurry", "distorted", "low quality"]
        }


class TestNegativePrompt:
    """Test negative prompt extraction."""
    
    def test_get_negative_prompt(self):
        """Test that get_negative_prompt() extracts constraints."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        
        result = generator.get_negative_prompt(style)
        
        assert "blurry" in result
        assert "distorted" in result
        assert "low quality" in result
    
    def test_get_negative_prompt_empty(self):
        """Test that get_negative_prompt() returns empty string when no constraints."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        del style["negative_constraints"]
        
        result = generator.get_negative_prompt(style)
        
        assert result == ""
    
    def test_negative_prompt_determinism(self):
        """Test that negative prompt extraction is deterministic."""
        generator = PromptGenerator()
        style = self._get_normalized_style()
        
        result1 = generator.get_negative_prompt(style)
        result2 = generator.get_negative_prompt(style)
        
        assert result1 == result2
    
    def _get_normalized_style(self):
        """Helper: Return a normalized style JSON for testing."""
        return {
            "style_id": "test-style-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            },
            "line": {
                "type": "clean",
                "width": 2.5,
                "variation": 0.1,
                "locked": True
            },
            "color": {
                "palette": ["#3357FF", "#33FF57", "#FF5733"],
                "saturation": 0.8,
                "temperature": "warm"
            },
            "material": {
                "type": "matte",
                "texture_strength": 0.3
            },
            "lighting": {
                "type": "soft",
                "direction": "top-left",
                "intensity": 0.7
            },
            "detail_density": {
                "foreground": 0.9,
                "background": 0.3
            },
            "negative_constraints": ["blurry", "distorted", "low quality"]
        }


class TestEdgeCases:
    """Test edge cases and partial styles."""
    
    def test_minimal_style(self):
        """Test generation with minimal style (only style_id)."""
        generator = PromptGenerator()
        style = {"style_id": "minimal-001"}
        
        result = generator.generate(style)
        
        # Should return empty or minimal prompt
        assert isinstance(result, str)
    
    def test_partial_style(self):
        """Test generation with partial style (only composition)."""
        generator = PromptGenerator()
        style = {
            "style_id": "partial-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            }
        }
        
        result = generator.generate(style)
        
        assert "isometric perspective" in result
        assert "centered composition" in result
    
    def test_empty_negative_constraints(self):
        """Test generation with empty negative_constraints list."""
        generator = PromptGenerator()
        style = {
            "style_id": "test-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            },
            "negative_constraints": []
        }
        
        result = generator.generate(style)
        
        # Should not crash
        assert isinstance(result, str)
