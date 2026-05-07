"""
Style JSON Schema Validator

Implements strict validation for Style JSON v1.0 based on
Style_JSON_Schema_Deep_Specification_v1.md

Core Principle:
    Style JSON is a strictly typed intermediate representation (IR),
    not descriptive data.
"""

import math
from typing import Dict, List, Any, Tuple


class StyleJSONSchema:
    """Style JSON Schema definition and validation."""
    
    # Enum definitions (closed vocabulary)
    PERSPECTIVE_ENUM = ["top_down", "isometric", "eye_level", "low_angle", "high_angle"]
    LAYOUT_ENUM = ["centered", "rule_of_thirds", "symmetrical", "asymmetrical"]
    LINE_TYPE_ENUM = ["none", "clean", "sketch", "ink"]
    MATERIAL_TYPE_ENUM = ["flat", "watercolor", "oil", "ink", "digital_paint"]
    LIGHTING_TYPE_ENUM = ["ambient", "directional", "soft_global", "studio"]
    LIGHTING_DIRECTION_ENUM = ["none", "left", "right", "top", "top_left", "top_right"]
    TEMPERATURE_ENUM = ["warm", "neutral", "cool"]
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """
        Return the complete JSON Schema for Style JSON v1.0.
        
        Returns:
            dict: JSON Schema definition
        """
        return {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "style_id",
                "composition",
                "line",
                "color",
                "material",
                "lighting",
                "detail_density",
                "negative_constraints"
            ],
            "properties": {
                "style_id": {
                    "type": "string",
                    "minLength": 1
                },
                "composition": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["perspective", "layout", "depth"],
                    "properties": {
                        "perspective": {
                            "type": "string",
                            "enum": StyleJSONSchema.PERSPECTIVE_ENUM
                        },
                        "layout": {
                            "type": "string",
                            "enum": StyleJSONSchema.LAYOUT_ENUM
                        },
                        "depth": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    }
                },
                "line": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["type", "width", "variation"],
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": StyleJSONSchema.LINE_TYPE_ENUM
                        },
                        "width": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 5.0
                        },
                        "variation": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "locked": {
                            "type": "boolean"
                        }
                    }
                },
                "color": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["palette", "saturation", "contrast", "temperature"],
                    "properties": {
                        "palette": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 8,
                            "items": {
                                "type": "string",
                                "minLength": 1
                            }
                        },
                        "saturation": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "contrast": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "temperature": {
                            "type": "string",
                            "enum": StyleJSONSchema.TEMPERATURE_ENUM
                        }
                    }
                },
                "material": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["type", "texture_strength"],
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": StyleJSONSchema.MATERIAL_TYPE_ENUM
                        },
                        "texture_strength": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "locked": {
                            "type": "boolean"
                        }
                    }
                },
                "lighting": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["type", "direction", "intensity"],
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": StyleJSONSchema.LIGHTING_TYPE_ENUM
                        },
                        "direction": {
                            "type": "string",
                            "enum": StyleJSONSchema.LIGHTING_DIRECTION_ENUM
                        },
                        "intensity": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    }
                },
                "detail_density": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["foreground", "background"],
                    "properties": {
                        "foreground": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "background": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    }
                },
                "negative_constraints": {
                    "type": "array",
                    "minItems": 0,
                    "maxItems": 10,
                    "items": {
                        "type": "string",
                        "minLength": 1
                    }
                }
            }
        }


