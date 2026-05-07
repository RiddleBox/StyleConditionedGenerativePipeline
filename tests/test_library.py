"""
Unit tests for Style Library.

Tests CRUD operations and SQLite persistence.
"""

import pytest
import os
from pathlib import Path
from src.core.library import StyleLibrary


class TestStyleLibrary:
    """Test StyleLibrary initialization and basic functionality."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database for testing."""
        db_path = tmp_path / "test_styles.db"
        return str(db_path)
    
    @pytest.fixture
    def library(self, temp_db):
        """Create a StyleLibrary instance with temporary database."""
        return StyleLibrary(temp_db)
    
    def test_library_initialization(self, library):
        """Test that StyleLibrary can be instantiated."""
        assert library is not None
    
    def test_database_file_created(self, temp_db, library):
        """Test that database file is created."""
        assert os.path.exists(temp_db)
    
    def test_initial_count_zero(self, library):
        """Test that initial count is zero."""
        assert library.count() == 0
    
    def _get_valid_style(self):
        """Helper: Return a valid style JSON for testing."""
        return {
            "style_id": "test-style-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            },
            "line": {
                "type": "clean",
                "width": 2.5,
                "variation": 0.1,
                "locked": True
            },
            "color": {
                "palette": ["#3357FF", "#33FF57", "#FF5733"],
                "saturation": 0.8,
                "temperature": "warm"
            },
            "material": {
                "type": "matte",
                "texture_strength": 0.3
            },
            "lighting": {
                "type": "soft",
                "direction": "top-left",
                "intensity": 0.7
            },
            "detail_density": {
                "foreground": 0.9,
                "background": 0.3
            },
            "negative_constraints": ["blurry", "distorted", "low quality"]
        }


class TestCreate:
    """Test create operation."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database for testing."""
        db_path = tmp_path / "test_styles.db"
        return str(db_path)
    
    @pytest.fixture
    def library(self, temp_db):
        """Create a StyleLibrary instance with temporary database."""
        return StyleLibrary(temp_db)
    
    def test_create_success(self, library):
        """Test successful creation."""
        style = self._get_valid_style()
        result = library.create(style)
        assert result is True
    
    def test_create_duplicate_fails(self, library):
        """Test that creating duplicate style_id fails."""
        style = self._get_valid_style()
        library.create(style)
        result = library.create(style)
        assert result is False
    
    def test_create_missing_style_id(self, library):
        """Test that creating without style_id raises ValueError."""
        style = {"composition": {"perspective": "isometric"}}
        with pytest.raises(ValueError):
            library.create(style)
    
    def test_create_increments_count(self, library):
        """Test that create increments count."""
        style = self._get_valid_style()
        library.create(style)
        assert library.count() == 1
    
    def _get_valid_style(self):
        """Helper: Return a valid style JSON for testing."""
        return {
            "style_id": "test-style-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            },
            "line": {
                "type": "clean",
                "width": 2.5,
                "variation": 0.1,
                "locked": True
            },
            "color": {
                "palette": ["#3357FF", "#33FF57", "#FF5733"],
                "saturation": 0.8,
                "temperature": "warm"
            },
            "material": {
                "type": "matte",
                "texture_strength": 0.3
            },
            "lighting": {
                "type": "soft",
                "direction": "top-left",
                "intensity": 0.7
            },
            "detail_density": {
                "foreground": 0.9,
                "background": 0.3
            },
            "negative_constraints": ["blurry", "distorted", "low quality"]
        }


