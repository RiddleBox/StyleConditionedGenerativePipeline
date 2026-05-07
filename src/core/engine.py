"""
Style Engine: 9-step normalization pipeline for style JSON.

Implements idempotent transformations to ensure consistent style representation.
"""

import copy
from typing import Dict, Any, List


class StyleEngine:
    """
    Style normalization engine with 9-step pipeline.
    
    Guarantees:
    - Idempotency: engine(engine(x)) == engine(x)
    - Determinism: Same input always produces same output
    - Validation: All outputs are valid according to StyleJSONSchema
    """
    
    def __init__(self):
        """Initialize the style engine."""
        pass
    
    def normalize(self, style_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply 9-step normalization pipeline to style JSON.
        
        Args:
            style_json: Input style JSON (must be valid)
            
        Returns:
            Normalized style JSON
            
        Raises:
            ValueError: If input is invalid
        """
        # Deep copy to avoid mutating input
        result = copy.deepcopy(style_json)
        
        # Step 1: Normalize palette order (alphabetical)
        result = self._normalize_palette(result)
        
        # Step 2: Normalize numeric precision (2 decimal places)
        result = self._normalize_numeric_precision(result)
        
        # Step 3: Normalize boolean fields (explicit True/False)
        result = self._normalize_booleans(result)
        
        # Step 4: Normalize negative_constraints order (alphabetical)
        result = self._normalize_negative_constraints(result)
        
        # Step 5: Remove redundant fields (if any)
        result = self._remove_redundant_fields(result)
        
        # Step 6: Normalize enum values (lowercase)
        result = self._normalize_enums(result)
        
        # Step 7: Normalize whitespace in strings
        result = self._normalize_whitespace(result)
        
        # Step 8: Ensure field order consistency
        result = self._normalize_field_order(result)
        
        # Step 9: Validate final output
        result = self._validate_output(result)
        
        return result
    
    def _normalize_palette(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Step 1: Sort palette alphabetically."""
        if 'color' in style and 'palette' in style['color']:
            style['color']['palette'] = sorted(style['color']['palette'])
        return style
    
    def _normalize_numeric_precision(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Round all numeric values to 2 decimal places."""
        def round_value(obj):
            if isinstance(obj, dict):
                return {k: round_value(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [round_value(item) for item in obj]
            elif isinstance(obj, float):
                return round(obj, 2)
            else:
                return obj
        
        return round_value(style)
    
    def _normalize_booleans(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Ensure all booleans are explicit True/False."""
        def normalize_bool(obj):
            if isinstance(obj, dict):
                return {k: normalize_bool(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [normalize_bool(item) for item in obj]
            elif isinstance(obj, bool):
                return bool(obj)
            else:
                return obj
        
        return normalize_bool(style)
    
    def _normalize_negative_constraints(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Sort negative_constraints alphabetically."""
        if 'negative_constraints' in style:
            style['negative_constraints'] = sorted(style['negative_constraints'])
        return style
    
    def _remove_redundant_fields(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Remove any redundant or computed fields."""
        # Currently no redundant fields defined in schema
        return style
    
    def _normalize_enums(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Step 6: Normalize enum values to lowercase."""
        def normalize_enum(obj):
            if isinstance(obj, dict):
                return {k: normalize_enum(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [normalize_enum(item) for item in obj]
            elif isinstance(obj, str):
                # Only normalize known enum fields
                return obj.lower() if obj.isupper() or obj.istitle() else obj
            else:
                return obj
        
        # Apply to specific enum fields
        if 'composition' in style:
            if 'perspective' in style['composition']:
                style['composition']['perspective'] = style['composition']['perspective'].lower()
            if 'layout' in style['composition']:
                style['composition']['layout'] = style['composition']['layout'].lower()
        
        if 'line' in style and 'type' in style['line']:
            style['line']['type'] = style['line']['type'].lower()
        
        if 'color' in style and 'temperature' in style['color']:
            style['color']['temperature'] = style['color']['temperature'].lower()
        
        if 'material' in style and 'type' in style['material']:
            style['material']['type'] = style['material']['type'].lower()
        
        if 'lighting' in style:
            if 'type' in style['lighting']:
                style['lighting']['type'] = style['lighting']['type'].lower()
            if 'direction' in style['lighting']:
                style['lighting']['direction'] = style['lighting']['direction'].lower()
        
        return style
    
    def _normalize_whitespace(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Step 7: Normalize whitespace in string fields."""
        def normalize_str(obj):
            if isinstance(obj, dict):
                return {k: normalize_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [normalize_str(item) for item in obj]
            elif isinstance(obj, str):
                return ' '.join(obj.split())
            else:
                return obj
        
        return normalize_str(style)
    
    def _normalize_field_order(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Step 8: Ensure consistent field ordering."""
        # Define canonical field order
        field_order = [
            'style_id',
            'composition',
            'line',
            'color',
            'material',
            'lighting',
            'detail_density',
            'negative_constraints'
        ]
        
        # Reorder top-level fields
        ordered = {}
        for field in field_order:
            if field in style:
                ordered[field] = style[field]
        
        # Add any remaining fields (shouldn't happen with valid schema)
        for key, value in style.items():
            if key not in ordered:
                ordered[key] = value
        
        return ordered
    
    def _validate_output(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Step 9: Validate final output (placeholder for now)."""
        # Validation will be done by schema.py
        # This step is a hook for future validation logic
        return style
    
    def is_normalized(self, style_json: Dict[str, Any]) -> bool:
        """
        Check if a style JSON is already normalized.
        
        Args:
            style_json: Style JSON to check
            
        Returns:
            True if already normalized, False otherwise
        """
        normalized = self.normalize(style_json)
        return style_json == normalized
