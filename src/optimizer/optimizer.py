"""
Style Optimizer

Updates Style JSON based on evaluation feedback.
Only updates numeric fields (9 adjustable parameters).
Enum fields and palette are frozen.
"""

import copy
from typing import Dict, Any, List, Optional


class StyleOptimizer:
    """
    Style parameter optimizer.
    
    Updates Style JSON based on structured evaluation feedback.
    Implements:
    - Numeric field updates (9 adjustable parameters)
    - Enum field freezing
    - Convergence detection
    - History tracking
    """
    
    # Adjustable numeric fields (from three-way mapping table)
    ADJUSTABLE_FIELDS = [
        'color.saturation',
        'color.contrast',
        'line.width',
        'line.variation',
        'lighting.intensity',
        'composition.depth',
        'material.texture_strength',
        'detail_density.foreground',
        'detail_density.background'
    ]
    
    def __init__(
        self,
        step_scale: float = 0.5,
        convergence_threshold: float = 0.02,
        convergence_window: int = 3
    ):
        """
        Initialize optimizer.
        
        Args:
            step_scale: Scale factor for adjustments (default: 0.5)
            convergence_threshold: Threshold for detecting convergence (default: 0.02)
            convergence_window: Number of iterations to check for convergence (default: 3)
        """
        self.step_scale = step_scale
        self.convergence_threshold = convergence_threshold
        self.convergence_window = convergence_window
        
        # Track frozen fields
        self.frozen_fields = set()
        
        # History of changes per field
        self.field_history = {field: [] for field in self.ADJUSTABLE_FIELDS}
    
    def optimize(
        self,
        current_style: Dict[str, Any],
        evaluation: Dict[str, Any],
        iteration: int
    ) -> Dict[str, Any]:
        """
        Update Style JSON based on evaluation feedback.
        
        Args:
            current_style: Current Style JSON
            evaluation: Evaluation result with adjustments
            iteration: Current iteration number
        
        Returns:
            Updated Style JSON
        """
        # Deep copy to avoid mutating input
        updated_style = copy.deepcopy(current_style)
        
        # Extract adjustments from evaluation
        adjustments = evaluation.get('adjustments', {})
        
        if not adjustments:
            return updated_style
        
        # Apply adjustments to numeric fields
        for field_path, delta in adjustments.items():
            if field_path not in self.ADJUSTABLE_FIELDS:
                # Skip non-adjustable fields
                continue
            
            if field_path in self.frozen_fields:
                # Skip frozen fields
                continue
            
            # Apply adjustment
            self._apply_adjustment(updated_style, field_path, delta)
            
            # Track history
            self.field_history[field_path].append(delta)
            
            # Check for convergence
            if self._is_converged(field_path):
                self.frozen_fields.add(field_path)
        
        return updated_style
    
    def _apply_adjustment(
        self,
        style: Dict[str, Any],
        field_path: str,
        delta: float
    ):
        """
        Apply adjustment to a specific field.
        
        Args:
            style: Style JSON to modify (in-place)
            field_path: Dot-separated field path (e.g., 'color.saturation')
            delta: Adjustment value
        """
        # Parse field path
        parts = field_path.split('.')
        
        # Navigate to parent
        current = style
        for part in parts[:-1]:
            if part not in current:
                return  # Field doesn't exist
            current = current[part]
        
        # Get current value
        field_name = parts[-1]
        if field_name not in current:
            return
        
        current_value = current[field_name]
        
        # Apply scaled adjustment
        new_value = current_value + (delta * self.step_scale)
        
        # Clamp to valid range [0, 1] for most fields
        # Exception: line.width is [0, 5]
        if field_path == 'line.width':
            new_value = max(0.0, min(5.0, new_value))
        else:
            new_value = max(0.0, min(1.0, new_value))
        
        # Update value
        current[field_name] = round(new_value, 2)
    
    def _is_converged(self, field_path: str) -> bool:
        """
        Check if a field has converged.
        
        A field is considered converged if the last N adjustments
        are all below the convergence threshold.
        
        Args:
            field_path: Field to check
        
        Returns:
            True if converged, False otherwise
        """
        history = self.field_history[field_path]
        
        if len(history) < self.convergence_window:
            return False
        
        # Check last N adjustments
        recent = history[-self.convergence_window:]
        
        return all(abs(delta) < self.convergence_threshold for delta in recent)
    
    def get_frozen_fields(self) -> List[str]:
        """Get list of frozen fields"""
        return list(self.frozen_fields)
    
    def reset(self):
        """Reset optimizer state"""
        self.frozen_fields.clear()
        self.field_history = {field: [] for field in self.ADJUSTABLE_FIELDS}
