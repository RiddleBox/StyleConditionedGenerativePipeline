"""
Unit tests for Style JSON Schema Validator
"""

import pytest
import math
from src.core.schema import StyleJSONSchema, validate_style_json


# Golden sample from specification
VALID_STYLE_JSON = {
    "style_id": "arch_watercolor_v1",
    "composition": {
        "perspective": "isometric",
        "layout": "centered",
        "depth": 0.6
    },
    "line": {
        "type": "clean",
        "width": 1.2,
        "variation": 0.1,
        "locked": True
    },
    "color": {
        "palette": ["beige", "olive", "brown"],
        "saturation": 0.35,
        "contrast": 0.4,
        "temperature": "warm"
    },
    "material": {
        "type": "watercolor",
        "texture_strength": 0.5,
        "locked": True
    },
    "lighting": {
        "type": "soft_global",
        "direction": "top_left",
        "intensity": 0.3
    },
    "detail_density": {
        "foreground": 0.8,
        "background": 0.3
    },
    "negative_constraints": [
        "no photorealism",
        "no harsh shadows",
        "no high contrast"
    ]
}


class TestStyleJSONSchema:
    """Test StyleJSONSchema class."""
    
    def test_get_schema(self):
        """Test schema retrieval."""
        schema = StyleJSONSchema.get_schema()
        assert isinstance(schema, dict)
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
    
    def test_enum_definitions(self):
        """Test enum definitions are correct."""
        assert len(StyleJSONSchema.PERSPECTIVE_ENUM) == 5
        assert "isometric" in StyleJSONSchema.PERSPECTIVE_ENUM
        
        assert len(StyleJSONSchema.LAYOUT_ENUM) == 4
        assert "centered" in StyleJSONSchema.LAYOUT_ENUM
        
        assert len(StyleJSONSchema.LINE_TYPE_ENUM) == 4
        assert "clean" in StyleJSONSchema.LINE_TYPE_ENUM
        
        assert len(StyleJSONSchema.MATERIAL_TYPE_ENUM) == 5
        assert "watercolor" in StyleJSONSchema.MATERIAL_TYPE_ENUM
        
        assert len(StyleJSONSchema.LIGHTING_TYPE_ENUM) == 4
        assert "soft_global" in StyleJSONSchema.LIGHTING_TYPE_ENUM
        
        assert len(StyleJSONSchema.LIGHTING_DIRECTION_ENUM) == 6
        assert "top_left" in StyleJSONSchema.LIGHTING_DIRECTION_ENUM
        
        assert len(StyleJSONSchema.TEMPERATURE_ENUM) == 3
        assert "warm" in StyleJSONSchema.TEMPERATURE_ENUM


class TestValidateStyleJSON:
    """Test validate_style_json function."""
    
    def test_valid_style_json(self):
        """Test validation of valid Style JSON."""
        is_valid, errors = validate_style_json(VALID_STYLE_JSON)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_not_a_dict(self):
        """Test validation fails for non-dict input."""
        is_valid, errors = validate_style_json("not a dict")
        assert is_valid is False
        assert "must be a dictionary" in errors[0]
    
    def test_missing_required_field(self):
        """Test validation fails for missing required field."""
        style = VALID_STYLE_JSON.copy()
        del style["style_id"]
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("style_id" in err for err in errors)
    
    def test_additional_property(self):
        """Test validation fails for additional property."""
        style = VALID_STYLE_JSON.copy()
        style["extra_field"] = "not allowed"
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("extra_field" in err for err in errors)
    
    def test_empty_style_id(self):
        """Test validation fails for empty style_id."""
        style = VALID_STYLE_JSON.copy()
        style["style_id"] = ""
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("style_id" in err for err in errors)


class TestCompositionValidation:
    """Test composition validation."""
    
    def test_invalid_perspective(self):
        """Test validation fails for invalid perspective."""
        style = VALID_STYLE_JSON.copy()
        style["composition"]["perspective"] = "invalid"
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("perspective" in err for err in errors)
    
    def test_invalid_layout(self):
        """Test validation fails for invalid layout."""
        style = VALID_STYLE_JSON.copy()
        style["composition"]["layout"] = "invalid"
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("layout" in err for err in errors)
    
    def test_depth_out_of_range(self):
        """Test validation fails for depth out of range."""
        style = VALID_STYLE_JSON.copy()
        style["composition"]["depth"] = 1.5
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("depth" in err for err in errors)
    
    def test_depth_negative(self):
        """Test validation fails for negative depth."""
        style = VALID_STYLE_JSON.copy()
        style["composition"]["depth"] = -0.1
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("depth" in err for err in errors)
    
    def test_additional_composition_field(self):
        """Test validation fails for additional composition field."""
        style = VALID_STYLE_JSON.copy()
        style["composition"]["extra"] = "not allowed"
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("composition.extra" in err for err in errors)


class TestLineValidation:
    """Test line validation."""
    
    def test_invalid_line_type(self):
        """Test validation fails for invalid line type."""
        style = VALID_STYLE_JSON.copy()
        style["line"]["type"] = "invalid"
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("line.type" in err for err in errors)
    
    def test_line_width_out_of_range(self):
        """Test validation fails for line width out of range."""
        style = VALID_STYLE_JSON.copy()
        style["line"]["width"] = 6.0
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("line.width" in err for err in errors)
    
    def test_line_variation_out_of_range(self):
        """Test validation fails for line variation out of range."""
        style = VALID_STYLE_JSON.copy()
        style["line"]["variation"] = 1.5
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("line.variation" in err for err in errors)
    
    def test_line_locked_not_boolean(self):
        """Test validation fails for non-boolean locked."""
        style = VALID_STYLE_JSON.copy()
        style["line"]["locked"] = "yes"
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("line.locked" in err for err in errors)


