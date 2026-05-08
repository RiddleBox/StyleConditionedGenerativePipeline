"""
Unit tests for ProductionMode
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from src.pipeline.production_mode import ProductionMode


@pytest.fixture
def mock_style():
    """Mock style JSON"""
    return {
        "palette": ["#FF0000", "#00FF00"],
        "color_temperature": "warm",
        "saturation_level": 0.8
    }


@pytest.fixture
def sample_image():
    """Create a sample image"""
    return Image.new("RGB", (100, 100), color="red")


class TestProductionMode:
    """Test suite for ProductionMode"""
    
    @patch('src.pipeline.production_mode.StyleLibrary')
    @patch('src.pipeline.production_mode.DALLEGenerator')
    def test_initialization(self, mock_dalle_class, mock_library_class):
        """Test production mode initialization"""
        pipeline = ProductionMode()
        
        assert pipeline.library is not None
        assert pipeline.prompt_generator is not None
        assert pipeline.dalle is not None
    
    @patch('src.pipeline.production_mode.StyleLibrary')
    @patch('src.pipeline.production_mode.DALLEGenerator')
    def test_generate_success(self, mock_dalle_class, mock_library_class, mock_style, sample_image):
        """Test successful image generation"""
        # Mock library
        mock_library = MagicMock()
        mock_library.get_style.return_value = mock_style
        mock_library_class.return_value = mock_library
        
        # Mock DALL-E
        mock_dalle = MagicMock()
        mock_dalle.generate.return_value = sample_image
        mock_dalle_class.return_value = mock_dalle
        
        pipeline = ProductionMode()
        image = pipeline.generate("test_style", "a cat")
        
        assert isinstance(image, Image.Image)
        mock_library.get_style.assert_called_once_with("test_style")
        mock_dalle.generate.assert_called_once()
    
    @patch('src.pipeline.production_mode.StyleLibrary')
    @patch('src.pipeline.production_mode.DALLEGenerator')
    def test_generate_style_not_found(self, mock_dalle_class, mock_library_class):
        """Test error when style not found"""
        mock_library = MagicMock()
        mock_library.get_style.return_value = None
        mock_library_class.return_value = mock_library
        
        pipeline = ProductionMode()
        
        with pytest.raises(ValueError, match="Style 'nonexistent' not found"):
            pipeline.generate("nonexistent", "a cat")
    
    @patch('src.pipeline.production_mode.StyleLibrary')
    @patch('src.pipeline.production_mode.DALLEGenerator')
    def test_generate_batch(self, mock_dalle_class, mock_library_class, mock_style, sample_image):
        """Test batch generation"""
        mock_library = MagicMock()
        mock_library.get_style.return_value = mock_style
        mock_library_class.return_value = mock_library
        
        mock_dalle = MagicMock()
        mock_dalle.generate.return_value = sample_image
        mock_dalle_class.return_value = mock_dalle
        
        pipeline = ProductionMode()
        subjects = ["cat", "dog", "bird"]
        images = pipeline.generate_batch("test_style", subjects)
        
        assert len(images) == 3
        assert all(isinstance(img, Image.Image) for img in images)
        assert mock_dalle.generate.call_count == 3
    
    @patch('src.pipeline.production_mode.StyleLibrary')
    @patch('src.pipeline.production_mode.DALLEGenerator')
    def test_list_available_styles(self, mock_dalle_class, mock_library_class):
        """Test listing available styles"""
        mock_library = MagicMock()
        mock_library.list_styles.return_value = ["style1", "style2", "style3"]
        mock_library_class.return_value = mock_library
        
        pipeline = ProductionMode()
        styles = pipeline.list_available_styles()
        
        assert len(styles) == 3
        assert "style1" in styles
    
    @patch('src.pipeline.production_mode.StyleLibrary')
    @patch('src.pipeline.production_mode.DALLEGenerator')
    def test_estimate_cost(self, mock_dalle_class, mock_library_class):
        """Test cost estimation"""
        mock_dalle = MagicMock()
        mock_dalle.estimate_cost.return_value = 0.40
        mock_dalle_class.return_value = mock_dalle
        
        pipeline = ProductionMode()
        cost = pipeline.estimate_cost(num_images=10)
        
        assert cost == 0.40
        mock_dalle.estimate_cost.assert_called_once_with(10)
