"""
Base Authentication Module - Common authentication functionality
Provides shared authentication methods for both User and Admin
"""
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Optional, Tuple


class BaseAuthentication:
    """Base authentication class with common functionality"""
    
    def __init__(self, account_type: str = "user"):
        """
        Initialize base authentication
        
        Args:
            account_type: Either 'user' or 'admin'
        """
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, 'Data')
        self.account_type = account_type
        
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _validate_credentials(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Validate username and password format
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not username or not password:
            return False, "Please enter all required information"
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        return True, ""
    
    def _load_json(self, file_path: str) -> dict:
        """
        Load data from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary with data or empty dict
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, file_path: str, data: dict) -> bool:
        """
        Save data to JSON file
        
        Args:
            file_path: Path to JSON file
            data: Dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[BaseAuth] Error saving to {file_path}: {e}")
            return False
    
    def _generate_id(self, items: list) -> int:
        """
        Generate new ID for item
        
        Args:
            items: List of items with 'id' field
            
        Returns:
            New unique ID
        """
        if not items:
            return 1
        max_id = max((item.get('id', 0) for item in items), default=0)
        return max_id + 1
