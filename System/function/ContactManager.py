"""
Contact Manager - Unified module for contact CRUD operations.
Combines logic from add_contact.py and edit.py to avoid duplicate code.
"""
from __future__ import annotations
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class ContactManager:
    """
    Manages CRUD operations for contacts (add, edit, delete, find).
    Combines logic from ContactAdder and ContactEditor.
    """
    
    REQUIRED_FIELDS = ['name', 'phone']
    EDITABLE_FIELDS = ['name', 'phone', 'email', 'address', 'group', 'notes', 'avatar']
    
    def __init__(self, username: str = None):
        """
        Initialize ContactManager for a specific user.
        
        Args:
            username: User's login name
        """
        self.username = username
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, 'Data', 'User', 'user_data')
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_contacts_file(self) -> Optional[str]:
        """Get path to user's contacts file."""
        if not self.username:
            return None
        return os.path.join(self.data_dir, f"{self.username}_contacts.json")
    
    def _load_contacts(self) -> List[Dict[str, Any]]:
        """Load contacts list from JSON file."""
        file_path = self._get_contacts_file()
        if not file_path or not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError) as e:
            print(f"[ContactManager] Error loading contacts: {e}")
            return []
    
    def _save_contacts(self, contacts: List[Dict[str, Any]]) -> bool:
        """Save contacts list to JSON file."""
        file_path = self._get_contacts_file()
        if not file_path:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(contacts, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"[ContactManager] Error saving contacts: {e}")
            return False
    
    def _generate_id(self, contacts: List[Dict[str, Any]]) -> int:
        """Generate new ID for contact."""
        if not contacts:
            return 1
        max_id = max((contact.get('id', 0) for contact in contacts), default=0)
        return max_id + 1
    
    def _validate_contact(self, contact_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate contact data.
        
        Returns:
            Tuple (is_valid, message)
        """
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if not contact_data.get(field, '').strip():
                return False, f"Field {field} is required"
        
        # Validate phone format (basic)
        phone = contact_data.get('phone', '').strip()
        phone_digits = ''.join(c for c in phone if c.isdigit())
        if len(phone_digits) < 9:
            return False, "Invalid phone number (minimum 9 digits)"
        
        # Validate email format (basic)
        email = contact_data.get('email', '').strip()
        if email and '@' not in email:
            return False, "Invalid email"
        
        return True, ""
    
    def _check_duplicate_phone(self, contacts: List[Dict], phone: str, exclude_id: int = None) -> bool:
        """
        Check if phone number already exists.
        
        Args:
            contacts: Current contacts list
            phone: Phone number to check
            exclude_id: Contact ID to exclude (used when updating)
        
        Returns:
            True if duplicate, False if OK
        """
        phone_digits = ''.join(c for c in phone if c.isdigit())
        
        for contact in contacts:
            # Skip if it's the contact being updated
            if exclude_id and contact.get('id') == exclude_id:
                continue
            
            existing_phone = ''.join(c for c in str(contact.get('phone', '')) if c.isdigit())
            if phone_digits == existing_phone:
                return True
        return False
    
    def get(self, contact_id: int) -> Dict[str, Any]:
        """
        Get a contact by ID.
        
        Args:
            contact_id: Contact ID
        
        Returns:
            Dict with keys: success, contact/message
        """
        if not self.username:
            return {"success": False, "message": "Not logged in"}
        
        contacts = self._load_contacts()
        
        for contact in contacts:
            if contact.get('id') == contact_id:
                return {"success": True, "contact": contact}
        
        return {"success": False, "message": "Contact not found"}
    
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all contacts of user.
        
        Returns:
            List of contact dicts
        """
        return self._load_contacts()
    
    def add(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add new contact.
        
        Args:
            contact_data: Dict containing contact information (name, phone, email, address, group, notes)
        
        Returns:
            Dict with keys: success (bool), message (str), contact (Dict if successful)
        """
        if not self.username:
            return {"success": False, "message": "Not logged in"}
        
        # Validate input
        is_valid, message = self._validate_contact(contact_data)
        if not is_valid:
            return {"success": False, "message": message}
        
        # Load existing contacts
        contacts = self._load_contacts()
        
        # Check duplicate phone
        phone = contact_data.get('phone', '').strip()
        if self._check_duplicate_phone(contacts, phone):
            return {"success": False, "message": "Phone number already exists in contact list"}
        
        # Create new contact with normalized phone (per ER Diagram)
        phone_normalized = ''.join(c for c in phone if c.isdigit())
        new_contact = {
            "id": self._generate_id(contacts),
            "name": contact_data.get('name', '').strip(),
            "phone": phone,
            "phone_normalized": phone_normalized,
            "email": contact_data.get('email', '').strip(),
            "address": contact_data.get('address', '').strip(),
            "group": contact_data.get('group', '').strip(),
            "notes": contact_data.get('notes', '').strip(),
            "avatar": contact_data.get('avatar', ''),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Add to list
        contacts.append(new_contact)
        
        # Save
        if self._save_contacts(contacts):
            return {"success": True, "message": "Contact added successfully", "contact": new_contact}
        else:
            return {"success": False, "message": "Error saving file"}
    
    def update(self, contact_id: int, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update contact information (full update).
        
        Args:
            contact_id: ID of contact to update
            contact_data: Dict containing new information
        
        Returns:
            Dict with keys: success (bool), message (str), contact (Dict if successful)
        """
        if not self.username:
            return {"success": False, "message": "Not logged in"}
        
        # Validate input
        is_valid, message = self._validate_contact(contact_data)
        if not is_valid:
            return {"success": False, "message": message}
        
        # Load existing contacts
        contacts = self._load_contacts()
        
        # Check duplicate phone (excluding current contact)
        phone = contact_data.get('phone', '').strip()
        if self._check_duplicate_phone(contacts, phone, exclude_id=contact_id):
            return {"success": False, "message": "Phone number already exists in contact list"}
        
        # Find and update contact with normalized phone (per ER Diagram)
        phone_normalized = ''.join(c for c in phone if c.isdigit())
        for i, contact in enumerate(contacts):
            if contact.get('id') == contact_id:
                # Update fields while preserving id and created_at
                updated_contact = {
                    **contact,  # Keep all existing data
                    "name": contact_data.get('name', '').strip(),
                    "phone": phone,
                    "phone_normalized": phone_normalized,
                    "email": contact_data.get('email', '').strip(),
                    "address": contact_data.get('address', '').strip(),
                    "group": contact_data.get('group', '').strip(),
                    "notes": contact_data.get('notes', '').strip(),
                    "avatar": contact_data.get('avatar', contact.get('avatar', '')),
                    "updated_at": datetime.now().isoformat()
                }
                contacts[i] = updated_contact
                
                if self._save_contacts(contacts):
                    return {"success": True, "message": "Update successful", "contact": updated_contact}
                else:
                    return {"success": False, "message": "Error saving file"}
        
        return {"success": False, "message": "Contact not found"}
    
    def update_partial(self, contact_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update specific fields of contact (partial update).
        
        Args:
            contact_id: Contact ID
            fields: Dict containing fields to update
        
        Returns:
            Dict with keys: success (bool), message (str), contact (Dict if successful)
        """
        if not self.username:
            return {"success": False, "message": "Not logged in"}
        
        contacts = self._load_contacts()
        
        for i, contact in enumerate(contacts):
            if contact.get('id') == contact_id:
                # Update only provided fields
                for field in self.EDITABLE_FIELDS:
                    if field in fields:
                        contact[field] = fields[field].strip() if isinstance(fields[field], str) else fields[field]
                
                contact['updated_at'] = datetime.now().isoformat()
                contacts[i] = contact
                
                # Validate after update
                is_valid, message = self._validate_contact(contact)
                if not is_valid:
                    return {"success": False, "message": message}
                
                if self._save_contacts(contacts):
                    return {"success": True, "message": "Update successful", "contact": contact}
                else:
                    return {"success": False, "message": "Error saving file"}
        
        return {"success": False, "message": "Contact not found"}
    
    def delete(self, contact_id: int) -> Dict[str, Any]:
        """
        Delete contact by ID.
        
        Args:
            contact_id: ID of contact to delete
        
        Returns:
            Dict with keys: success, message
        """
        if not self.username:
            return {"success": False, "message": "Not logged in"}
        
        contacts = self._load_contacts()
        
        # Find and remove contact
        for i, contact in enumerate(contacts):
            if contact.get('id') == contact_id:
                contacts.pop(i)
                
                if self._save_contacts(contacts):
                    return {"success": True, "message": "Contact deleted successfully"}
                else:
                    return {"success": False, "message": "Error saving file"}
        
        return {"success": False, "message": "Contact not found"}


# ===== BACKWARD COMPATIBILITY WRAPPERS =====
# Keep legacy functions to avoid breaking existing code

def get_contact(username: str, contact_id: int) -> Dict[str, Any]:
    """Legacy wrapper for backward compatibility."""
    manager = ContactManager(username)
    return manager.get(contact_id)


def add_contact(username: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy wrapper for backward compatibility."""
    manager = ContactManager(username)
    return manager.add(contact_data)


def update_contact(username: str, contact_id: int, contact_data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy wrapper for backward compatibility."""
    manager = ContactManager(username)
    return manager.update(contact_id, contact_data)


def update_contact_partial(username: str, contact_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy wrapper for backward compatibility."""
    manager = ContactManager(username)
    return manager.update_partial(contact_id, fields)


def delete_contact(username: str, contact_id: int) -> Dict[str, Any]:
    """Legacy wrapper for backward compatibility."""
    manager = ContactManager(username)
    return manager.delete(contact_id)
