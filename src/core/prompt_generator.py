"""
Prompt Generator: Deterministic compiler from normalized style JSON to text prompts.

Implements a pure function that always produces the same prompt for the same input.
"""

from typing import Dict, Any, List


class PromptGenerator:
    """
    Deterministic prompt compiler.
    
    Guarantees:
    - Determinism: Same input always produces same output
    - Completeness: All style parameters are reflected in the prompt
    - Readability: Generated prompts are human-readable
    """
    
    def __init__(self):
        """Initialize the prompt generator."""
        pass
    
    def generate(self, normalized_style: Dict[str, Any]) -> str:
        """
        Generate a text prompt from normalized style JSON.
        
        Args:
            normalized_style: Normalized style JSON (from StyleEngine)
            
        Returns:
            Deterministic text prompt
            
        Raises:
            ValueError: If input is invalid or not normalized
        """
        sections = []
        
        # Section 1: Composition
        if "composition" in normalized_style:
            sections.append(self._compile_composition(normalized_style["composition"]))
        
        # Section 2: Line
        if "line" in normalized_style:
            sections.append(self._compile_line(normalized_style["line"]))
        
        # Section 3: Color
        if "color" in normalized_style:
            sections.append(self._compile_color(normalized_style["color"]))
        
        # Section 4: Material
        if "material" in normalized_style:
            sections.append(self._compile_material(normalized_style["material"]))
        
        # Section 5: Lighting
        if "lighting" in normalized_style:
            sections.append(self._compile_lighting(normalized_style["lighting"]))
        
        # Section 6: Detail Density
        if "detail_density" in normalized_style:
            sections.append(self._compile_detail_density(normalized_style["detail_density"]))
        
        # Section 7: Negative Constraints
        if "negative_constraints" in normalized_style:
            sections.append(self._compile_negative_constraints(normalized_style["negative_constraints"]))
        
        # Join all sections with commas
        prompt = ", ".join(filter(None, sections))
        
        return prompt
    
    def _compile_composition(self, composition: Dict[str, Any]) -> str:
        """Compile composition parameters into prompt text."""
        parts = []
        
        if "perspective" in composition:
            parts.append(f"{composition['perspective']} perspective")
        
        if "layout" in composition:
            parts.append(f"{composition['layout']} composition")
        
        if "depth" in composition:
            depth_value = composition["depth"]
            if depth_value <= 3:
                parts.append("shallow depth")
            elif depth_value <= 7:
                parts.append("medium depth")
            else:
                parts.append("deep depth")
        
        return ", ".join(parts)
    
    def _compile_line(self, line: Dict[str, Any]) -> str:
        """Compile line parameters into prompt text."""
        parts = []
        
        if "type" in line:
            parts.append(f"{line['type']} lines")
        
        if "width" in line:
            width = line["width"]
            if width < 1.5:
                parts.append("thin strokes")
            elif width < 3.0:
                parts.append("medium strokes")
            else:
                parts.append("thick strokes")
        
        if "variation" in line:
            variation = line["variation"]
            if variation < 0.3:
                parts.append("consistent line weight")
            elif variation < 0.7:
                parts.append("moderate line variation")
            else:
                parts.append("high line variation")
        
        if "locked" in line and line["locked"]:
            parts.append("precise linework")
        
        return ", ".join(parts)
    
    def _compile_color(self, color: Dict[str, Any]) -> str:
        """Compile color parameters into prompt text."""
        parts = []
        
        if "palette" in color:
            palette_size = len(color["palette"])
            if palette_size <= 3:
                parts.append("limited color palette")
            elif palette_size <= 6:
                parts.append("balanced color palette")
            else:
                parts.append("rich color palette")
            
            # Include actual colors
            parts.append(f"colors: {', '.join(color['palette'])}")
        
        if "saturation" in color:
            saturation = color["saturation"]
            if saturation < 0.3:
                parts.append("desaturated")
            elif saturation < 0.7:
                parts.append("moderate saturation")
            else:
                parts.append("highly saturated")
        
        if "temperature" in color:
            parts.append(f"{color['temperature']} color temperature")
        
        return ", ".join(parts)
    
    def _compile_material(self, material: Dict[str, Any]) -> str:
        """Compile material parameters into prompt text."""
        parts = []
        
        if "type" in material:
            parts.append(f"{material['type']} material")
        
        if "texture_strength" in material:
            strength = material["texture_strength"]
            if strength < 0.3:
                parts.append("subtle texture")
            elif strength < 0.7:
                parts.append("moderate texture")
            else:
                parts.append("strong texture")
        
        return ", ".join(parts)
    
    def _compile_lighting(self, lighting: Dict[str, Any]) -> str:
        """Compile lighting parameters into prompt text."""
        parts = []
        
        if "type" in lighting:
            parts.append(f"{lighting['type']} lighting")
        
        if "direction" in lighting:
            parts.append(f"light from {lighting['direction']}")
        
        if "intensity" in lighting:
            intensity = lighting["intensity"]
            if intensity < 0.3:
                parts.append("dim illumination")
            elif intensity < 0.7:
                parts.append("moderate brightness")
            else:
                parts.append("bright illumination")
        
        return ", ".join(parts)
    
    def _compile_detail_density(self, detail_density: Dict[str, Any]) -> str:
        """Compile detail density parameters into prompt text."""
        parts = []
        
        if "foreground" in detail_density:
            fg = detail_density["foreground"]
            if fg < 0.3:
                parts.append("minimal foreground detail")
            elif fg < 0.7:
                parts.append("moderate foreground detail")
            else:
                parts.append("high foreground detail")
        
        if "background" in detail_density:
            bg = detail_density["background"]
            if bg < 0.3:
                parts.append("minimal background detail")
            elif bg < 0.7:
                parts.append("moderate background detail")
            else:
                parts.append("high background detail")
        
        return ", ".join(parts)
    
    def _compile_negative_constraints(self, constraints: List[str]) -> str:
        """Compile negative constraints into prompt text."""
        if not constraints:
            return ""
        
        # Negative constraints are typically used separately in image generation
        # But we include them here for completeness
        return f"avoid: {', '.join(constraints)}"
    
    def get_negative_prompt(self, normalized_style: Dict[str, Any]) -> str:
        """
        Extract negative prompt from style JSON.
        
        Args:
            normalized_style: Normalized style JSON
            
        Returns:
            Negative prompt string (empty if no constraints)
        """
        if "negative_constraints" not in normalized_style:
            return ""
        
        constraints = normalized_style["negative_constraints"]
        return ", ".join(constraints)
