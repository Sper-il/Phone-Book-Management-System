"""
Admin Authentication Module - JSON Primary Storage
Admin inherits from User according to Class Diagram
"""
import json
import os
from datetime import datetime
from typing import Optional, Tuple, Dict
from .User import User


class Admin(User):
    """
    Admin class inherits from User.
    Admin is a special type of User with administrative privileges.
    """
    
    def __init__(self):
        super().__init__()
        # Override directories for admin
        self.admin_account_dir = os.path.join(self.data_dir, 'Admin', 'admin_account')
        self.admin_data_dir = os.path.join(self.data_dir, 'Admin', 'admin_data')
        self.admins_file = os.path.join(self.admin_account_dir, 'admins.json')
        
        # Ensure directories exist
        os.makedirs(self.admin_account_dir, exist_ok=True)
        os.makedirs(self.admin_data_dir, exist_ok=True)
        
        # Initialize admins.json if not exists
        if not os.path.exists(self.admins_file):
            with open(self.admins_file, 'w', encoding='utf-8') as f:
                json.dump({"admins": []}, f, ensure_ascii=False, indent=2)
    
    def _load_admins(self) -> Dict:
        """Load admins from JSON"""
        return self._load_json(self.admins_file) or {"admins": []}
    
    def _save_admins(self, data: Dict):
        """Save admins to JSON"""
        self._save_json(self.admins_file, data)
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Admin login
        
        Args:
            username: Admin username
            password: Admin password
            
        Returns:
            Tuple (success, message, admin_data)
        """
        if not username or not password:
            return False, "Please enter all information", None
        
        data = self._load_admins()
        admins = data.get('admins', [])
        
        # Find admin
        admin = next((a for a in admins if a['username'] == username), None)
        
        if not admin:
            return False, "Admin account does not exist", None
        
        if admin['password'] != self._hash_password(password):
            return False, "Incorrect password", None
        
        # Update last login
        admin['last_login'] = datetime.now().isoformat()
        self._save_admins(data)
        
        return True, "Login successful", admin
    
    def register(self, username: str, password: str, role: str = "admin", 
                 email: str = "", full_name: str = "") -> Tuple[bool, str]:
        """
        Register new admin
        
        Args:
            username: Admin username
            password: Password
            role: Admin role (admin/manager/superadmin)
            email: Admin email
            full_name: Full name
            
        Returns:
            Tuple (success, message)
        """
        # Validate credentials
        is_valid, error_msg = self._validate_credentials(username, password)
        if not is_valid:
            return False, error_msg
        
        data = self._load_admins()
        admins = data.get('admins', [])
        
        # Check if username exists
        if any(a['username'] == username for a in admins):
            return False, "Admin username already exists"
        
        # Create new admin
        hashed_password = self._hash_password(password)
        
        new_admin = {
            "username": username,
            "password": hashed_password,
            "password_plain": password,
            "email": email,
            "full_name": full_name,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "permissions": ["view_users", "view_statistics"]
        }
        
        admins.append(new_admin)
        data['admins'] = admins
        self._save_admins(data)
        
        # Create empty contacts file for admin
        admin_contacts_file = os.path.join(self.admin_data_dir, f"{username}_contacts.json")
        with open(admin_contacts_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        return True, "Admin registration successful"
    
    def get_admin_by_username(self, username: str) -> Optional[Dict]:
        """Get admin by username"""
        data = self._load_admins()
        admins = data.get('admins', [])
        return next((a for a in admins if a['username'] == username), None)
    
    def get_all_admins(self) -> list:
        """Get all admins"""
        data = self._load_admins()
        return data.get('admins', [])
    
    def is_admin(self, username: str) -> bool:
        """Check if username is admin"""
        admin = self.get_admin_by_username(username)
        return admin is not None
