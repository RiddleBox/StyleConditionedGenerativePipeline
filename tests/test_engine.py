"""
Unit tests for Style Engine.

Tests the 9-step normalization pipeline and guarantees:
- Idempotency: engine(engine(x)) == engine(x)
- Determinism: Same input always produces same output
"""

import pytest
import copy
from src.core.engine import StyleEngine


class TestStyleEngine:
    """Test StyleEngine initialization and basic functionality."""
    
    def test_engine_initialization(self):
        """Test that StyleEngine can be instantiated."""
        engine = StyleEngine()
        assert engine is not None
    
    def test_normalize_returns_dict(self):
        """Test that normalize() returns a dictionary."""
        engine = StyleEngine()
        style = self._get_valid_style()
        result = engine.normalize(style)
        assert isinstance(result, dict)
    
    def test_normalize_does_not_mutate_input(self):
        """Test that normalize() does not mutate the input."""
        engine = StyleEngine()
        style = self._get_valid_style()
        original = copy.deepcopy(style)
        engine.normalize(style)
        assert style == original
    
    def _get_valid_style(self):
        """Helper: Return a valid style JSON for testing."""
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
                "palette": ["#FF5733", "#33FF57", "#3357FF"],
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


class TestIdempotency:
    """Test that normalization is idempotent."""
    
    def test_idempotency_basic(self):
        """Test engine(engine(x)) == engine(x)."""
        engine = StyleEngine()
        style = self._get_valid_style()
        
        normalized_once = engine.normalize(style)
        normalized_twice = engine.normalize(normalized_once)
        
        assert normalized_once == normalized_twice
    
    def test_idempotency_with_unsorted_palette(self):
        """Test idempotency with unsorted palette."""
        engine = StyleEngine()
        style = self._get_valid_style()
        style["color"]["palette"] = ["#FF5733", "#3357FF", "#33FF57"]  # Unsorted
        
        normalized_once = engine.normalize(style)
        normalized_twice = engine.normalize(normalized_once)
        
        assert normalized_once == normalized_twice
    
    def test_idempotency_with_unsorted_constraints(self):
        """Test idempotency with unsorted negative_constraints."""
        engine = StyleEngine()
        style = self._get_valid_style()
        style["negative_constraints"] = ["low quality", "blurry", "distorted"]  # Unsorted
        
        normalized_once = engine.normalize(style)
        normalized_twice = engine.normalize(normalized_once)
        
        assert normalized_once == normalized_twice
    
    def test_idempotency_with_extra_precision(self):
        """Test idempotency with extra numeric precision."""
        engine = StyleEngine()
        style = self._get_valid_style()
        style["line"]["width"] = 2.5555555  # Extra precision
        
        normalized_once = engine.normalize(style)
        normalized_twice = engine.normalize(normalized_once)
        
        assert normalized_once == normalized_twice
    
    def _get_valid_style(self):
        """Helper: Return a valid style JSON for testing."""
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
                "palette": ["#FF5733", "#33FF57", "#3357FF"],
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
    """Test that normalization is deterministic."""
    
    def test_determinism_same_input_same_output(self):
        """Test that same input produces same output."""
        engine = StyleEngine()
        style = self._get_valid_style()
        
        result1 = engine.normalize(style)
        result2 = engine.normalize(style)
        
        assert result1 == result2
    
    def test_determinism_multiple_runs(self):
        """Test determinism across multiple runs."""
        engine = StyleEngine()
        style = self._get_valid_style()
        
        results = [engine.normalize(style) for _ in range(10)]
        
        # All results should be identical
        for result in results[1:]:
            assert result == results[0]
    
    def _get_valid_style(self):
        """Helper: Return a valid style JSON for testing."""
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
                "palette": ["#FF5733", "#33FF57", "#3357FF"],
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


