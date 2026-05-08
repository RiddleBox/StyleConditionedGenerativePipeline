"""
Production Mode Pipeline

Loads pre-saved styles from Style Library and generates images directly.
No optimization loop - single-shot generation for production use.
"""

from typing import Union, Optional
from pathlib import Path
from PIL import Image

from ..core.library import StyleLibrary
from ..core.prompt_generator import PromptGenerator
from ..generator.dalle_generator import DALLEGenerator


class ProductionMode:
    """
    Production mode pipeline for fast, single-shot image generation.
    
    Workflow:
    1. Load style from library by name
    2. Generate prompt from style
    3. Generate image with DALL-E 3
    4. Return image
    
    No evaluation or optimization - assumes style is already tuned.
    """
    
    def __init__(
        self,
        library_path: str = "data/style_library.db",
        dalle_model: str = "dall-e-3",
        dalle_size: str = "1024x1024",
        dalle_quality: str = "standard"
    ):
        """
        Initialize production mode pipeline.
        
        Args:
            library_path: Path to style library database
            dalle_model: DALL-E model name
            dalle_size: Image size
            dalle_quality: "standard" or "hd"
        """
        self.library = StyleLibrary(db_path=library_path)
        self.prompt_generator = PromptGenerator()
        self.dalle = DALLEGenerator(
            model=dalle_model,
            size=dalle_size,
            quality=dalle_quality
        )
    
    def generate(
        self,
        style_name: str,
        subject: str,
        save_path: Optional[Union[str, Path]] = None
    ) -> Image.Image:
        """
        Generate image using pre-saved style.
        
        Args:
            style_name: Name of style in library
            subject: Subject to generate (e.g., "a cat", "a landscape")
            save_path: Path to save generated image (optional)
        
        Returns:
            Generated PIL Image
        """
        # Load style from library
        style = self.library.get_style(style_name)
        if style is None:
            raise ValueError(f"Style '{style_name}' not found in library")
        
        # Generate prompt
        prompt = self.prompt_generator.generate(style, subject=subject)
        
        # Generate image
        image = self.dalle.generate(prompt, save_path=save_path)
        
        return image
    
    def generate_batch(
        self,
        style_name: str,
        subjects: list,
        save_dir: Optional[Union[str, Path]] = None
    ) -> list:
        """
        Generate multiple images with the same style.
        
        Args:
            style_name: Name of style in library
            subjects: List of subjects to generate
            save_dir: Directory to save images (optional)
        
        Returns:
            List of generated PIL Images
        """
        # Load style once
        style = self.library.get_style(style_name)
        if style is None:
            raise ValueError(f"Style '{style_name}' not found in library")
        
        images = []
        for i, subject in enumerate(subjects):
            # Generate prompt
            prompt = self.prompt_generator.generate(style, subject=subject)
            
            # Generate image
            if save_dir:
                save_path = Path(save_dir) / f"{style_name}_{i:03d}.png"
            else:
                save_path = None
            
            image = self.dalle.generate(prompt, save_path=save_path)
            images.append(image)
        
        return images
    
    def list_available_styles(self) -> list:
        """List all available styles in library"""
        return self.library.list_styles()
    
    def estimate_cost(self, num_images: int = 1) -> float:
        """Estimate generation cost"""
        return self.dalle.estimate_cost(num_images)
