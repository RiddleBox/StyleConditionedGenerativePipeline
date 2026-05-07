"""
Style Library: SQLite-based persistent storage for style JSON.

Implements CRUD operations with deterministic behavior.
"""

import sqlite3
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class StyleLibrary:
    """
    SQLite-based style storage with CRUD operations.
    
    Features:
    - Persistent storage of normalized style JSON
    - CRUD operations (Create, Read, Update, Delete)
    - Query by style_id
    - List all styles
    - Atomic transactions
    """
    
    def __init__(self, db_path: str = "styles.db"):
        """
        Initialize the style library.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema if not exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS styles (
                style_id TEXT PRIMARY KEY,
                style_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create(self, style_json: Dict[str, Any]) -> bool:
        """
        Create a new style in the library.
        
        Args:
            style_json: Normalized style JSON
            
        Returns:
            True if created successfully, False if style_id already exists
            
        Raises:
            ValueError: If style_json is invalid or missing style_id
        """
        if "style_id" not in style_json:
            raise ValueError("style_json must contain 'style_id' field")
        
        style_id = style_json["style_id"]
        style_json_str = json.dumps(style_json, sort_keys=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO styles (style_id, style_json) VALUES (?, ?)",
                (style_id, style_json_str)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # style_id already exists
            return False
        finally:
            conn.close()
    
    def read(self, style_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a style from the library.
        
        Args:
            style_id: Style ID to retrieve
            
        Returns:
            Style JSON if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT style_json FROM styles WHERE style_id = ?",
            (style_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return json.loads(row[0])
    
    def update(self, style_json: Dict[str, Any]) -> bool:
        """
        Update an existing style in the library.
        
        Args:
            style_json: Normalized style JSON with style_id
            
        Returns:
            True if updated successfully, False if style_id not found
            
        Raises:
            ValueError: If style_json is invalid or missing style_id
        """
        if "style_id" not in style_json:
            raise ValueError("style_json must contain 'style_id' field")
        
        style_id = style_json["style_id"]
        style_json_str = json.dumps(style_json, sort_keys=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE styles SET style_json = ?, updated_at = CURRENT_TIMESTAMP WHERE style_id = ?",
            (style_json_str, style_id)
        )
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def delete(self, style_id: str) -> bool:
        """
        Delete a style from the library.
        
        Args:
            style_id: Style ID to delete
            
        Returns:
            True if deleted successfully, False if style_id not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM styles WHERE style_id = ?",
            (style_id,)
        )
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def list_all(self) -> List[Dict[str, Any]]:
        """
        List all styles in the library.
        
        Returns:
            List of style JSON objects (sorted by style_id)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT style_json FROM styles ORDER BY style_id"
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [json.loads(row[0]) for row in rows]
    
    def exists(self, style_id: str) -> bool:
        """
        Check if a style exists in the library.
        
        Args:
            style_id: Style ID to check
            
        Returns:
            True if exists, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM styles WHERE style_id = ?",
            (style_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def count(self) -> int:
        """
        Count total number of styles in the library.
        
        Returns:
            Number of styles
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM styles")
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def clear(self):
        """
        Clear all styles from the library.
        
        Warning: This operation cannot be undone.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM styles")
        
        conn.commit()
        conn.close()
