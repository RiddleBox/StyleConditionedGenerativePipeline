"""
End-to-End Integration Tests for Learning Mode

Tests the complete Learning Mode workflow with mocked components:
1. Extract style (mocked)
2. Generate image (mocked)
3. Evaluate quality (mocked)
4. Optimize style
5. Iterate until convergence
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PIL import Image
import numpy as np

from src.pipeline.learning_mode import LearningModePipeline


@pytest.fixture
def sample_image():
    """Create a sample RGB image"""
    img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    return Image.fromarray(img)


@pytest.fixture
def mock_style():
    """Mock style JSON"""
    return {
        "palette": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"],
        "color_temperature": "warm",
        "color_harmony": "complementary",
        "saturation_level": 0.7,
        "brightness_level": 0.6,
        "contrast_level": 0.5,
        "line_style": "smooth",
        "line_weight": 0.5,
        "line_density": 0.4,
        "lighting_direction": "front",
        "lighting_quality": "soft",
        "shadow_intensity": 0.3,
        "composition_rule": "rule_of_thirds",
        "focal_point": "center",
        "depth_of_field": 0.5,
        "material_finish": "matte",
        "texture_scale": 0.5,
        "detail_level": 0.6
    }


class TestLearningModeE2E:
    """End-to-end tests for Learning Mode"""
    
    @patch('src.pipeline.learning_mode.StyleLibrary')
    def test_learning_mode_initialization(self, mock_library_class):
        """Test learning mode pipeline initialization"""
        pipeline = LearningModePipeline()
        
        assert pipeline.library is not None
        assert pipeline.prompt_generator is not None
        assert pipeline.optimizer is not None
    
    @patch('src.pipeline.learning_mode.StyleLibrary')
    def test_learning_loop_convergence(self, mock_library_class, sample_image, mock_style):
        """Test that learning loop converges to target score"""
        # Mock library
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library
        
        pipeline = LearningModePipeline()
        
        # Mock the internal methods
        with patch.object(pipeline, '_generate_image') as mock_gen, \
             patch.object(pipeline, '_evaluate_image') as mock_eval:
            
            # Simulate improving scores over iterations
            mock_gen.return_value = sample_image
            mock_eval.side_effect = [0.5, 0.6, 0.7, 0.8, 0.85]
            
            result = pipeline.run_learning_loop(
                reference_image=sample_image,
                initial_style=mock_style,
                subject="test",
                max_iterations=5,
                target_score=0.85
            )
            
            assert result['final_score'] >= 0.85
            assert result['iterations'] <= 5
            assert len(result['history']) > 0
    
    @patch('src.pipeline.learning_mode.StyleLibrary')
    def test_learning_loop_max_iterations(self, mock_library_class, sample_image, mock_style):
        """Test that learning loop respects max_iterations"""
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library
        
        pipeline = LearningModePipeline()
        
        with patch.object(pipeline, '_generate_image') as mock_gen, \
             patch.object(pipeline, '_evaluate_image') as mock_eval:
            
            # Simulate scores that never reach target
            mock_gen.return_value = sample_image
            mock_eval.return_value = 0.5
            
            result = pipeline.run_learning_loop(
                reference_image=sample_image,
                initial_style=mock_style,
                subject="test",
                max_iterations=3,
                target_score=0.9
            )
            
            assert result['iterations'] == 3
            assert result['final_score'] < 0.9
    
    @patch('src.pipeline.learning_mode.StyleLibrary')
    def test_optimization_improves_style(self, mock_library_class, sample_image, mock_style):
        """Test that optimizer improves style based on evaluation"""
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library
        
        pipeline = LearningModePipeline()
        
        # Simulate low scores that trigger adjustments
        eval_result = {
            'overall_score': 0.5,
            'structured_metrics': {
                'color': 0.4,
                'line': 0.5,
                'lighting': 0.6,
                'composition': 0.5,
                'material': 0.5,
                'detail_density': 0.5
            }
        }
        
        adjustments = pipeline._compute_adjustments(eval_result)
        
        # Should have adjustments for low-scoring dimensions
        assert len(adjustments) > 0
        assert 'saturation_level' in adjustments or 'brightness_level' in adjustments
    
    @patch('src.pipeline.learning_mode.StyleLibrary')
    def test_history_tracking(self, mock_library_class, sample_image, mock_style):
        """Test that optimization history is properly tracked"""
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library
        
        pipeline = LearningModePipeline()
        
        with patch.object(pipeline, '_generate_image') as mock_gen, \
             patch.object(pipeline, '_evaluate_image') as mock_eval:
            
            mock_gen.return_value = sample_image
            mock_eval.side_effect = [0.6, 0.7, 0.8]
            
            result = pipeline.run_learning_loop(
                reference_image=sample_image,
                initial_style=mock_style,
                subject="test",
                max_iterations=3,
                target_score=0.9
            )
            
            # Check history structure
            assert len(result['history']) == 3
            for entry in result['history']:
                assert 'iteration' in entry
                assert 'score' in entry
                assert 'style' in entry
    
    @patch('src.pipeline.learning_mode.StyleLibrary')
    def test_best_result_selection(self, mock_library_class, sample_image, mock_style):
        """Test that best result is selected across iterations"""
        mock_library = MagicMock()
        mock_library_class.return_value = mock_library
        
        pipeline = LearningModePipeline()
        
        with patch.object(pipeline, '_generate_image') as mock_gen, \
             patch.object(pipeline, '_evaluate_image') as mock_eval:
            
            mock_gen.return_value = sample_image
            # Scores: improve then decline
            mock_eval.side_effect = [0.6, 0.8, 0.7, 0.65]
            
            result = pipeline.run_learning_loop(
                reference_image=sample_image,
                initial_style=mock_style,
                subject="test",
                max_iterations=4,
                target_score=0.9
            )
            
            # Best score should be 0.8 (from iteration 2)
            assert result['final_score'] == 0.8
