"""
Unit tests for StyleOptimizer
"""

import pytest
from src.optimizer.optimizer import StyleOptimizer


@pytest.fixture
def optimizer():
    """Create a StyleOptimizer instance"""
    return StyleOptimizer(step_scale=0.5, convergence_threshold=0.02, convergence_window=3)


@pytest.fixture
def sample_style():
    """Sample Style JSON for testing"""
    return {
        'style_id': 'test-001',
        'composition': {'perspective': 'isometric', 'layout': 'centered', 'depth': 0.5},
        'line': {'type': 'clean', 'width': 2.0, 'variation': 0.3, 'locked': False},
        'color': {'palette': ['#FF0000', '#00FF00'], 'saturation': 0.7, 'contrast': 0.6, 'temperature': 'warm'},
        'material': {'type': 'flat', 'texture_strength': 0.4, 'locked': False},
        'lighting': {'type': 'ambient', 'direction': 'top', 'intensity': 0.8},
        'detail_density': {'foreground': 0.7, 'background': 0.3},
        'negative_constraints': []
    }


@pytest.fixture
def sample_evaluation():
    """Sample evaluation with adjustments"""
    return {
        'overall_score': 0.75,
        'adjustments': {
            'color.saturation': 0.1,
            'lighting.intensity': -0.05,
            'line.width': 0.2
        }
    }


class TestStyleOptimizer:
    """Test suite for StyleOptimizer"""
    
    def test_initialization(self, optimizer):
        """Test optimizer initialization"""
        assert optimizer.step_scale == 0.5
        assert optimizer.convergence_threshold == 0.02
        assert optimizer.convergence_window == 3
        assert len(optimizer.frozen_fields) == 0
    
    def test_optimize_applies_adjustments(self, optimizer, sample_style, sample_evaluation):
        """Test that optimize applies adjustments correctly"""
        updated = optimizer.optimize(sample_style, sample_evaluation, iteration=1)
        
        # Check that adjustments were applied (scaled by step_scale=0.5)
        assert updated['color']['saturation'] == pytest.approx(0.7 + 0.1 * 0.5, abs=0.01)
        assert updated['lighting']['intensity'] == pytest.approx(0.8 - 0.05 * 0.5, abs=0.01)
        assert updated['line']['width'] == pytest.approx(2.0 + 0.2 * 0.5, abs=0.01)
    
    def test_optimize_does_not_mutate_input(self, optimizer, sample_style, sample_evaluation):
        """Test that optimize does not mutate input style"""
        original_saturation = sample_style['color']['saturation']
        optimizer.optimize(sample_style, sample_evaluation, iteration=1)
        assert sample_style['color']['saturation'] == original_saturation
    
    def test_optimize_clamps_to_valid_range(self, optimizer, sample_style):
        """Test that values are clamped to valid ranges"""
        evaluation = {
            'overall_score': 0.5,
            'adjustments': {
                'color.saturation': 2.0,  # Would exceed 1.0
                'lighting.intensity': -2.0  # Would go below 0.0
            }
        }
        
        updated = optimizer.optimize(sample_style, evaluation, iteration=1)
        
        # Should be clamped to [0, 1]
        assert 0.0 <= updated['color']['saturation'] <= 1.0
        assert 0.0 <= updated['lighting']['intensity'] <= 1.0
    
    def test_optimize_line_width_range(self, optimizer, sample_style):
        """Test that line.width is clamped to [0, 5]"""
        evaluation = {
            'overall_score': 0.5,
            'adjustments': {
                'line.width': 10.0  # Would exceed 5.0
            }
        }
        
        updated = optimizer.optimize(sample_style, evaluation, iteration=1)
        
        # Should be clamped to [0, 5]
        assert 0.0 <= updated['line']['width'] <= 5.0
    
    def test_convergence_detection(self, optimizer, sample_style):
        """Test convergence detection mechanism"""
        # Apply small adjustments 3 times
        for i in range(3):
            evaluation = {
                'overall_score': 0.8,
                'adjustments': {'color.saturation': 0.01}  # Small adjustment
            }
            optimizer.optimize(sample_style, evaluation, iteration=i)
        
        # Field should be frozen after 3 small adjustments
        assert 'color.saturation' in optimizer.frozen_fields
    
    def test_frozen_fields_not_updated(self, optimizer, sample_style):
        """Test that frozen fields are not updated"""
        # Freeze a field
        optimizer.frozen_fields.add('color.saturation')
        
        original_saturation = sample_style['color']['saturation']
        
        evaluation = {
            'overall_score': 0.7,
            'adjustments': {'color.saturation': 0.2}
        }
        
        updated = optimizer.optimize(sample_style, evaluation, iteration=1)
        
        # Saturation should not change
        assert updated['color']['saturation'] == original_saturation
    
    def test_ignores_non_adjustable_fields(self, optimizer, sample_style):
        """Test that non-adjustable fields are ignored"""
        evaluation = {
            'overall_score': 0.7,
            'adjustments': {
                'color.temperature': 'cool',  # Enum field, not adjustable
                'color.palette': ['#000000']  # Palette, not adjustable
            }
        }
        
        updated = optimizer.optimize(sample_style, evaluation, iteration=1)
        
        # These fields should not change
        assert updated['color']['temperature'] == sample_style['color']['temperature']
        assert updated['color']['palette'] == sample_style['color']['palette']
    
    def test_reset(self, optimizer, sample_style, sample_evaluation):
        """Test reset functionality"""
        # Apply some optimizations
        optimizer.optimize(sample_style, sample_evaluation, iteration=1)
        optimizer.frozen_fields.add('color.saturation')
        
        # Reset
        optimizer.reset()
        
        # State should be cleared
        assert len(optimizer.frozen_fields) == 0
        assert all(len(history) == 0 for history in optimizer.field_history.values())
    
    def test_get_frozen_fields(self, optimizer):
        """Test get_frozen_fields method"""
        optimizer.frozen_fields.add('color.saturation')
        optimizer.frozen_fields.add('line.width')
        
        frozen = optimizer.get_frozen_fields()
        
        assert 'color.saturation' in frozen
        assert 'line.width' in frozen
        assert len(frozen) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
