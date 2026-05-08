"""
LLM-based Style Extractor

Automatically extracts style parameters from reference images using LLM vision APIs.
Supports OpenAI GPT-4V and Anthropic Claude 3.5 Sonnet.
"""

import os
import time
import base64
from typing import Dict, Optional, Union, List
from pathlib import Path
from PIL import Image
import io


class LLMExtractor:
    """
    LLM-based style extractor with retry mechanism and stability sampling.
    
    Supports:
    - OpenAI GPT-4V (gpt-4-vision-preview)
    - Anthropic Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
    """
    
    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize LLM extractor.
        
        Args:
            provider: "openai" or "anthropic"
            model: Model name (defaults to provider's vision model)
            api_key: API key (defaults to env var)
            max_retries: Maximum retry attempts on failure
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.provider = provider.lower()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Set default models
        if model is None:
            if self.provider == "openai":
                self.model = "gpt-4-vision-preview"
            elif self.provider == "anthropic":
                self.model = "claude-3-5-sonnet-20241022"
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        else:
            self.model = model
        
        # Get API key
        if api_key is None:
            if self.provider == "openai":
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif self.provider == "anthropic":
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
            
            if not self.api_key:
                raise ValueError(f"API key not found for {provider}")
        else:
            self.api_key = api_key
        
        # Initialize client
        self._init_client()
    
    def _init_client(self):
        """Initialize API client"""
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
    
    def extract_style(
        self,
        image: Union[str, Image.Image],
        stability_sampling: bool = False,
        num_samples: int = 3
    ) -> Dict:
        """
        Extract style parameters from image using LLM.
        
        Args:
            image: Image path or PIL Image
            stability_sampling: If True, run multiple times and average results
            num_samples: Number of samples for stability sampling
        
        Returns:
            Style JSON dict
        """
        if stability_sampling:
            return self._extract_with_stability_sampling(image, num_samples)
        else:
            return self._extract_single(image)
    
    def _extract_single(self, image: Union[str, Image.Image]) -> Dict:
        """Extract style with retry mechanism"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return self._call_llm(image)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
        
        raise RuntimeError(f"Failed after {self.max_retries} attempts: {last_error}")
    
    def _extract_with_stability_sampling(
        self,
        image: Union[str, Image.Image],
        num_samples: int
    ) -> Dict:
        """
        Extract style multiple times and average numerical values.
        
        For enumerated fields, use majority voting.
        """
        samples = []
        for i in range(num_samples):
            style = self._extract_single(image)
            samples.append(style)
        
        # Merge samples
        return self._merge_samples(samples)
    
    def _call_llm(self, image: Union[str, Image.Image]) -> Dict:
        """Call LLM API to extract style"""
        # Load and encode image
        image_data = self._encode_image(image)
        
        # Build prompt
        prompt = self._build_extraction_prompt()
        
        # Call API
        if self.provider == "openai":
            return self._call_openai(prompt, image_data)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt, image_data)
    
    def _encode_image(self, image: Union[str, Image.Image]) -> str:
        """Encode image to base64"""
        if isinstance(image, str):
            img = Image.open(image)
        else:
            img = image
        
        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Resize if too large (max 2048px)
        max_size = 2048
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Encode to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    def _build_extraction_prompt(self) -> str:
        """Build style extraction prompt"""
        return """Analyze this image and extract its visual style parameters in JSON format.

Output a JSON object with these fields:

{
  "palette": ["#RRGGBB", ...],  // 5-8 dominant colors
  "color_temperature": "warm" | "cool" | "neutral",
  "color_harmony": "monochromatic" | "analogous" | "complementary" | "triadic" | "split_complementary",
  "saturation_level": 0.0-1.0,
  "brightness_level": 0.0-1.0,
  "contrast_level": 0.0-1.0,
  "line_style": "smooth" | "angular" | "organic" | "geometric" | "mixed",
  "line_weight": 0.0-1.0,
  "line_density": 0.0-1.0,
  "lighting_direction": "front" | "back" | "side" | "top" | "bottom" | "ambient",
  "lighting_quality": "hard" | "soft" | "mixed",
  "shadow_intensity": 0.0-1.0,
  "composition_rule": "rule_of_thirds" | "golden_ratio" | "symmetry" | "asymmetry" | "centered" | "dynamic",
  "focal_point": "center" | "left" | "right" | "top" | "bottom" | "multiple",
  "depth_of_field": 0.0-1.0,
  "material_finish": "matte" | "glossy" | "metallic" | "rough" | "smooth" | "mixed",
  "texture_scale": 0.0-1.0,
  "detail_level": 0.0-1.0
}

Return ONLY the JSON object, no explanation."""
    
    def _call_openai(self, prompt: str, image_data: str) -> Dict:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.0  # Deterministic
        )
        
        # Parse JSON response
        import json
        content = response.choices[0].message.content
        return json.loads(content)
    
    def _call_anthropic(self, prompt: str, image_data: str) -> Dict:
        """Call Anthropic API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.0,  # Deterministic
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        # Parse JSON response
        import json
        content = response.content[0].text
        return json.loads(content)
    
    def _merge_samples(self, samples: List[Dict]) -> Dict:
        """
        Merge multiple style samples.
        
        - Numerical fields: average
        - Enumerated fields: majority voting
        - Palette: merge and deduplicate
        """
        import numpy as np
        from collections import Counter
        
        merged = {}
        
        # Get all keys
        all_keys = set()
        for sample in samples:
            all_keys.update(sample.keys())
        
        for key in all_keys:
            values = [s[key] for s in samples if key in s]
            
            if not values:
                continue
            
            # Check value type
            if isinstance(values[0], (int, float)):
                # Numerical: average
                merged[key] = float(np.mean(values))
            elif isinstance(values[0], str):
                # Enumerated: majority voting
                counter = Counter(values)
                merged[key] = counter.most_common(1)[0][0]
            elif isinstance(values[0], list):
                # Palette: merge and deduplicate
                all_colors = []
                for v in values:
                    all_colors.extend(v)
                # Deduplicate and take top colors
                counter = Counter(all_colors)
                merged[key] = [color for color, _ in counter.most_common(8)]
        
        return merged
