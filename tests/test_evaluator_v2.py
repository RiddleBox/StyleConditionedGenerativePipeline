"""
Unit tests for EvaluatorV2
"""

import pytest
import numpy as np
from PIL import Image

from src.evaluator.evaluator_v2 import EvaluatorV2


@pytest.fixture
def evaluator():
    """Create an EvaluatorV2 instance"""
    return EvaluatorV2(device="cpu")


@pytest.fixture
def sample_image():
    """Create a sample RGB image"""
    img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    return Image.fromarray(img)


@pytest.fixture
def identical_images():
    """Create two identical images"""
    img_array = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    img1 = Image.fromarray(img_array)
    img2 = Image.fromarray(img_array.copy())
    return img1, img2


@pytest.fixture
def multiple_images():
    """Create multiple test images"""
    images = []
    for _ in range(3):
        img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        images.append(Image.fromarray(img))
    return images


class TestEvaluatorV2:
    """Test suite for EvaluatorV2"""
    
    def test_initialization(self):
        """Test evaluator initialization"""
        evaluator = EvaluatorV2(device="cpu")
        assert evaluator.clip_evaluator is not None
        assert evaluator.structured_metrics is not None
        assert evaluator.weights == {'global': 0.3, 'structured': 0.7}
    
    def test_custom_weights(self):
        """Test initialization with custom weights"""
        custom_weights = {'global': 0.5, 'structured': 0.5}
        evaluator = EvaluatorV2(weights=custom_weights)
        assert evaluator.weights == custom_weights
    
    def test_evaluate_returns_complete_result(self, evaluator, sample_image):
        """Test that evaluate() returns complete result structure"""
        result = evaluator.evaluate(sample_image, sample_image, return_details=True)
        
        assert isinstance(result, dict)
        assert 'global_similarity' in result
        assert 'structured_metrics' in result
        assert 'overall_score' in result
        assert 'weights' in result
        
        # Check structured metrics
        structured = result['structured_metrics']
        assert len(structured) == 6
        expected_keys = ['color', 'line', 'lighting', 'composition', 'material', 'detail_density']
        for key in expected_keys:
            assert key in structured
    
    def test_evaluate_without_details(self, evaluator, sample_image):
        """Test evaluate() with return_details=False"""
        result = evaluator.evaluate(sample_image, sample_image, return_details=False)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        assert 'global_similarity' not in result
        assert 'structured_metrics' not in result
    
    def test_identical_images_high_score(self, evaluator, identical_images):
        """Test that identical images get high overall score"""
        img1, img2 = identical_images
        result = evaluator.evaluate(img1, img2)
        
        assert result['overall_score'] >= 0.95
        assert result['global_similarity'] >= 0.95
        
        # All structured metrics should be high
        for key, value in result['structured_metrics'].items():
            assert value >= 0.95, f"{key} score {value} too low"
    
    def test_overall_score_calculation(self, evaluator, sample_image):
        """Test that overall score is correctly calculated from weights"""
        result = evaluator.evaluate(sample_image, sample_image)
        
        global_sim = result['global_similarity']
        structured_avg = np.mean(list(result['structured_metrics'].values()))
        
        expected_overall = (
            evaluator.weights['global'] * global_sim +
            evaluator.weights['structured'] * structured_avg
        )
        
        assert abs(result['overall_score'] - expected_overall) < 1e-6
    
    def test_evaluate_batch(self, evaluator, sample_image, multiple_images):
        """Test batch evaluation"""
        results = evaluator.evaluate_batch(sample_image, multiple_images)
        
        assert isinstance(results, list)
        assert len(results) == len(multiple_images)
        
        for result in results:
            assert 'overall_score' in result
            assert 'global_similarity' in result
            assert 'structured_metrics' in result
    
    def test_rank_by_overall_score(self, evaluator, sample_image, multiple_images):
        """Test ranking by overall score"""
        ranked = evaluator.rank_by_score(sample_image, multiple_images, score_key='overall_score')
        
        assert isinstance(ranked, list)
        assert len(ranked) == len(multiple_images)
        
        # Check structure: (index, score, result)
        for item in ranked:
            assert len(item) == 3
            idx, score, result = item
            assert isinstance(idx, int)
            assert isinstance(score, float)
            assert isinstance(result, dict)
        
        # Check that scores are in descending order
        scores = [item[1] for item in ranked]
        assert scores == sorted(scores, reverse=True)
    
    def test_rank_by_structured_metric(self, evaluator, sample_image, multiple_images):
        """Test ranking by a specific structured metric"""
        ranked = evaluator.rank_by_score(sample_image, multiple_images, score_key='color')
        
        assert isinstance(ranked, list)
        assert len(ranked) == len(multiple_images)
        
        # Check that scores are in descending order
        scores = [item[1] for item in ranked]
        assert scores == sorted(scores, reverse=True)
    
    def test_determinism(self, evaluator, sample_image):
        """Test that evaluation is deterministic"""
        result1 = evaluator.evaluate(sample_image, sample_image)
        result2 = evaluator.evaluate(sample_image, sample_image)
        
        # Overall scores should be identical
        assert abs(result1['overall_score'] - result2['overall_score']) < 1e-6
        
        # Global similarity should be identical
        assert abs(result1['global_similarity'] - result2['global_similarity']) < 1e-6
        
        # Structured metrics should be identical
        for key in result1['structured_metrics'].keys():
            diff = abs(result1['structured_metrics'][key] - result2['structured_metrics'][key])
            assert diff < 1e-6
