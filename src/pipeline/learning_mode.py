"""
Learning Mode Pipeline

Implements iterative optimization loop:
1. Extract style from reference image
2. Generate image from current style
3. Evaluate generated vs reference
4. Optimize style based on evaluation
5. Repeat until convergence or max iterations

Key features:
- Reference Style immutability
- Early stopping (score >= 0.9)
- Max iterations limit (default: 5)
- History tracking
"""

import copy
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from ..core.engine import StyleEngine
from ..core.prompt_generator import PromptGenerator
from ..optimizer.optimizer import StyleOptimizer


class LearningModePipeline:
    """
    Learning Mode Pipeline for iterative style optimization.
    
    Workflow:
    1. Initialize with reference style (extracted or provided)
    2. Iterate:
       a. Generate prompt from current style
       b. User/system generates image
       c. Evaluate image vs reference
       d. Optimize style based on evaluation
    3. Stop when converged or max iterations reached
    """
    
    def __init__(
        self,
        max_iterations: int = 5,
        target_score: float = 0.9,
        step_scale: float = 0.5
    ):
        """
        Initialize Learning Mode Pipeline.
        
        Args:
            max_iterations: Maximum number of optimization iterations
            target_score: Target score for early stopping
            step_scale: Optimizer step scale
        """
        self.max_iterations = max_iterations
        self.target_score = target_score
        
        # Initialize components
        self.engine = StyleEngine()
        self.prompt_generator = PromptGenerator()
        self.optimizer = StyleOptimizer(step_scale=step_scale)
        
        # State
        self.reference_style = None
        self.current_style = None
        self.history = []
    
    def initialize(
        self,
        reference_style: Dict[str, Any],
        normalize: bool = True
    ):
        """
        Initialize pipeline with reference style.
        
        Args:
            reference_style: Reference Style JSON
            normalize: Whether to normalize the style (default: True)
        """
        if normalize:
            self.reference_style = self.engine.normalize(reference_style)
        else:
            self.reference_style = copy.deepcopy(reference_style)
        
        # Initialize current style as copy of reference
        self.current_style = copy.deepcopy(self.reference_style)
        
        # Reset optimizer and history
        self.optimizer.reset()
        self.history = []
    
    def run_iteration(
        self,
        evaluation: Dict[str, Any],
        iteration: int
    ) -> Dict[str, Any]:
        """
        Run one optimization iteration.
        
        Args:
            evaluation: Evaluation result from previous iteration
            iteration: Current iteration number (0-indexed)
        
        Returns:
            Dict with iteration results:
            {
                'iteration': int,
                'current_style': dict,
                'evaluation': dict,
                'prompt': str,
                'negative_prompt': str,
                'frozen_fields': list,
                'converged': bool
            }
        """
        # Optimize style based on evaluation
        if iteration > 0:  # Skip optimization on first iteration
            self.current_style = self.optimizer.optimize(
                self.current_style,
                evaluation,
                iteration
            )
        
        # Generate prompt from current style
        prompt = self.prompt_generator.generate(self.current_style)
        negative_prompt = self.prompt_generator.get_negative_prompt(self.current_style)
        
        # Check convergence
        overall_score = evaluation.get('overall_score', 0.0)
        converged = overall_score >= self.target_score
        
        # Build result
        result = {
            'iteration': iteration,
            'current_style': copy.deepcopy(self.current_style),
            'evaluation': evaluation,
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'frozen_fields': self.optimizer.get_frozen_fields(),
            'converged': converged
        }
        
        # Add to history
        self.history.append(result)
        
        return result
    
    def should_continue(self, iteration: int, last_result: Dict[str, Any]) -> bool:
        """
        Check if optimization should continue.
        
        Args:
            iteration: Current iteration number
            last_result: Result from last iteration
        
        Returns:
            True if should continue, False otherwise
        """
        # Check max iterations
        if iteration >= self.max_iterations:
            return False
        
        # Check convergence
        if last_result.get('converged', False):
            return False
        
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of optimization process.
        
        Returns:
            Dict with summary:
            {
                'total_iterations': int,
                'final_score': float,
                'converged': bool,
                'frozen_fields': list,
                'score_history': list,
                'reference_style': dict,
                'final_style': dict
            }
        """
        if not self.history:
            return {
                'total_iterations': 0,
                'final_score': 0.0,
                'converged': False,
                'frozen_fields': [],
                'score_history': [],
                'reference_style': self.reference_style,
                'final_style': self.current_style
            }
        
        last_result = self.history[-1]
        
        return {
            'total_iterations': len(self.history),
            'final_score': last_result['evaluation'].get('overall_score', 0.0),
            'converged': last_result.get('converged', False),
            'frozen_fields': last_result.get('frozen_fields', []),
            'score_history': [
                r['evaluation'].get('overall_score', 0.0)
                for r in self.history
            ],
            'reference_style': self.reference_style,
            'final_style': self.current_style
        }
    
    def save_history(self, filepath: str):
        """
        Save optimization history to file.
        
        Args:
            filepath: Path to save history
        """
        import json
        
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': self.get_summary(),
                'history': self.history
            }, f, indent=2, ensure_ascii=False)
