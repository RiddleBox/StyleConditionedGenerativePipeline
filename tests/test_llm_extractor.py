"""
Unit tests for LLMExtractor
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import numpy as np

from src.extractor.llm_extractor import LLMExtractor


@pytest.fixture
def sample_image():
    """Create a sample RGB image"""
    img = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    return Image.fromarray(img)


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "palette": ["#FF0000", "#00FF00", "#0000FF"],
        "color_temperature": "warm",
        "color_harmony": "complementary",
        "saturation_level": 0.8,
        "brightness_level": 0.7,
        "contrast_level": 0.6,
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
        "texture_scale": 0.6,
        "detail_level": 0.7
    }


class TestLLMExtractor:
    """Test suite for LLMExtractor"""
    
    def test_initialization_openai(self):
        """Test OpenAI initialization"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="openai")
            assert extractor.provider == "openai"
            assert extractor.model == "gpt-4-vision-preview"
            assert extractor.api_key == "test-key"
    
    def test_initialization_anthropic(self):
        """Test Anthropic initialization"""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="anthropic")
            assert extractor.provider == "anthropic"
            assert extractor.model == "claude-3-5-sonnet-20241022"
            assert extractor.api_key == "test-key"
    
    def test_initialization_missing_api_key(self):
        """Test that missing API key raises error"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                LLMExtractor(provider="openai")
    
    def test_initialization_custom_model(self):
        """Test initialization with custom model"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="openai", model="gpt-4-turbo")
            assert extractor.model == "gpt-4-turbo"
    
    def test_encode_image_pil(self, sample_image):
        """Test encoding PIL Image to base64"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="openai")
            encoded = extractor._encode_image(sample_image)
            
            assert isinstance(encoded, str)
            assert len(encoded) > 0
    
    def test_encode_image_resize_large(self):
        """Test that large images are resized"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="openai")
            
            # Create large image
            large_img = Image.new("RGB", (3000, 3000), color="red")
            encoded = extractor._encode_image(large_img)
            
            assert isinstance(encoded, str)
            # Image should be resized, so encoded size should be reasonable
            assert len(encoded) < 10_000_000  # Less than 10MB
    
    @patch('src.extractor.llm_extractor.OpenAI')
    def test_extract_style_openai(self, mock_openai_class, sample_image, mock_openai_response):
        """Test style extraction with OpenAI"""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = str(mock_openai_response).replace("'", '"')
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="openai")
            style = extractor.extract_style(sample_image)
            
            assert isinstance(style, dict)
            assert 'palette' in style
            assert 'color_temperature' in style
    
    def test_retry_mechanism(self, sample_image):
        """Test retry mechanism on API failure"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="openai", max_retries=3, retry_delay=0.1)
            
            # Mock API to fail twice then succeed
            with patch.object(extractor, '_call_llm') as mock_call:
                mock_call.side_effect = [
                    Exception("API Error 1"),
                    Exception("API Error 2"),
                    {"palette": ["#FF0000"], "color_temperature": "warm"}
                ]
                
                result = extractor._extract_single(sample_image)
                assert result is not None
                assert mock_call.call_count == 3
    
    def test_retry_exhaustion(self, sample_image):
        """Test that retry exhaustion raises error"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="openai", max_retries=2, retry_delay=0.1)
            
            # Mock API to always fail
            with patch.object(extractor, '_call_llm') as mock_call:
                mock_call.side_effect = Exception("API Error")
                
                with pytest.raises(RuntimeError, match="Failed after 2 attempts"):
                    extractor._extract_single(sample_image)
    
    def test_stability_sampling(self, sample_image):
        """Test stability sampling (multiple extractions)"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="openai")
            
            # Mock multiple extractions
            sample_styles = [
                {"saturation_level": 0.7, "color_temperature": "warm"},
                {"saturation_level": 0.8, "color_temperature": "warm"},
                {"saturation_level": 0.9, "color_temperature": "cool"}
            ]
            
            with patch.object(extractor, '_extract_single') as mock_extract:
                mock_extract.side_effect = sample_styles
                
                result = extractor.extract_style(sample_image, stability_sampling=True, num_samples=3)
                
                assert mock_extract.call_count == 3
                assert isinstance(result, dict)
                # Saturation should be averaged
                assert 'saturation_level' in result
                assert 0.7 <= result['saturation_level'] <= 0.9
    
    def test_merge_samples_numerical(self):
        """Test merging numerical values (averaging)"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="openai")
            
            samples = [
                {"saturation_level": 0.6},
                {"saturation_level": 0.8},
                {"saturation_level": 1.0}
            ]
            
            merged = extractor._merge_samples(samples)
            assert merged['saturation_level'] == pytest.approx(0.8, abs=0.01)
    
    def test_merge_samples_enumerated(self):
        """Test merging enumerated values (majority voting)"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="openai")
            
            samples = [
                {"color_temperature": "warm"},
                {"color_temperature": "warm"},
                {"color_temperature": "cool"}
            ]
            
            merged = extractor._merge_samples(samples)
            assert merged['color_temperature'] == "warm"  # Majority
    
    def test_merge_samples_palette(self):
        """Test merging palette (deduplicate and take top colors)"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            extractor = LLMExtractor(provider="openai")
            
            samples = [
                {"palette": ["#FF0000", "#00FF00", "#0000FF"]},
                {"palette": ["#FF0000", "#FF0000", "#FFFF00"]},
                {"palette": ["#FF0000", "#00FF00", "#000000"]}
            ]
            
            merged = extractor._merge_samples(samples)
            assert isinstance(merged['palette'], list)
            assert "#FF0000" in merged['palette']  # Most common
