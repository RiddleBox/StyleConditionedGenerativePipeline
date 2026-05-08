"""
Unit tests for StructuredMetrics
"""

import pytest
import numpy as np
from PIL import Image

from src.evaluator.structured_metrics import StructuredMetrics


@pytest.fixture
def metrics():
    """Create a StructuredMetrics instance"""
    return StructuredMetrics()


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
def solid_color_images():
    """Create two solid color images"""
    img1 = Image.new("RGB", (256, 256), color="red")
    img2 = Image.new("RGB", (256, 256), color="blue")
    return img1, img2


class TestStructuredMetrics:
    """Test suite for StructuredMetrics"""
    
    def test_initialization(self):
        """Test metrics initialization"""
        metrics = StructuredMetrics()
        assert metrics is not None
    
    def test_evaluate_returns_six_dimensions(self, metrics, sample_image):
        """Test that evaluate() returns all 6 dimensions"""
        scores = metrics.evaluate(sample_image, sample_image)
        
        assert isinstance(scores, dict)
        assert len(scores) == 6
        
        expected_keys = ['color', 'line', 'lighting', 'composition', 'material', 'detail_density']
        for key in expected_keys:
            assert key in scores
            assert isinstance(scores[key], float)
    
    def test_scores_in_valid_range(self, metrics, sample_image):
        """Test that all scores are in [0, 1] range"""
        scores = metrics.evaluate(sample_image, sample_image)
        
        for key, value in scores.items():
            assert 0.0 <= value <= 1.0, f"{key} score {value} out of range"
    
    def test_identical_images_high_scores(self, metrics, identical_images):
        """Test that identical images get high scores"""
        img1, img2 = identical_images
        scores = metrics.evaluate(img1, img2)
        
        # All scores should be very high (close to 1.0)
        for key, value in scores.items():
            assert value >= 0.95, f"{key} score {value} too low for identical images"
    
    def test_color_metric(self, metrics, solid_color_images):
        """Test color metric on solid color images"""
        red_img, blue_img = solid_color_images
        
        # Same color should have high score
        same_color_score = metrics._evaluate_color(
            np.array(red_img), np.array(red_img)
        )
        assert same_color_score >= 0.95
        
        # Different colors should have lower score
        diff_color_score = metrics._evaluate_color(
            np.array(red_img), np.array(blue_img)
        )
        assert diff_color_score < same_color_score
    
    def test_line_metric(self, metrics):
        """Test line metric on edge images"""
        # Create image with edges
        img_with_edges = np.zeros((256, 256, 3), dtype=np.uint8)
        img_with_edges[100:150, :] = 255  # Horizontal line
        
        # Same edges should have high score
        score = metrics._evaluate_line(img_with_edges, img_with_edges)
        assert score >= 0.95
    
    def test_lighting_metric(self, metrics):
        """Test lighting metric on brightness variations"""
        # Create bright and dark images
        bright_img = np.full((256, 256, 3), 200, dtype=np.uint8)
        dark_img = np.full((256, 256, 3), 50, dtype=np.uint8)
        
        # Same brightness should have high score
        same_score = metrics._evaluate_lighting(bright_img, bright_img)
        assert same_score >= 0.95
        
        # Different brightness should have lower score
        diff_score = metrics._evaluate_lighting(bright_img, dark_img)
        assert diff_score < same_score
    
    def test_composition_metric(self, metrics):
        """Test composition metric on spatial layouts"""
        # Create image with specific spatial pattern
        img = np.zeros((256, 256, 3), dtype=np.uint8)
        img[:128, :] = 255  # Top half white
        
        # Same composition should have high score
        score = metrics._evaluate_composition(img, img)
        assert score >= 0.95
    
    def test_material_metric(self, metrics):
        """Test material/texture metric"""
        # Create textured image (checkerboard pattern)
        img = np.zeros((256, 256, 3), dtype=np.uint8)
        for i in range(0, 256, 32):
            for j in range(0, 256, 32):
                if (i // 32 + j // 32) % 2 == 0:
                    img[i:i+32, j:j+32] = 255
        
        # Same texture should have high score
        score = metrics._evaluate_material(img, img)
        assert score >= 0.95
    
    def test_detail_density_metric(self, metrics):
        """Test detail density metric"""
        # Create high-detail image (random noise)
        high_detail = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        
        # Create low-detail image (solid color)
        low_detail = np.full((256, 256, 3), 128, dtype=np.uint8)
        
        # Same detail level should have high score
        same_score = metrics._evaluate_detail_density(high_detail, high_detail)
        assert same_score >= 0.95
        
        # Different detail levels should have lower score
        diff_score = metrics._evaluate_detail_density(high_detail, low_detail)
        assert diff_score < same_score
    
    def test_determinism(self, metrics, sample_image):
        """Test that metrics are deterministic"""
        # Compute metrics twice
        scores1 = metrics.evaluate(sample_image, sample_image)
        scores2 = metrics.evaluate(sample_image, sample_image)
        
        # Should be identical (within floating point precision)
        for key in scores1.keys():
            assert abs(scores1[key] - scores2[key]) < 1e-6
    
    def test_load_image_formats(self, metrics):
        """Test loading different image formats"""
        # PIL Image
        pil_img = Image.new("RGB", (100, 100), color="red")
        loaded_pil = metrics._load_image(pil_img)
        assert isinstance(loaded_pil, np.ndarray)
        assert loaded_pil.shape == (100, 100, 3)
        
        # Numpy array
        np_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        loaded_np = metrics._load_image(np_img)
        assert isinstance(loaded_np, np.ndarray)
        assert loaded_np.shape == (100, 100, 3)