def validate_style_json(style: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a Style JSON object against the schema.
    
    Args:
        style: Style JSON object to validate
        
    Returns:
        Tuple of (is_valid, errors)
        - is_valid: True if valid, False otherwise
        - errors: List of error messages (empty if valid)
        
    Validation Rules:
        1. All required fields must exist
        2. No additional properties allowed
        3. All enum values must be from closed vocabulary
        4. All numeric values must be in valid ranges
        5. All numeric values must be finite (no NaN/Infinity)
        6. Palette must have 1-8 unique items
        7. Palette items must have unique values
    """
    errors = []
    
    # Check if style is a dict
    if not isinstance(style, dict):
        return False, ["Style must be a dictionary"]
    
    # Check required top-level fields
    required_fields = [
        "style_id", "composition", "line", "color",
        "material", "lighting", "detail_density", "negative_constraints"
    ]
    for field in required_fields:
        if field not in style:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Check for additional properties at top level
    allowed_fields = set(required_fields)
    for field in style.keys():
        if field not in allowed_fields:
            errors.append(f"Additional property not allowed: {field}")
    
    # Validate style_id
    if not isinstance(style["style_id"], str) or len(style["style_id"]) == 0:
        errors.append("style_id must be a non-empty string")
    
    # Validate composition
    errors.extend(_validate_composition(style.get("composition", {})))
    
    # Validate line
    errors.extend(_validate_line(style.get("line", {})))
    
    # Validate color
    errors.extend(_validate_color(style.get("color", {})))
    
    # Validate material
    errors.extend(_validate_material(style.get("material", {})))
    
    # Validate lighting
    errors.extend(_validate_lighting(style.get("lighting", {})))
    
    # Validate detail_density
    errors.extend(_validate_detail_density(style.get("detail_density", {})))
    
    # Validate negative_constraints
    errors.extend(_validate_negative_constraints(style.get("negative_constraints", [])))
    
    return len(errors) == 0, errors


def _validate_composition(comp: Dict[str, Any]) -> List[str]:
    """Validate composition object."""
    errors = []
    
    if not isinstance(comp, dict):
        return ["composition must be an object"]
    
    # Check required fields
    required = ["perspective", "layout", "depth"]
    for field in required:
        if field not in comp:
            errors.append(f"composition.{field} is required")
    
    # Check for additional properties
    for field in comp.keys():
        if field not in required:
            errors.append(f"composition.{field} is not allowed")
    
    # Validate perspective
    if "perspective" in comp:
        if comp["perspective"] not in StyleJSONSchema.PERSPECTIVE_ENUM:
            errors.append(f"composition.perspective must be one of {StyleJSONSchema.PERSPECTIVE_ENUM}")
    
    # Validate layout
    if "layout" in comp:
        if comp["layout"] not in StyleJSONSchema.LAYOUT_ENUM:
            errors.append(f"composition.layout must be one of {StyleJSONSchema.LAYOUT_ENUM}")
    
    # Validate depth
    if "depth" in comp:
        errors.extend(_validate_number(comp["depth"], "composition.depth", 0.0, 1.0))
    
    return errors


def _validate_line(line: Dict[str, Any]) -> List[str]:
    """Validate line object."""
    errors = []
    
    if not isinstance(line, dict):
        return ["line must be an object"]
    
    # Check required fields
    required = ["type", "width", "variation"]
    for field in required:
        if field not in line:
            errors.append(f"line.{field} is required")
    
    # Check for additional properties
    allowed = required + ["locked"]
    for field in line.keys():
        if field not in allowed:
            errors.append(f"line.{field} is not allowed")
    
    # Validate type
    if "type" in line:
        if line["type"] not in StyleJSONSchema.LINE_TYPE_ENUM:
            errors.append(f"line.type must be one of {StyleJSONSchema.LINE_TYPE_ENUM}")
    
    # Validate width
    if "width" in line:
        errors.extend(_validate_number(line["width"], "line.width", 0.0, 5.0))
    
    # Validate variation
    if "variation" in line:
        errors.extend(_validate_number(line["variation"], "line.variation", 0.0, 1.0))
    
    # Validate locked (optional)
    if "locked" in line and not isinstance(line["locked"], bool):
        errors.append("line.locked must be a boolean")
    
    return errors


def _validate_color(color: Dict[str, Any]) -> List[str]:
    """Validate color object."""
    errors = []
    
    if not isinstance(color, dict):
        return ["color must be an object"]
    
    # Check required fields
    required = ["palette", "saturation", "contrast", "temperature"]
    for field in required:
        if field not in color:
            errors.append(f"color.{field} is required")
    
    # Check for additional properties
    for field in color.keys():
        if field not in required:
            errors.append(f"color.{field} is not allowed")
    
    # Validate palette
    if "palette" in color:
        palette = color["palette"]
        if not isinstance(palette, list):
            errors.append("color.palette must be an array")
        elif len(palette) < 1:
            errors.append("color.palette must have at least 1 item")
        elif len(palette) > 8:
            errors.append("color.palette must have at most 8 items")
        else:
            # Check all items are non-empty strings
            for i, item in enumerate(palette):
                if not isinstance(item, str) or len(item) == 0:
                    errors.append(f"color.palette[{i}] must be a non-empty string")
            
            # Check for duplicates
            if len(palette) != len(set(palette)):
                errors.append("color.palette must have unique items")
    
    # Validate saturation
    if "saturation" in color:
        errors.extend(_validate_number(color["saturation"], "color.saturation", 0.0, 1.0))
    
    # Validate contrast
    if "contrast" in color:
        errors.extend(_validate_number(color["contrast"], "color.contrast", 0.0, 1.0))
    
    # Validate temperature
    if "temperature" in color:
        if color["temperature"] not in StyleJSONSchema.TEMPERATURE_ENUM:
            errors.append(f"color.temperature must be one of {StyleJSONSchema.TEMPERATURE_ENUM}")
    
    return errors


def _validate_material(material: Dict[str, Any]) -> List[str]:
    """Validate material object."""
    errors = []
    
    if not isinstance(material, dict):
        return ["material must be an object"]
    
    # Check required fields
    required = ["type", "texture_strength"]
    for field in required:
        if field not in material:
            errors.append(f"material.{field} is required")
    
    # Check for additional properties
    allowed = required + ["locked"]
    for field in material.keys():
        if field not in allowed:
            errors.append(f"material.{field} is not allowed")
    
    # Validate type
    if "type" in material:
        if material["type"] not in StyleJSONSchema.MATERIAL_TYPE_ENUM:
            errors.append(f"material.type must be one of {StyleJSONSchema.MATERIAL_TYPE_ENUM}")
    
    # Validate texture_strength
    if "texture_strength" in material:
        errors.extend(_validate_number(material["texture_strength"], "material.texture_strength", 0.0, 1.0))
    
    # Validate locked (optional)
    if "locked" in material and not isinstance(material["locked"], bool):
        errors.append("material.locked must be a boolean")
    
    return errors


def _validate_lighting(lighting: Dict[str, Any]) -> List[str]:
    """Validate lighting object."""
    errors = []
    
    if not isinstance(lighting, dict):
        return ["lighting must be an object"]
    
    # Check required fields
    required = ["type", "direction", "intensity"]
    for field in required:
        if field not in lighting:
            errors.append(f"lighting.{field} is required")
    
    # Check for additional properties
    for field in lighting.keys():
        if field not in required:
            errors.append(f"lighting.{field} is not allowed")
    
    # Validate type
    if "type" in lighting:
        if lighting["type"] not in StyleJSONSchema.LIGHTING_TYPE_ENUM:
            errors.append(f"lighting.type must be one of {StyleJSONSchema.LIGHTING_TYPE_ENUM}")
    
    # Validate direction
    if "direction" in lighting:
        if lighting["direction"] not in StyleJSONSchema.LIGHTING_DIRECTION_ENUM:
            errors.append(f"lighting.direction must be one of {StyleJSONSchema.LIGHTING_DIRECTION_ENUM}")
    
    # Validate intensity
    if "intensity" in lighting:
        errors.extend(_validate_number(lighting["intensity"], "lighting.intensity", 0.0, 1.0))
    
    return errors


def _validate_detail_density(detail: Dict[str, Any]) -> List[str]:
    """Validate detail_density object."""
    errors = []
    
    if not isinstance(detail, dict):
        return ["detail_density must be an object"]
    
    # Check required fields
    required = ["foreground", "background"]
    for field in required:
        if field not in detail:
            errors.append(f"detail_density.{field} is required")
    
    # Check for additional properties
    for field in detail.keys():
        if field not in required:
            errors.append(f"detail_density.{field} is not allowed")
    
    # Validate foreground
    if "foreground" in detail:
        errors.extend(_validate_number(detail["foreground"], "detail_density.foreground", 0.0, 1.0))
    
    # Validate background
    if "background" in detail:
        errors.extend(_validate_number(detail["background"], "detail_density.background", 0.0, 1.0))
    
    return errors


def _validate_negative_constraints(constraints: List[str]) -> List[str]:
    """Validate negative_constraints array."""
    errors = []
    
    if not isinstance(constraints, list):
        return ["negative_constraints must be an array"]
    
    if len(constraints) > 10:
        errors.append("negative_constraints must have at most 10 items")
    
    for i, item in enumerate(constraints):
        if not isinstance(item, str) or len(item) == 0:
            errors.append(f"negative_constraints[{i}] must be a non-empty string")
    
    return errors


def _validate_number(value: Any, field_name: str, min_val: float, max_val: float) -> List[str]:
    """
    Validate a numeric field.
    
    Args:
        value: Value to validate
        field_name: Name of the field (for error messages)
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Check type
    if not isinstance(value, (int, float)):
        errors.append(f"{field_name} must be a number")
        return errors
    
    # Check for NaN/Infinity
    if math.isnan(value) or math.isinf(value):
        errors.append(f"{field_name} must be finite (no NaN/Infinity)")
        return errors
    
    # Check range
    if value < min_val or value > max_val:
        errors.append(f"{field_name} must be between {min_val} and {max_val}")
    
    return errors
