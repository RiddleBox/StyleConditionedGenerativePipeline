"""
Unit tests for LearningModePipeline
"""

import pytest
import copy
from src.pipeline.learning_mode import LearningModePipeline


@pytest.fixture
def pipeline():
    """Create a LearningModePipeline instance"""
    return LearningModePipeline(max_iterations=5, target_score=0.9, step_scale=0.5)


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
    """Sample evaluation result"""
    return {
        'overall_score': 0.75,
        'global_similarity': 0.8,
        'structured_metrics': {
            'color': 0.85,
            'line': 0.7,
            'lighting': 0.75,
            'composition': 0.8,
            'material': 0.7,
            'detail_density': 0.7
        },
        'adjustments': {
            'color.saturation': 0.1,
            'lighting.intensity': -0.05
        }
    }


class TestLearningModePipeline:
    """Test suite for LearningModePipeline"""
    
    def test_initialization(self, pipeline):
        """Test pipeline initialization"""
        assert pipeline.max_iterations == 5
        assert pipeline.target_score == 0.9
        assert pipeline.reference_style is None
        assert pipeline.current_style is None
        assert len(pipeline.history) == 0
    
    def test_initialize_with_style(self, pipeline, sample_style):
        """Test initialize method"""
        pipeline.initialize(sample_style, normalize=False)
        
        assert pipeline.reference_style is not None
        assert pipeline.current_style is not None
        assert pipeline.reference_style == pipeline.current_style
        assert len(pipeline.history) == 0
    
    def test_initialize_does_not_mutate_input(self, pipeline, sample_style):
        """Test that initialize does not mutate input"""
        original = copy.deepcopy(sample_style)
        pipeline.initialize(sample_style, normalize=False)
        
        assert sample_style == original
    
    def test_reference_style_immutability(self, pipeline, sample_style, sample_evaluation):
        """Test that reference style remains unchanged"""
        pipeline.initialize(sample_style, normalize=False)
        
        original_ref = copy.deepcopy(pipeline.reference_style)
        
        # Run iteration
        pipeline.run_iteration(sample_evaluation, iteration=1)
        
        # Reference should not change
        assert pipeline.reference_style == original_ref
    
    def test_current_style_updates(self, pipeline, sample_style, sample_evaluation):
        """Test that current style is updated"""
        pipeline.initialize(sample_style, normalize=False)
        
        original_saturation = pipeline.current_style['color']['saturation']
        
        # Run iteration
        pipeline.run_iteration(sample_evaluation, iteration=1)
        
        # Current style should change
        assert pipeline.current_style['color']['saturation'] != original_saturation
    
    def test_run_iteration_returns_result(self, pipeline, sample_style, sample_evaluation):
        """Test that run_iteration returns proper result"""
        pipeline.initialize(sample_style, normalize=False)
        
        result = pipeline.run_iteration(sample_evaluation, iteration=0)
        
        assert 'iteration' in result
        assert 'current_style' in result
        assert 'evaluation' in result
        assert 'prompt' in result
        assert 'negative_prompt' in result
        assert 'frozen_fields' in result
        assert 'converged' in result
    
    def test_convergence_detection(self, pipeline, sample_style):
        """Test convergence detection"""
        pipeline.initialize(sample_style, normalize=False)
        
        # High score evaluation
        high_score_eval = {
            'overall_score': 0.95,
            'adjustments': {}
        }
        
        result = pipeline.run_iteration(high_score_eval, iteration=0)
        
        assert result['converged'] is True
    
    def test_should_continue_max_iterations(self, pipeline, sample_style, sample_evaluation):
        """Test should_continue respects max_iterations"""
        pipeline.initialize(sample_style, normalize=False)
        
        result = {'converged': False}
        
        # Should continue before max
        assert pipeline.should_continue(3, result) is True
        
        # Should stop at max
        assert pipeline.should_continue(5, result) is False
    
    def test_should_continue_convergence(self, pipeline, sample_style):
        """Test should_continue respects convergence"""
        pipeline.initialize(sample_style, normalize=False)
        
        converged_result = {'converged': True}
        
        # Should stop when converged
        assert pipeline.should_continue(2, converged_result) is False
    
    def test_history_tracking(self, pipeline, sample_style, sample_evaluation):
        """Test that history is tracked"""
        pipeline.initialize(sample_style, normalize=False)
        
        # Run 3 iterations
        for i in range(3):
            pipeline.run_iteration(sample_evaluation, iteration=i)
        
        assert len(pipeline.history) == 3
    
    def test_get_summary(self, pipeline, sample_style, sample_evaluation):
        """Test get_summary method"""
        pipeline.initialize(sample_style, normalize=False)
        
        # Run 2 iterations
        pipeline.run_iteration(sample_evaluation, iteration=0)
        pipeline.run_iteration(sample_evaluation, iteration=1)
        
        summary = pipeline.get_summary()
        
        assert summary['total_iterations'] == 2
        assert 'final_score' in summary
        assert 'converged' in summary
        assert 'frozen_fields' in summary
        assert 'score_history' in summary
        assert len(summary['score_history']) == 2
        assert 'reference_style' in summary
        assert 'final_style' in summary
    
    def test_get_summary_empty(self, pipeline, sample_style):
        """Test get_summary with no history"""
        pipeline.initialize(sample_style, normalize=False)
        
        summary = pipeline.get_summary()
        
        assert summary['total_iterations'] == 0
        assert summary['final_score'] == 0.0
        assert summary['converged'] is False
    
    def test_save_history(self, pipeline, sample_style, sample_evaluation, tmp_path):
        """Test save_history method"""
        pipeline.initialize(sample_style, normalize=False)
        
        # Run iteration
        pipeline.run_iteration(sample_evaluation, iteration=0)
        
        # Save history
        output_path = tmp_path / "history.json"
        pipeline.save_history(str(output_path))
        
        assert output_path.exists()
        
        # Verify content
        import json
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        assert 'summary' in data
        assert 'history' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