class TestNormalizationSteps:
    """Test individual normalization steps."""
    
    def test_palette_sorting(self):
        """Test that palette is sorted alphabetically."""
        engine = StyleEngine()
        style = self._get_valid_style()
        style["color"]["palette"] = ["#FF5733", "#3357FF", "#33FF57"]  # Unsorted
        
        result = engine.normalize(style)
        
        assert result["color"]["palette"] == ["#3357FF", "#33FF57", "#FF5733"]
    
    def test_numeric_precision(self):
        """Test that numeric values are rounded to 2 decimal places."""
        engine = StyleEngine()
        style = self._get_valid_style()
        style["line"]["width"] = 2.5555555
        style["color"]["saturation"] = 0.8888888
        
        result = engine.normalize(style)
        
        assert result["line"]["width"] == 2.56
        assert result["color"]["saturation"] == 0.89
    
    def test_negative_constraints_sorting(self):
        """Test that negative_constraints are sorted alphabetically."""
        engine = StyleEngine()
        style = self._get_valid_style()
        style["negative_constraints"] = ["low quality", "blurry", "distorted"]
        
        result = engine.normalize(style)
        
        assert result["negative_constraints"] == ["blurry", "distorted", "low quality"]
    
    def test_enum_normalization(self):
        """Test that enum values are normalized to lowercase."""
        engine = StyleEngine()
        style = self._get_valid_style()
        style["composition"]["perspective"] = "ISOMETRIC"
        style["line"]["type"] = "CLEAN"
        style["color"]["temperature"] = "WARM"
        
        result = engine.normalize(style)
        
        assert result["composition"]["perspective"] == "isometric"
        assert result["line"]["type"] == "clean"
        assert result["color"]["temperature"] == "warm"
    
    def test_whitespace_normalization(self):
        """Test that whitespace in strings is normalized."""
        engine = StyleEngine()
        style = self._get_valid_style()
        style["style_id"] = "test  style   001"  # Extra spaces
        style["negative_constraints"] = ["low  quality", "  blurry  "]
        
        result = engine.normalize(style)
        
        assert result["style_id"] == "test style 001"
        assert "low quality" in result["negative_constraints"]
        assert "blurry" in result["negative_constraints"]
    
    def test_field_order(self):
        """Test that fields are ordered consistently."""
        engine = StyleEngine()
        style = self._get_valid_style()
        
        # Shuffle field order
        shuffled = {
            "negative_constraints": style["negative_constraints"],
            "style_id": style["style_id"],
            "lighting": style["lighting"],
            "composition": style["composition"],
            "material": style["material"],
            "line": style["line"],
            "detail_density": style["detail_density"],
            "color": style["color"]
        }
        
        result = engine.normalize(shuffled)
        
        # Check that fields are in canonical order
        keys = list(result.keys())
        expected_order = [
            "style_id",
            "composition",
            "line",
            "color",
            "material",
            "lighting",
            "detail_density",
            "negative_constraints"
        ]
        assert keys == expected_order
    
    def _get_valid_style(self):
        """Helper: Return a valid style JSON for testing."""
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
                "palette": ["#FF5733", "#33FF57", "#3357FF"],
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


class TestIsNormalized:
    """Test the is_normalized() method."""
    
    def test_is_normalized_true(self):
        """Test that normalized style returns True."""
        engine = StyleEngine()
        style = self._get_valid_style()
        normalized = engine.normalize(style)
        
        assert engine.is_normalized(normalized) is True
    
    def test_is_normalized_false_unsorted_palette(self):
        """Test that unsorted palette returns False."""
        engine = StyleEngine()
        style = self._get_valid_style()
        style["color"]["palette"] = ["#FF5733", "#3357FF", "#33FF57"]  # Unsorted
        
        assert engine.is_normalized(style) is False
    
    def test_is_normalized_false_extra_precision(self):
        """Test that extra precision returns False."""
        engine = StyleEngine()
        style = self._get_valid_style()
        style["line"]["width"] = 2.5555555
        
        assert engine.is_normalized(style) is False
    
    def test_is_normalized_false_unsorted_constraints(self):
        """Test that unsorted constraints return False."""
        engine = StyleEngine()
        style = self._get_valid_style()
        style["negative_constraints"] = ["low quality", "blurry", "distorted"]
        
        assert engine.is_normalized(style) is False
    
    def _get_valid_style(self):
        """Helper: Return a valid style JSON for testing."""
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
                "palette": ["#3357FF", "#33FF57", "#FF5733"],  # Already sorted
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
            "negative_constraints": ["blurry", "distorted", "low quality"]  # Already sorted
        }
