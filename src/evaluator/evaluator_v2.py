"""
EvaluatorV2: Two-Level Evaluation System

Level 1: CLIP Global Similarity (0-1 score)
Level 2: Structured Style Metrics (6 dimensional scores)

Usage:
    evaluator = EvaluatorV2()
    result = evaluator.evaluate(reference_image, generated_image)
    
    # result = {
    #     'global_similarity': 0.85,
    #     'structured_metrics': {
    #         'color': 0.92,
    #         'line': 0.78,
    #         'lighting': 0.88,
    #         'composition': 0.81,
    #         'material': 0.75,
    #         'detail_density': 0.83
    #     },
    #     'overall_score': 0.84
    # }
"""

from typing import Union, Dict
from PIL import Image
import numpy as np

from .clip_evaluator import CLIPEvaluator
from .structured_metrics import StructuredMetrics


class EvaluatorV2:
    """
    Two-level evaluation system for style-conditioned image generation.
    
    Combines:
    - Level 1: CLIP global similarity (semantic alignment)
    - Level 2: Structured style metrics (6 dimensions)
    
    Provides both detailed breakdown and overall score.
    """
    
    def __init__(
        self,
        clip_model: str = "openai/clip-vit-base-patch32",
        device: str = "auto",
        weights: Dict[str, float] = None
    ):
        """
        Initialize EvaluatorV2.
        
        Args:
            clip_model: CLIP model name
            device: Device to run on ("cpu", "cuda", or "auto")
            weights: Custom weights for overall score calculation
                     Default: {'global': 0.3, 'structured': 0.7}
        """
        self.clip_evaluator = CLIPEvaluator(model_name=clip_model, device=device)
        self.structured_metrics = StructuredMetrics()
        
        # Default weights: structured metrics are more important
        self.weights = weights or {
            'global': 0.3,
            'structured': 0.7
        }
    
    def evaluate(
        self,
        reference_image: Union[str, Image.Image, np.ndarray],
        generated_image: Union[str, Image.Image, np.ndarray],
        return_details: bool = True
    ) -> Dict:
        """
        Evaluate generated image against reference.
        
        Args:
            reference_image: Reference image (path, PIL Image, or numpy array)
            generated_image: Generated image (path, PIL Image, or numpy array)
            return_details: If True, return full breakdown; if False, only overall score
        
        Returns:
            Dict with evaluation results:
            {
                'global_similarity': float,
                'structured_metrics': {
                    'color': float,
                    'line': float,
                    'lighting': float,
                    'composition': float,
                    'material': float,
                    'detail_density': float
                },
                'overall_score': float
            }
        """
        # Level 1: CLIP global similarity
        clip_result = self.clip_evaluator.evaluate(reference_image, generated_image)
        global_similarity = clip_result['similarity_score']
        
        # Level 2: Structured metrics
        structured_scores = self.structured_metrics.evaluate(reference_image, generated_image)
        
        # Compute overall score
        structured_avg = np.mean(list(structured_scores.values()))
        overall_score = (
            self.weights['global'] * global_similarity +
            self.weights['structured'] * structured_avg
        )
        
        if return_details:
            return {
                'global_similarity': global_similarity,
                'structured_metrics': structured_scores,
                'overall_score': overall_score,
                'weights': self.weights
            }
        else:
            return {
                'overall_score': overall_score
            }
    
    def evaluate_batch(
        self,
        reference_image: Union[str, Image.Image, np.ndarray],
        generated_images: list,
        return_details: bool = True
    ) -> list:
        """
        Evaluate multiple generated images against the same reference.
        
        Args:
            reference_image: Reference image
            generated_images: List of generated images
            return_details: If True, return full breakdown for each
        
        Returns:
            List of evaluation results (one per generated image)
        """
        results = []
        for gen_img in generated_images:
            result = self.evaluate(reference_image, gen_img, return_details=return_details)
            results.append(result)
        
        return results
    
    def rank_by_score(
        self,
        reference_image: Union[str, Image.Image, np.ndarray],
        generated_images: list,
        score_key: str = 'overall_score'
    ) -> list:
        """
        Rank generated images by evaluation score.
        
        Args:
            reference_image: Reference image
            generated_images: List of generated images
            score_key: Which score to rank by ('overall_score', 'global_similarity', 
                       or any structured metric key)
        
        Returns:
            List of (index, score, result) tuples, sorted by score (descending)
        """
        results = self.evaluate_batch(reference_image, generated_images, return_details=True)
        
        # Extract scores
        ranked = []
        for idx, result in enumerate(results):
            if score_key == 'overall_score' or score_key == 'global_similarity':
                score = result[score_key]
            else:
                # Structured metric key
                score = result['structured_metrics'].get(score_key, 0.0)
            
            ranked.append((idx, score, result))
        
        # Sort by score (descending)
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        return ranked