class TestColorValidation:
    """Test color validation."""
    
    def test_empty_palette(self):
        """Test validation fails for empty palette."""
        style = VALID_STYLE_JSON.copy()
        style["color"]["palette"] = []
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("palette" in err for err in errors)
    
    def test_palette_too_large(self):
        """Test validation fails for palette with >8 items."""
        style = VALID_STYLE_JSON.copy()
        style["color"]["palette"] = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("palette" in err for err in errors)
    
    def test_palette_duplicate_items(self):
        """Test validation fails for duplicate palette items."""
        style = VALID_STYLE_JSON.copy()
        style["color"]["palette"] = ["red", "blue", "red"]
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("unique" in err for err in errors)
    
    def test_palette_empty_string(self):
        """Test validation fails for empty string in palette."""
        style = VALID_STYLE_JSON.copy()
        style["color"]["palette"] = ["red", ""]
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("palette[1]" in err for err in errors)
    
    def test_saturation_out_of_range(self):
        """Test validation fails for saturation out of range."""
        style = VALID_STYLE_JSON.copy()
        style["color"]["saturation"] = 1.5
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("saturation" in err for err in errors)
    
    def test_invalid_temperature(self):
        """Test validation fails for invalid temperature."""
        style = VALID_STYLE_JSON.copy()
        style["color"]["temperature"] = "hot"
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("temperature" in err for err in errors)


class TestMaterialValidation:
    """Test material validation."""
    
    def test_invalid_material_type(self):
        """Test validation fails for invalid material type."""
        style = VALID_STYLE_JSON.copy()
        style["material"]["type"] = "invalid"
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("material.type" in err for err in errors)
    
    def test_texture_strength_out_of_range(self):
        """Test validation fails for texture_strength out of range."""
        style = VALID_STYLE_JSON.copy()
        style["material"]["texture_strength"] = 1.5
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("texture_strength" in err for err in errors)


class TestLightingValidation:
    """Test lighting validation."""
    
    def test_invalid_lighting_type(self):
        """Test validation fails for invalid lighting type."""
        style = VALID_STYLE_JSON.copy()
        style["lighting"]["type"] = "invalid"
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("lighting.type" in err for err in errors)
    
    def test_invalid_lighting_direction(self):
        """Test validation fails for invalid lighting direction."""
        style = VALID_STYLE_JSON.copy()
        style["lighting"]["direction"] = "invalid"
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("lighting.direction" in err for err in errors)
    
    def test_intensity_out_of_range(self):
        """Test validation fails for intensity out of range."""
        style = VALID_STYLE_JSON.copy()
        style["lighting"]["intensity"] = 1.5
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("intensity" in err for err in errors)


class TestDetailDensityValidation:
    """Test detail_density validation."""
    
    def test_foreground_out_of_range(self):
        """Test validation fails for foreground out of range."""
        style = VALID_STYLE_JSON.copy()
        style["detail_density"]["foreground"] = 1.5
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("foreground" in err for err in errors)
    
    def test_background_out_of_range(self):
        """Test validation fails for background out of range."""
        style = VALID_STYLE_JSON.copy()
        style["detail_density"]["background"] = -0.1
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("background" in err for err in errors)


class TestNegativeConstraintsValidation:
    """Test negative_constraints validation."""
    
    def test_too_many_constraints(self):
        """Test validation fails for >10 constraints."""
        style = VALID_STYLE_JSON.copy()
        style["negative_constraints"] = [f"constraint_{i}" for i in range(11)]
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("negative_constraints" in err for err in errors)
    
    def test_empty_constraint(self):
        """Test validation fails for empty constraint."""
        style = VALID_STYLE_JSON.copy()
        style["negative_constraints"] = ["valid", ""]
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("negative_constraints[1]" in err for err in errors)


class TestNumericValidation:
    """Test numeric value validation."""
    
    def test_nan_value(self):
        """Test validation fails for NaN value."""
        style = VALID_STYLE_JSON.copy()
        style["composition"]["depth"] = float('nan')
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("finite" in err for err in errors)
    
    def test_infinity_value(self):
        """Test validation fails for Infinity value."""
        style = VALID_STYLE_JSON.copy()
        style["composition"]["depth"] = float('inf')
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("finite" in err for err in errors)
    
    def test_negative_infinity_value(self):
        """Test validation fails for -Infinity value."""
        style = VALID_STYLE_JSON.copy()
        style["composition"]["depth"] = float('-inf')
        is_valid, errors = validate_style_json(style)
        assert is_valid is False
        assert any("finite" in err for err in errors)


class TestDeterminism:
    """Test deterministic behavior."""
    
    def test_same_input_same_output(self):
        """Test that same input produces same output."""
        is_valid1, errors1 = validate_style_json(VALID_STYLE_JSON)
        is_valid2, errors2 = validate_style_json(VALID_STYLE_JSON)
        
        assert is_valid1 == is_valid2
        assert errors1 == errors2
    
    def test_invalid_input_consistent_errors(self):
        """Test that invalid input produces consistent errors."""
        style = VALID_STYLE_JSON.copy()
        style["composition"]["depth"] = 1.5
        
        is_valid1, errors1 = validate_style_json(style)
        is_valid2, errors2 = validate_style_json(style)
        
        assert is_valid1 == is_valid2
        assert errors1 == errors2