class TestRead:
    """Test read operation."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database for testing."""
        db_path = tmp_path / "test_styles.db"
        return str(db_path)
    
    @pytest.fixture
    def library(self, temp_db):
        """Create a StyleLibrary instance with temporary database."""
        return StyleLibrary(temp_db)
    
    def test_read_existing(self, library):
        """Test reading existing style."""
        style = self._get_valid_style()
        library.create(style)
        
        result = library.read("test-style-001")
        
        assert result is not None
        assert result["style_id"] == "test-style-001"
    
    def test_read_non_existing(self, library):
        """Test reading non-existing style returns None."""
        result = library.read("non-existing-id")
        assert result is None
    
    def test_read_returns_same_data(self, library):
        """Test that read returns the same data that was created."""
        style = self._get_valid_style()
        library.create(style)
        
        result = library.read("test-style-001")
        
        assert result == style
    
    def _get_valid_style(self):
        """Helper: Return a valid style JSON for testing."""
        return {
            "style_id": "test-style-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            },
            "line": {
                "type": "clean",
                "width": 2.5,
                "variation": 0.1,
                "locked": True
            },
            "color": {
                "palette": ["#3357FF", "#33FF57", "#FF5733"],
                "saturation": 0.8,
                "temperature": "warm"
            },
            "material": {
                "type": "matte",
                "texture_strength": 0.3
            },
            "lighting": {
                "type": "soft",
                "direction": "top-left",
                "intensity": 0.7
            },
            "detail_density": {
                "foreground": 0.9,
                "background": 0.3
            },
            "negative_constraints": ["blurry", "distorted", "low quality"]
        }


class TestUpdate:
    """Test update operation."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database for testing."""
        db_path = tmp_path / "test_styles.db"
        return str(db_path)
    
    @pytest.fixture
    def library(self, temp_db):
        """Create a StyleLibrary instance with temporary database."""
        return StyleLibrary(temp_db)
    
    def test_update_existing(self, library):
        """Test updating existing style."""
        style = self._get_valid_style()
        library.create(style)
        
        # Modify style
        style["composition"]["depth"] = 8
        result = library.update(style)
        
        assert result is True
    
    def test_update_non_existing(self, library):
        """Test updating non-existing style returns False."""
        style = self._get_valid_style()
        result = library.update(style)
        assert result is False
    
    def test_update_changes_data(self, library):
        """Test that update actually changes the data."""
        style = self._get_valid_style()
        library.create(style)
        
        # Modify style
        style["composition"]["depth"] = 8
        library.update(style)
        
        # Read back
        result = library.read("test-style-001")
        assert result["composition"]["depth"] == 8
    
    def test_update_missing_style_id(self, library):
        """Test that updating without style_id raises ValueError."""
        style = {"composition": {"perspective": "isometric"}}
        with pytest.raises(ValueError):
            library.update(style)
    
    def _get_valid_style(self):
        """Helper: Return a valid style JSON for testing."""
        return {
            "style_id": "test-style-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            },
            "line": {
                "type": "clean",
                "width": 2.5,
                "variation": 0.1,
                "locked": True
            },
            "color": {
                "palette": ["#3357FF", "#33FF57", "#FF5733"],
                "saturation": 0.8,
                "temperature": "warm"
            },
            "material": {
                "type": "matte",
                "texture_strength": 0.3
            },
            "lighting": {
                "type": "soft",
                "direction": "top-left",
                "intensity": 0.7
            },
            "detail_density": {
                "foreground": 0.9,
                "background": 0.3
            },
            "negative_constraints": ["blurry", "distorted", "low quality"]
        }


class TestDelete:
    """Test delete operation."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database for testing."""
        db_path = tmp_path / "test_styles.db"
        return str(db_path)
    
    @pytest.fixture
    def library(self, temp_db):
        """Create a StyleLibrary instance with temporary database."""
        return StyleLibrary(temp_db)
    
    def test_delete_existing(self, library):
        """Test deleting existing style."""
        style = self._get_valid_style()
        library.create(style)
        
        result = library.delete("test-style-001")
        
        assert result is True
    
    def test_delete_non_existing(self, library):
        """Test deleting non-existing style returns False."""
        result = library.delete("non-existing-id")
        assert result is False
    
    def test_delete_removes_data(self, library):
        """Test that delete actually removes the data."""
        style = self._get_valid_style()
        library.create(style)
        library.delete("test-style-001")
        
        result = library.read("test-style-001")
        assert result is None
    
    def test_delete_decrements_count(self, library):
        """Test that delete decrements count."""
        style = self._get_valid_style()
        library.create(style)
        library.delete("test-style-001")
        
        assert library.count() == 0
    
    def _get_valid_style(self):
        """Helper: Return a valid style JSON for testing."""
        return {
            "style_id": "test-style-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            },
            "line": {
                "type": "clean",
                "width": 2.5,
                "variation": 0.1,
                "locked": True
            },
            "color": {
                "palette": ["#3357FF", "#33FF57", "#FF5733"],
                "saturation": 0.8,
                "temperature": "warm"
            },
            "material": {
                "type": "matte",
                "texture_strength": 0.3
            },
            "lighting": {
                "type": "soft",
                "direction": "top-left",
                "intensity": 0.7
            },
            "detail_density": {
                "foreground": 0.9,
                "background": 0.3
            },
            "negative_constraints": ["blurry", "distorted", "low quality"]
        }


