"""
User Authentication Module - JSON Primary Storage
SQLite is used only for backup/sync
"""
import json
import os
from datetime import datetime
from typing import Dict, Optional, Tuple
from .BaseAuthentication import BaseAuthentication


class User(BaseAuthentication):
    def __init__(self):
        super().__init__(account_type="user")
        self.user_account_dir = os.path.join(self.data_dir, 'User', 'user_account')
        self.user_data_dir = os.path.join(self.data_dir, 'User', 'user_data')
        self.users_file = os.path.join(self.user_account_dir, 'users.json')
        
        # Ensure directories exist
        os.makedirs(self.user_account_dir, exist_ok=True)
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        # Initialize users.json if not exists
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({"users": []}, f, ensure_ascii=False, indent=2)
    
    def _load_users(self) -> dict:
        """Load users from JSON"""
        return self._load_json(self.users_file) or {"users": []}
    
    def _save_users(self, data: dict):
        """Save users to JSON"""
        self._save_json(self.users_file, data)
    
    def _sync_to_sqlite(self):
        """Sync data to SQLite for backup"""
        try:
            import sys
            sys.path.insert(0, self.base_dir)
            from database import get_db_connection
            
            data = self._load_users()
            with get_db_connection() as conn:
                cursor = conn.cursor()
                for user in data.get('users', []):
                    cursor.execute('''
                        INSERT OR REPLACE INTO users 
                        (id, username, password, password_plain, security_question, security_answer, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (user.get('id'), user.get('username'), user.get('password'),
                          user.get('password_plain'), user.get('security_question'),
                          user.get('security_answer'), user.get('created_at')))
        except:
            pass  # SQLite backup optional
    
    def register(self, username: str, password: str, security_question: str = "", security_answer: str = "") -> Tuple[bool, str]:
        """
        Register new user - Save to JSON
        
        Args:
            username: Username
            password: Password
            security_question: Security question for password recovery
            security_answer: Answer to security question
            
        Returns:
            Tuple (success, message)
        """
        # Validate credentials
        is_valid, error_msg = self._validate_credentials(username, password)
        if not is_valid:
            return False, error_msg
        
        data = self._load_users()
        users = data.get('users', [])
        
        # Check if username exists
        if any(u['username'] == username for u in users):
            return False, "Username already exists"
        
        # Create new user (per ER Diagram: fullname, email, is_active fields)
        user_id = self._generate_id(users)
        hashed_password = self._hash_password(password)
        
        new_user = {
            "id": user_id,
            "username": username,
            "password": hashed_password,
            "password_plain": password,
            "fullname": "",  # Can be updated via profile
            "email": "",  # Can be updated via profile
            "security_question": security_question or "What is your pet's name?",
            "security_answer": (security_answer or "").lower().strip(),
            "security_answer_hash": self._hash_password((security_answer or "").lower().strip()),
            "created_at": datetime.now().isoformat(),
            "is_active": 1,  # 1 = active, 0 = inactive (per ER Diagram)
            "contacts_file": f"{username}_contacts.json"
        }
        
        users.append(new_user)
        data['users'] = users
        self._save_users(data)
        
        # Create empty contacts file for user
        user_contacts_file = os.path.join(self.user_data_dir, new_user['contacts_file'])
        with open(user_contacts_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        
        # Sync to SQLite backup
        self._sync_to_sqlite()
        
        return True, "Registration successful"
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Login - Read from JSON
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple (success, message, user_data)
        """
        if not username or not password:
            return False, "Please enter all information", None
        
        data = self._load_users()
        users = data.get('users', [])
        
        user = next((u for u in users if u['username'] == username), None)
        if not user:
            return False, "Username does not exist", None
        
        if user['password'] != self._hash_password(password):
            return False, "Incorrect password", None
        
        return True, "Login successful", user
    
    def get_security_question(self, username: str) -> Optional[str]:
        """Get user's security question"""
        data = self._load_users()
        users = data.get('users', [])
        user = next((u for u in users if u['username'] == username), None)
        return user.get('security_question') if user else None
    
    def verify_security_answer(self, username: str, answer: str) -> Tuple[bool, str]:
        """
        Verify security answer
        
        Args:
            username: Username
            answer: Answer to verify
        
        Returns:
            Tuple (success, message)
        """
        if not username or not answer:
            return False, "Please provide all information"
        
        data = self._load_users()
        users = data.get('users', [])
        user = next((u for u in users if u['username'] == username), None)
        
        if not user:
            return False, "User does not exist"
        
        stored_answer = user.get('security_answer', '').lower().strip()
        if stored_answer == answer.lower().strip():
            return True, "Verification successful"
        
        return False, "Incorrect security answer"
    
    def reset_password(self, username: str, security_answer: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset password
        
        Args:
            username: Username
            security_answer: Security answer for verification
            new_password: New password
            
        Returns:
            Tuple (success, message)
        """
        if not username or not security_answer or not new_password:
            return False, "Please provide all information"
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters"
        
        data = self._load_users()
        users = data.get('users', [])
        
        for user in users:
            if user['username'] == username:
                if user.get('security_answer', '').lower() != security_answer.lower().strip():
                    return False, "Incorrect security answer"
                
                user['password'] = self._hash_password(new_password)
                user['password_plain'] = new_password
                user['password_reset_at'] = datetime.now().isoformat()
                
                data['users'] = users
                self._save_users(data)
                self._sync_to_sqlite()
                
                return True, "Password reset successful"
        
        return False, "User does not exist"
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        data = self._load_users()
        users = data.get('users', [])
        return next((u for u in users if u['username'] == username), None)
    
    def get_user_contacts_file(self, username: str) -> Optional[str]:
        """Get path to user's contacts file"""
        user = self.get_user_by_username(username)
        if user and user.get('contacts_file'):
            return os.path.join(self.user_data_dir, user['contacts_file'])
        return None
    
    # ==================== PROFILE METHODS ====================
    
    def get_profile(self, username: str) -> Dict:
        """
        Get user's profile information.
        
        Args:
            username: Login name
            
        Returns:
            Dict with keys: success, profile (if successful), message (if error)
        """
        if not username:
            return {"success": False, "message": "Not logged in"}
        
        user = self.get_user_by_username(username)
        if user:
            profile = {
                "id": user.get('id'),
                "username": user.get('username'),
                "fullname": user.get('fullname', ''),
                "email": user.get('email', ''),
                "phone": user.get('phone', ''),
                "avatar": user.get('avatar', ''),
                "is_active": user.get('is_active', 1),
                "created_at": user.get('created_at', '')
            }
            return {"success": True, "profile": profile}
        
        return {"success": False, "message": "User not found"}
    
    def update_profile(self, username: str, profile_data: Dict) -> Dict:
        """
        Update profile information.
        
        Args:
            username: Login name
            profile_data: Dict containing new information (fullname, email, phone, avatar)
        
        Returns:
            Dict with keys: success, message, profile (if successful)
        """
        if not username:
            return {"success": False, "message": "Not logged in"}
        
        data = self._load_users()
        users = data.get('users', [])
        
        for i, user in enumerate(users):
            if user.get('username') == username:
                # Update allowed fields only
                if 'fullname' in profile_data:
                    user['fullname'] = profile_data['fullname'].strip()
                if 'email' in profile_data:
                    user['email'] = profile_data['email'].strip()
                if 'phone' in profile_data:
                    user['phone'] = profile_data['phone'].strip()
                if 'avatar' in profile_data:
                    user['avatar'] = profile_data['avatar']
                
                user['updated_at'] = datetime.now().isoformat()
                users[i] = user
                data['users'] = users
                
                if self._save_json(self.users_file, data):
                    profile = {
                        "id": user.get('id'),
                        "username": user.get('username'),
                        "fullname": user.get('fullname', ''),
                        "email": user.get('email', ''),
                        "phone": user.get('phone', ''),
                        "avatar": user.get('avatar', ''),
                        "is_active": user.get('is_active', 1)
                    }
                    return {"success": True, "message": "Update successful", "profile": profile}
                else:
                    return {"success": False, "message": "Error saving file"}
        
        return {"success": False, "message": "User not found"}
