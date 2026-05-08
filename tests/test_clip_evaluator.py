"""
Unit tests for CLIPEvaluator
"""

import pytest
import numpy as np
from PIL import Image
import torch

from src.evaluator.clip_evaluator import CLIPEvaluator


@pytest.fixture
def evaluator():
    """Create a CLIPEvaluator instance"""
    return CLIPEvaluator(device="cpu")


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
def different_images():
    """Create two different images"""
    img1 = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    img2 = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    return Image.fromarray(img1), Image.fromarray(img2)


class TestCLIPEvaluator:
    """Test suite for CLIPEvaluator"""
    
    def test_initialization(self):
        """Test evaluator initialization"""
        evaluator = CLIPEvaluator(device="cpu")
        assert evaluator.model_name == "openai/clip-vit-base-patch32"
        assert evaluator.device == "cpu"
        assert evaluator._model is None  # Lazy loading
    
    def test_device_auto_selection(self):
        """Test automatic device selection"""
        evaluator = CLIPEvaluator(device="auto")
        expected_device = "cuda" if torch.cuda.is_available() else "cpu"
        assert evaluator.device == expected_device
    
    def test_compute_similarity_identical_images(self, evaluator, identical_images):
        """Test similarity computation for identical images"""
        img1, img2 = identical_images
        similarity = evaluator.compute_similarity(img1, img2)
        
        # Identical images should have very high similarity (close to 1.0)
        assert 0.95 <= similarity <= 1.0
        assert isinstance(similarity, float)
    
    def test_compute_similarity_different_images(self, evaluator, different_images):
        """Test similarity computation for different images"""
        img1, img2 = different_images
        similarity = evaluator.compute_similarity(img1, img2)
        
        # Different random images should have lower similarity
        assert 0.0 <= similarity <= 1.0
        assert isinstance(similarity, float)
    
    def test_compute_similarity_determinism(self, evaluator, sample_image):
        """Test that similarity computation is deterministic"""
        # Compute similarity twice
        similarity1 = evaluator.compute_similarity(sample_image, sample_image)
        similarity2 = evaluator.compute_similarity(sample_image, sample_image)
        
        # Should be identical (deterministic)
        assert abs(similarity1 - similarity2) < 1e-6
    
    def test_evaluate_returns_dict(self, evaluator, sample_image):
        """Test that evaluate() returns a structured dict"""
        result = evaluator.evaluate(sample_image, sample_image)
        
        assert isinstance(result, dict)
        assert 'similarity_score' in result
        assert 'model' in result
        assert 'device' in result
        assert result['model'] == "openai/clip-vit-base-patch32"
    
    def test_load_image_from_pil(self, evaluator):
        """Test loading PIL Image"""
        img = Image.new("RGB", (100, 100), color="red")
        loaded = evaluator._load_image(img)
        
        assert isinstance(loaded, Image.Image)
        assert loaded.mode == "RGB"
    
    def test_load_image_from_numpy(self, evaluator):
        """Test loading numpy array"""
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        loaded = evaluator._load_image(img_array)
        
        assert isinstance(loaded, Image.Image)
        assert loaded.mode == "RGB"
    
    def test_similarity_range(self, evaluator, sample_image):
        """Test that similarity scores are in valid range [0, 1]"""
        # Test with multiple random images
        for _ in range(5):
            random_img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
            random_img = Image.fromarray(random_img)
            
            similarity = evaluator.compute_similarity(sample_image, random_img)
            assert 0.0 <= similarity <= 1.0