class TestListAndQuery:
    """Test list and query operations."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create a temporary database for testing."""
        db_path = tmp_path / "test_styles.db"
        return str(db_path)
    
    @pytest.fixture
    def library(self, temp_db):
        """Create a StyleLibrary instance with temporary database."""
        return StyleLibrary(temp_db)
    
    def test_list_all_empty(self, library):
        """Test list_all on empty library."""
        result = library.list_all()
        assert result == []
    
    def test_list_all_single(self, library):
        """Test list_all with single style."""
        style = self._get_valid_style()
        library.create(style)
        
        result = library.list_all()
        
        assert len(result) == 1
        assert result[0]["style_id"] == "test-style-001"
    
    def test_list_all_multiple(self, library):
        """Test list_all with multiple styles."""
        style1 = self._get_valid_style()
        style2 = self._get_valid_style()
        style2["style_id"] = "test-style-002"
        
        library.create(style1)
        library.create(style2)
        
        result = library.list_all()
        
        assert len(result) == 2
    
    def test_list_all_sorted(self, library):
        """Test that list_all returns sorted results."""
        style1 = self._get_valid_style()
        style2 = self._get_valid_style()
        style2["style_id"] = "test-style-002"
        style3 = self._get_valid_style()
        style3["style_id"] = "test-style-000"
        
        library.create(style1)
        library.create(style2)
        library.create(style3)
        
        result = library.list_all()
        
        assert result[0]["style_id"] == "test-style-000"
        assert result[1]["style_id"] == "test-style-001"
        assert result[2]["style_id"] == "test-style-002"
    
    def test_exists_true(self, library):
        """Test exists returns True for existing style."""
        style = self._get_valid_style()
        library.create(style)
        
        assert library.exists("test-style-001") is True
    
    def test_exists_false(self, library):
        """Test exists returns False for non-existing style."""
        assert library.exists("non-existing-id") is False
    
    def test_count(self, library):
        """Test count returns correct number."""
        style1 = self._get_valid_style()
        style2 = self._get_valid_style()
        style2["style_id"] = "test-style-002"
        
        library.create(style1)
        library.create(style2)
        
        assert library.count() == 2
    
    def test_clear(self, library):
        """Test clear removes all styles."""
        style1 = self._get_valid_style()
        style2 = self._get_valid_style()
        style2["style_id"] = "test-style-002"
        
        library.create(style1)
        library.create(style2)
        library.clear()
        
        assert library.count() == 0
    
    def _get_valid_style(self):
        """Helper: Return a valid style JSON for testing."""
        return {
            "style_id": "test-style-001",
            "composition": {
                "perspective": "isometric",
                "layout": "centered",
                "depth": 5
            },
            "line": {
                "type": "clean",
                "width": 2.5,
                "variation": 0.1,
                "locked": True
            },
            "color": {
                "palette": ["#3357FF", "#33FF57", "#FF5733"],
                "saturation": 0.8,
                "temperature": "warm"
            },
            "material": {
                "type": "matte",
                "texture_strength": 0.3
            },
            "lighting": {
                "type": "soft",
                "direction": "top-left",
                "intensity": 0.7
            },
            "detail_density": {
                "foreground": 0.9,
                "background": 0.3
            },
            "negative_constraints": ["blurry", "distorted", "low quality"]
        }
