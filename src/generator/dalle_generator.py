"""
DALL-E 3 Image Generator

Generates images using OpenAI's DALL-E 3 API.
"""

import os
import time
import requests
from typing import Optional, Union
from pathlib import Path
from PIL import Image
import io


class DALLEGenerator:
    """
    DALL-E 3 image generator with retry mechanism.
    
    Supports:
    - DALL-E 3 (1024x1024, 1024x1792, 1792x1024)
    - Automatic image download and saving
    - Retry on API failures
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        max_retries: int = 3,
        retry_delay: float = 2.0
    ):
        """
        Initialize DALL-E generator.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (dall-e-3 or dall-e-2)
            size: Image size (1024x1024, 1024x1792, 1792x1024 for DALL-E 3)
            quality: "standard" or "hd"
            max_retries: Maximum retry attempts on failure
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.model = model
        self.size = size
        self.quality = quality
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Get API key
        if api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found")
        else:
            self.api_key = api_key
        
        # Initialize client
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(
        self,
        prompt: str,
        save_path: Optional[Union[str, Path]] = None,
        return_image: bool = True
    ) -> Union[Image.Image, str, None]:
        """
        Generate image from prompt.
        
        Args:
            prompt: Text prompt for image generation
            save_path: Path to save generated image (optional)
            return_image: If True, return PIL Image; if False, return URL
        
        Returns:
            PIL Image, URL string, or None (if saved to file)
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # Call DALL-E API
                response = self.client.images.generate(
                    model=self.model,
                    prompt=prompt,
                    size=self.size,
                    quality=self.quality,
                    n=1
                )
                
                # Get image URL
                image_url = response.data[0].url
                
                # Download image
                image = self._download_image(image_url)
                
                # Save if path provided
                if save_path:
                    save_path = Path(save_path)
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    image.save(save_path)
                
                # Return based on flag
                if return_image:
                    return image
                else:
                    return image_url
                
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
        
        raise RuntimeError(f"Failed after {self.max_retries} attempts: {last_error}")
    
    def generate_batch(
        self,
        prompts: list,
        save_dir: Optional[Union[str, Path]] = None,
        return_images: bool = True
    ) -> list:
        """
        Generate multiple images from prompts.
        
        Args:
            prompts: List of text prompts
            save_dir: Directory to save images (optional)
            return_images: If True, return PIL Images; if False, return URLs
        
        Returns:
            List of PIL Images or URLs
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            if save_dir:
                save_path = Path(save_dir) / f"image_{i:03d}.png"
            else:
                save_path = None
            
            result = self.generate(prompt, save_path, return_images)
            results.append(result)
        
        return results
    
    def _download_image(self, url: str) -> Image.Image:
        """Download image from URL"""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        image_data = io.BytesIO(response.content)
        return Image.open(image_data)
    
    def estimate_cost(self, num_images: int = 1) -> float:
        """
        Estimate generation cost in USD.
        
        DALL-E 3 pricing (as of 2024):
        - Standard 1024x1024: $0.040 per image
        - Standard 1024x1792 or 1792x1024: $0.080 per image
        - HD 1024x1024: $0.080 per image
        - HD 1024x1792 or 1792x1024: $0.120 per image
        """
        if self.model == "dall-e-3":
            if self.quality == "hd":
                if self.size == "1024x1024":
                    cost_per_image = 0.080
                else:
                    cost_per_image = 0.120
            else:  # standard
                if self.size == "1024x1024":
                    cost_per_image = 0.040
                else:
                    cost_per_image = 0.080
        elif self.model == "dall-e-2":
            cost_per_image = 0.020  # 1024x1024
        else:
            cost_per_image = 0.0
        
        return cost_per_image * num_images
