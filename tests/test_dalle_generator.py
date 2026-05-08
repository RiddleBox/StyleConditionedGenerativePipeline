"""
Unit tests for DALLEGenerator
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io

from src.generator.dalle_generator import DALLEGenerator


@pytest.fixture
def mock_dalle_response():
    """Mock DALL-E API response"""
    mock_response = MagicMock()
    mock_response.data = [MagicMock()]
    mock_response.data[0].url = "https://example.com/image.png"
    return mock_response


@pytest.fixture
def sample_image_bytes():
    """Create sample image bytes"""
    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


class TestDALLEGenerator:
    """Test suite for DALLEGenerator"""
    
    def test_initialization(self):
        """Test generator initialization"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            generator = DALLEGenerator()
            assert generator.model == "dall-e-3"
            assert generator.size == "1024x1024"
            assert generator.quality == "standard"
            assert generator.api_key == "test-key"
    
    def test_initialization_missing_api_key(self):
        """Test that missing API key raises error"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
                DALLEGenerator()
    
    def test_initialization_custom_params(self):
        """Test initialization with custom parameters"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            generator = DALLEGenerator(
                model="dall-e-2",
                size="512x512",
                quality="hd"
            )
            assert generator.model == "dall-e-2"
            assert generator.size == "512x512"
            assert generator.quality == "hd"
    
    @patch('src.generator.dalle_generator.OpenAI')
    @patch('src.generator.dalle_generator.requests.get')
    def test_generate_success(self, mock_requests, mock_openai_class, mock_dalle_response, sample_image_bytes):
        """Test successful image generation"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.generate.return_value = mock_dalle_response
        
        # Mock image download
        mock_response = MagicMock()
        mock_response.content = sample_image_bytes
        mock_requests.return_value = mock_response
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            generator = DALLEGenerator()
            image = generator.generate("a red cat")
            
            assert isinstance(image, Image.Image)
            mock_client.images.generate.assert_called_once()
    
    @patch('src.generator.dalle_generator.OpenAI')
    def test_generate_retry_mechanism(self, mock_openai_class):
        """Test retry mechanism on API failure"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Mock API to fail twice then succeed
        mock_client.images.generate.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            MagicMock(data=[MagicMock(url="https://example.com/image.png")])
        ]
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch.object(DALLEGenerator, '_download_image') as mock_download:
                mock_download.return_value = Image.new("RGB", (100, 100))
                
                generator = DALLEGenerator(max_retries=3, retry_delay=0.1)
                image = generator.generate("test prompt")
                
                assert isinstance(image, Image.Image)
                assert mock_client.images.generate.call_count == 3
    
    @patch('src.generator.dalle_generator.OpenAI')
    def test_generate_retry_exhaustion(self, mock_openai_class):
        """Test that retry exhaustion raises error"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.generate.side_effect = Exception("API Error")
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            generator = DALLEGenerator(max_retries=2, retry_delay=0.1)
            
            with pytest.raises(RuntimeError, match="Failed after 2 attempts"):
                generator.generate("test prompt")
    
    @patch('src.generator.dalle_generator.requests.get')
    def test_download_image(self, mock_requests, sample_image_bytes):
        """Test image download from URL"""
        mock_response = MagicMock()
        mock_response.content = sample_image_bytes
        mock_requests.return_value = mock_response
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            generator = DALLEGenerator()
            image = generator._download_image("https://example.com/image.png")
            
            assert isinstance(image, Image.Image)
            mock_requests.assert_called_once()
    
    def test_estimate_cost_dalle3_standard_1024(self):
        """Test cost estimation for DALL-E 3 standard 1024x1024"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            generator = DALLEGenerator(model="dall-e-3", size="1024x1024", quality="standard")
            cost = generator.estimate_cost(num_images=10)
            assert cost == 0.40  # $0.04 per image * 10
    
    def test_estimate_cost_dalle3_hd_1024(self):
        """Test cost estimation for DALL-E 3 HD 1024x1024"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            generator = DALLEGenerator(model="dall-e-3", size="1024x1024", quality="hd")
            cost = generator.estimate_cost(num_images=5)
            assert cost == 0.40  # $0.08 per image * 5
    
    def test_estimate_cost_dalle3_standard_1792(self):
        """Test cost estimation for DALL-E 3 standard 1792x1024"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            generator = DALLEGenerator(model="dall-e-3", size="1792x1024", quality="standard")
            cost = generator.estimate_cost(num_images=5)
            assert cost == 0.40  # $0.08 per image * 5
    
    def test_estimate_cost_dalle3_hd_1792(self):
        """Test cost estimation for DALL-E 3 HD 1792x1024"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            generator = DALLEGenerator(model="dall-e-3", size="1792x1024", quality="hd")
            cost = generator.estimate_cost(num_images=5)
            assert cost == 0.60  # $0.12 per image * 5
    
    @patch('src.generator.dalle_generator.OpenAI')
    @patch('src.generator.dalle_generator.requests.get')
    def test_generate_batch(self, mock_requests, mock_openai_class, mock_dalle_response, sample_image_bytes):
        """Test batch generation"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.images.generate.return_value = mock_dalle_response
        
        mock_response = MagicMock()
        mock_response.content = sample_image_bytes
        mock_requests.return_value = mock_response
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            generator = DALLEGenerator()
            prompts = ["cat", "dog", "bird"]
            images = generator.generate_batch(prompts)
            
            assert len(images) == 3
            assert all(isinstance(img, Image.Image) for img in images)
            assert mock_client.images.generate.call_count == 3
