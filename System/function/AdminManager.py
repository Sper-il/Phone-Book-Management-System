"""
Admin functionality module - JSON Primary Storage
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class AdminManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, 'Data')
        self.user_account_dir = os.path.join(self.data_dir, 'User', 'user_account')
        self.user_data_dir = os.path.join(self.data_dir, 'User', 'user_data')
        self.users_file = os.path.join(self.user_account_dir, 'users.json')
    
    def _load_users(self) -> Dict:
        """Load users from JSON"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"users": []}
    
    def _save_users(self, data: Dict):
        """Save users to JSON"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _count_user_contacts(self, username: str) -> int:
        """Count user's contacts"""
        contacts_file = os.path.join(self.user_data_dir, f"{username}_contacts.json")
        if not os.path.exists(contacts_file):
            return 0
        try:
            with open(contacts_file, 'r', encoding='utf-8') as f:
                contacts = json.load(f)
                return len(contacts) if isinstance(contacts, list) else 0
        except:
            return 0
    
    def get_all_users(self) -> List[Dict]:
        """Get all users with contact count"""
        data = self._load_users()
        users = data.get('users', [])
        
        # Add contact count to each user
        for user in users:
            user['contact_count'] = self._count_user_contacts(user.get('username', ''))
        
        return users
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        data = self._load_users()
        users = data.get('users', [])
        user = next((u for u in users if u['username'] == username), None)
        
        if user:
            user['contact_count'] = self._count_user_contacts(username)
        
        return user
    
    def delete_user(self, username: str) -> tuple:
        """Delete user"""
        if username == "admin":
            return False, "Cannot delete admin account"
        
        data = self._load_users()
        users = data.get('users', [])
        
        # Find and remove user
        user_found = False
        new_users = []
        for user in users:
            if user.get('username') == username:
                user_found = True
                # Delete user's contacts file
                contacts_file = os.path.join(self.user_data_dir, f"{username}_contacts.json")
                if os.path.exists(contacts_file):
                    os.remove(contacts_file)
            else:
                new_users.append(user)
        
        if not user_found:
            return False, "User does not exist"
        
        data['users'] = new_users
        self._save_users(data)
        
        return True, f"Successfully deleted user {username}"
    
    def update_user_password(self, username: str, new_password: str, hashed_password: str) -> tuple:
        """Update user password"""
        data = self._load_users()
        users = data.get('users', [])
        
        user_found = False
        for user in users:
            if user.get('username') == username:
                user['password'] = hashed_password
                user['password_plain'] = new_password
                user['password_updated_at'] = datetime.now().isoformat()
                user_found = True
                break
        
        if not user_found:
            return False, "User does not exist"
        
        self._save_users(data)
        return True, "Password updated successfully"
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        data = self._load_users()
        users = data.get('users', [])
        
        # Calculate stats
        total_users = len(users)
        total_contacts = sum(self._count_user_contacts(u.get('username', '')) for u in users)
        
        # Recent registrations (last 7 days)
        recent_count = 0
        seven_days_ago = datetime.now() - timedelta(days=7)
        for user in users:
            created_at = user.get('created_at', '')
            try:
                user_date = datetime.fromisoformat(created_at)
                if user_date >= seven_days_ago:
                    recent_count += 1
            except:
                pass
        
        avg_contacts = round(total_contacts / total_users, 2) if total_users > 0 else 0
        
        return {
            "total_users": total_users,
            "total_contacts": total_contacts,
            "recent_registrations": recent_count,
            "avg_contacts_per_user": avg_contacts
        }
    
    def search_users(self, query: str) -> List[Dict]:
        """Search users"""
        if not query:
            return self.get_all_users()
        
        data = self._load_users()
        users = data.get('users', [])
        
        # Filter users by username
        filtered_users = [u for u in users if query.lower() in u.get('username', '').lower()]
        
        # Add contact count
        for user in filtered_users:
            user['contact_count'] = self._count_user_contacts(user.get('username', ''))
        
        return filtered_users


_admin_manager = AdminManager()

def get_all_users() -> List[Dict]:
    return _admin_manager.get_all_users()

def get_user_by_username(username: str) -> Optional[Dict]:
    return _admin_manager.get_user_by_username(username)

def delete_user(username: str) -> tuple:
    return _admin_manager.delete_user(username)

def get_system_stats() -> Dict:
    return _admin_manager.get_system_stats()
