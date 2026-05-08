"""
Auto Mode Pipeline

Fully automated end-to-end pipeline:
1. Extract style from reference image (LLM)
2. Generate image (DALL-E 3)
3. Evaluate quality (EvaluatorV2)
4. Optimize if needed (StyleOptimizer + LearningMode)
5. Save to library

Supports both Learning Mode (with optimization) and Production Mode (direct generation).
"""

from typing import Union, Optional, Dict
from pathlib import Path
from PIL import Image

from ..extractor.llm_extractor import LLMExtractor
from ..generator.dalle_generator import DALLEGenerator
from ..evaluator.evaluator_v2 import EvaluatorV2
from ..optimizer.optimizer import StyleOptimizer
from ..pipeline.learning_mode import LearningModePipeline
from ..pipeline.production_mode import ProductionMode
from ..core.library import StyleLibrary
from ..core.prompt_generator import PromptGenerator


class AutoModePipeline:
    """
    Fully automated pipeline with LLM extraction and API-driven generation.
    
    Two modes:
    1. Learning Mode: Extract → Generate → Evaluate → Optimize → Save
    2. Production Mode: Load from library → Generate
    """
    
    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: Optional[str] = None,
        dalle_model: str = "dall-e-3",
        dalle_size: str = "1024x1024",
        dalle_quality: str = "standard",
        library_path: str = "data/style_library.db"
    ):
        """
        Initialize auto mode pipeline.
        
        Args:
            llm_provider: "openai" or "anthropic"
            llm_model: LLM model name (defaults to provider's vision model)
            dalle_model: DALL-E model name
            dalle_size: Image size
            dalle_quality: "standard" or "hd"
            library_path: Path to style library database
        """
        # Initialize components
        self.extractor = LLMExtractor(provider=llm_provider, model=llm_model)
        self.generator = DALLEGenerator(
            model=dalle_model,
            size=dalle_size,
            quality=dalle_quality
        )
        self.evaluator = EvaluatorV2()
        self.optimizer = StyleOptimizer()
        self.library = StyleLibrary(db_path=library_path)
        self.prompt_generator = PromptGenerator()
        
        # Initialize sub-pipelines
        self.learning_mode = LearningModePipeline(library_path=library_path)
        self.production_mode = ProductionMode(
            library_path=library_path,
            dalle_model=dalle_model,
            dalle_size=dalle_size,
            dalle_quality=dalle_quality
        )
    
    def learn_from_reference(
        self,
        reference_image: Union[str, Image.Image],
        style_name: str,
        subject: str = "abstract art",
        max_iterations: int = 5,
        target_score: float = 0.85,
        save_to_library: bool = True,
        save_dir: Optional[Union[str, Path]] = None
    ) -> Dict:
        """
        Learning Mode: Extract style from reference and optimize through iteration.
        
        Args:
            reference_image: Reference image to learn from
            style_name: Name to save style as
            subject: Subject for test generation
            max_iterations: Maximum optimization iterations
            target_score: Target evaluation score (0-1)
            save_to_library: If True, save final style to library
            save_dir: Directory to save generated images (optional)
        
        Returns:
            Dict with:
            - final_style: Optimized style JSON
            - final_image: Best generated image
            - final_score: Best evaluation score
            - iterations: Number of iterations run
            - history: Optimization history
        """
        # Step 1: Extract initial style from reference
        print(f"Extracting style from reference image...")
        initial_style = self.extractor.extract_style(
            reference_image,
            stability_sampling=True,
            num_samples=3
        )
        
        # Step 2: Run learning mode optimization
        print(f"Starting optimization (max {max_iterations} iterations)...")
        result = self._run_learning_loop(
            reference_image=reference_image,
            initial_style=initial_style,
            subject=subject,
            max_iterations=max_iterations,
            target_score=target_score,
            save_dir=save_dir
        )
        
        # Step 3: Save to library if requested
        if save_to_library:
            print(f"Saving style '{style_name}' to library...")
            self.library.save_style(
                name=style_name,
                style=result['final_style'],
                metadata={
                    'source': 'auto_learning',
                    'iterations': result['iterations'],
                    'final_score': result['final_score']
                }
            )
        
        return result
    
    def generate_from_library(
        self,
        style_name: str,
        subject: str,
        save_path: Optional[Union[str, Path]] = None
    ) -> Image.Image:
        """
        Production Mode: Generate image using pre-saved style from library.
        
        Args:
            style_name: Name of style in library
            subject: Subject to generate
            save_path: Path to save image (optional)
        
        Returns:
            Generated PIL Image
        """
        return self.production_mode.generate(style_name, subject, save_path)
    
    def _run_learning_loop(
        self,
        reference_image: Union[str, Image.Image],
        initial_style: Dict,
        subject: str,
        max_iterations: int,
        target_score: float,
        save_dir: Optional[Union[str, Path]]
    ) -> Dict:
        """
        Run optimization loop with LLM extraction and DALL-E generation.
        
        Similar to LearningModePipeline but uses API-driven components.
        """
        current_style = initial_style
        best_style = initial_style
        best_score = 0.0
        best_image = None
        history = []
        
        for iteration in range(max_iterations):
            print(f"\nIteration {iteration + 1}/{max_iterations}")
            
            # Generate prompt
            prompt = self.prompt_generator.generate(current_style, subject=subject)
            print(f"  Prompt: {prompt[:100]}...")
            
            # Generate image
            print(f"  Generating image with DALL-E 3...")
            if save_dir:
                save_path = Path(save_dir) / f"iter_{iteration:02d}.png"
            else:
                save_path = None
            
            generated_image = self.generator.generate(prompt, save_path=save_path)
            
            # Evaluate
            print(f"  Evaluating...")
            eval_result = self.evaluator.evaluate(reference_image, generated_image)
            score = eval_result['overall_score']
            print(f"  Score: {score:.3f}")
            
            # Track history
            history.append({
                'iteration': iteration,
                'score': score,
                'style': current_style.copy()
            })
            
            # Update best
            if score > best_score:
                best_score = score
                best_style = current_style.copy()
                best_image = generated_image
                print(f"  ✓ New best score!")
            
            # Check convergence
            if score >= target_score:
                print(f"\n✓ Target score {target_score} reached!")
                break
            
            # Optimize style for next iteration
            if iteration < max_iterations - 1:
                print(f"  Optimizing style...")
                adjustments = self._compute_adjustments(eval_result)
                current_style = self.optimizer.apply_adjustments(current_style, adjustments)
        
        return {
            'final_style': best_style,
            'final_image': best_image,
            'final_score': best_score,
            'iterations': len(history),
            'history': history
        }
    
    def _compute_adjustments(self, eval_result: Dict) -> Dict:
        """
        Compute style adjustments based on evaluation result.
        
        Uses structured metrics to determine which parameters to adjust.
        """
        adjustments = {}
        structured = eval_result['structured_metrics']
        
        # Adjust based on low-scoring dimensions
        threshold = 0.7
        
        if structured['color'] < threshold:
            adjustments['saturation_level'] = 0.05
            adjustments['brightness_level'] = 0.05
        
        if structured['line'] < threshold:
            adjustments['line_weight'] = 0.05
            adjustments['line_density'] = 0.05
        
        if structured['lighting'] < threshold:
            adjustments['shadow_intensity'] = 0.05
        
        if structured['composition'] < threshold:
            adjustments['depth_of_field'] = 0.05
        
        if structured['material'] < threshold:
            adjustments['texture_scale'] = 0.05
        
        if structured['detail_density'] < threshold:
            adjustments['detail_level'] = 0.05
        
        return adjustments
    
    def list_available_styles(self) -> list:
        """List all styles in library"""
        return self.library.list_styles()
    
    def estimate_cost(
        self,
        mode: str = "learning",
        num_iterations: int = 5,
        num_images: int = 1
    ) -> float:
        """
        Estimate API cost.
        
        Args:
            mode: "learning" or "production"
            num_iterations: Number of iterations (for learning mode)
            num_images: Number of images (for production mode)
        
        Returns:
            Estimated cost in USD
        """
        if mode == "learning":
            # LLM extraction (3 samples) + DALL-E generation per iteration
            llm_cost = 0.01 * 3  # Rough estimate for vision API
            dalle_cost = self.generator.estimate_cost(num_iterations)
            return llm_cost + dalle_cost
        else:  # production
            return self.generator.estimate_cost(num_images)
