"""
CLIP-based Global Similarity Evaluator

Uses CLIP (openai/clip-vit-base-patch32) to compute global semantic similarity
between reference and generated images.
"""

import torch
from PIL import Image
from typing import Union, Tuple
import numpy as np


class CLIPEvaluator:
    """
    CLIP-based global similarity evaluator.
    
    Computes cosine similarity between image embeddings using CLIP.
    Guarantees determinism when using the same model and preprocessing.
    """
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", device: str = "auto"):
        """
        Initialize CLIP evaluator.
        
        Args:
            model_name: CLIP model to use (default: openai/clip-vit-base-patch32)
            device: Device to run on ("cpu", "cuda", or "auto")
        """
        self.model_name = model_name
        
        # Determine device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        # Lazy loading - will be initialized on first use
        self._model = None
        self._processor = None
    
    def _load_model(self):
        """Lazy load CLIP model and processor"""
        if self._model is None:
            from transformers import CLIPProcessor, CLIPModel
            
            self._processor = CLIPProcessor.from_pretrained(self.model_name)
            self._model = CLIPModel.from_pretrained(self.model_name).to(self.device)
            self._model.eval()  # Set to evaluation mode for determinism
    
    def compute_similarity(
        self,
        reference_image: Union[str, Image.Image, np.ndarray],
        generated_image: Union[str, Image.Image, np.ndarray]
    ) -> float:
        """
        Compute CLIP similarity between two images.
        
        Args:
            reference_image: Reference image (path, PIL Image, or numpy array)
            generated_image: Generated image (path, PIL Image, or numpy array)
        
        Returns:
            Cosine similarity score in [0, 1] (higher is more similar)
        """
        self._load_model()
        
        # Load images
        ref_img = self._load_image(reference_image)
        gen_img = self._load_image(generated_image)
        
        # Extract embeddings
        with torch.no_grad():
            ref_embedding = self._get_image_embedding(ref_img)
            gen_embedding = self._get_image_embedding(gen_img)
        
        # Compute cosine similarity
        similarity = torch.nn.functional.cosine_similarity(
            ref_embedding, gen_embedding, dim=0
        ).item()
        
        # Normalize to [0, 1] range (cosine similarity is in [-1, 1])
        normalized_similarity = (similarity + 1.0) / 2.0
        
        return normalized_similarity
    
    def _load_image(self, image: Union[str, Image.Image, np.ndarray]) -> Image.Image:
        """Load image from various formats"""
        if isinstance(image, str):
            return Image.open(image).convert("RGB")
        elif isinstance(image, Image.Image):
            return image.convert("RGB")
        elif isinstance(image, np.ndarray):
            return Image.fromarray(image).convert("RGB")
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
    
    def _get_image_embedding(self, image: Image.Image) -> torch.Tensor:
        """Extract CLIP embedding for an image"""
        # Preprocess image
        inputs = self._processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get image features
        image_features = self._model.get_image_features(**inputs)
        
        # Normalize embedding
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        return image_features.squeeze(0)
    
    def evaluate(
        self,
        reference_image: Union[str, Image.Image, np.ndarray],
        generated_image: Union[str, Image.Image, np.ndarray]
    ) -> dict:
        """
        Evaluate similarity and return structured result.
        
        Args:
            reference_image: Reference image
            generated_image: Generated image
        
        Returns:
            Dict with 'similarity_score' and metadata
        """
        similarity = self.compute_similarity(reference_image, generated_image)
        
        return {
            'similarity_score': similarity,
            'model': self.model_name,
            'device': self.device
        }
