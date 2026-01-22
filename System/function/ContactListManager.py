"""
ContactListManager - Unified class for all contact list operations.
Combines all functions: CRUD, Search, Sort, Filter following OOP design.
"""
from __future__ import annotations
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class ContactListManager:
    """
    Manages all operations for contact list.
    Combines: ContactManager, ContactSearcher, ContactsSorter, ContactDeleter.
    """
    
    REQUIRED_FIELDS = ['name', 'phone']
    EDITABLE_FIELDS = ['name', 'phone', 'email', 'address', 'group', 'notes', 'avatar']
    SEARCHABLE_FIELDS = ['name', 'phone', 'email', 'address', 'group', 'notes']
    SORTABLE_FIELDS = ['name', 'phone', 'email', 'created_at', 'updated_at']
    
    def __init__(self, username: str = None):
        """
        Initialize ContactListManager for a specific user.
        
        Args:
            username: User's login name
        """
        self.username = username
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, 'Data', 'User', 'user_data')
        self._cache: Optional[List[Dict[str, Any]]] = None  # Cache to improve performance
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    # ==================== PRIVATE METHODS ====================
    
    def _get_contacts_file(self) -> Optional[str]:
        """Get path to user's contacts file."""
        if not self.username:
            return None
        return os.path.join(self.data_dir, f"{self.username}_contacts.json")
    
    def _load_contacts(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Load contacts list from JSON file.
        
        Args:
            use_cache: Use cache if available (default True)
        
        Returns:
            List of contact dicts
        """
        # Check cache first
        if use_cache and self._cache is not None:
            return self._cache
        
        file_path = self._get_contacts_file()
        if not file_path or not os.path.exists(file_path):
            self._cache = []
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                contacts = data if isinstance(data, list) else []
                self._cache = contacts
                return contacts
        except (json.JSONDecodeError, IOError) as e:
            print(f"[ContactListManager] Error loading contacts: {e}")
            self._cache = []
            return []
    
    def _save_contacts(self, contacts: List[Dict[str, Any]]) -> bool:
        """
        Save contacts list to JSON file and update cache.
        
        Args:
            contacts: List of contacts to save
        
        Returns:
            True if successful, False if error
        """
        file_path = self._get_contacts_file()
        if not file_path:
            return False
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(contacts, f, ensure_ascii=False, indent=2)
            # Update cache
            self._cache = contacts
            return True
        except IOError as e:
            print(f"[ContactListManager] Error saving contacts: {e}")
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
        
        # Validate phone format
        phone = contact_data.get('phone', '').strip()
        phone_digits = ''.join(c for c in phone if c.isdigit())
        if len(phone_digits) < 9:
            return False, "Invalid phone number (minimum 9 digits)"
        
        # Validate email format
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
            if exclude_id and contact.get('id') == exclude_id:
                continue
            
            existing_phone = ''.join(c for c in str(contact.get('phone', '')) if c.isdigit())
            if phone_digits == existing_phone:
                return True
        return False
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for search (lowercase, remove accents)."""
        import unicodedata
        # Remove accents
        nfd = unicodedata.normalize('NFD', text)
        text_no_accents = ''.join(c for c in nfd if not unicodedata.combining(c))
        return text_no_accents.lower()
    
    def _get_sort_key(self, contact: Dict[str, Any], field: str) -> Any:
        """Get sort key for a contact based on field."""
        if field == 'phone':
            # Extract digits only for numeric sort
            phone = contact.get('phone', '')
            digits = ''.join(c for c in str(phone) if c.isdigit())
            return int(digits) if digits else 0
        elif field in ['created_at', 'updated_at']:
            # Sort by datetime
            return contact.get(field, '')
        else:
            # Default: string sort (case-insensitive)
            return str(contact.get(field, '')).lower()
    
    # ==================== PUBLIC CRUD METHODS ====================
    
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
    
    def get_all(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get all contacts of user.
        
        Args:
            use_cache: Use cache if available
        
        Returns:
            List of contact dicts
        """
        return self._load_contacts(use_cache=use_cache)
    
    def reload(self) -> ContactListManager:
        """Force reload data from file (clear cache)."""
        self._cache = None
        self._load_contacts(use_cache=False)
        return self
    
    def add(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add new contact.
        
        Args:
            contact_data: Dict containing contact information
        
        Returns:
            Dict with keys: success, message, contact
        """
        if not self.username:
            return {"success": False, "message": "Not logged in"}
        
        # Validate input
        is_valid, message = self._validate_contact(contact_data)
        if not is_valid:
            return {"success": False, "message": message}
        
        # Load existing contacts
        contacts = self._load_contacts(use_cache=False)  # Force reload
        
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
            Dict with keys: success, message, contact
        """
        if not self.username:
            return {"success": False, "message": "Not logged in"}
        
        # Validate input
        is_valid, message = self._validate_contact(contact_data)
        if not is_valid:
            return {"success": False, "message": message}
        
        # Load existing contacts
        contacts = self._load_contacts(use_cache=False)
        
        # Check duplicate phone
        phone = contact_data.get('phone', '').strip()
        if self._check_duplicate_phone(contacts, phone, exclude_id=contact_id):
            return {"success": False, "message": "Phone number already exists in contact list"}
        
        # Find and update contact with normalized phone (per ER Diagram)
        phone_normalized = ''.join(c for c in phone if c.isdigit())
        for i, contact in enumerate(contacts):
            if contact.get('id') == contact_id:
                updated_contact = {
                    **contact,
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
        
        contacts = self._load_contacts(use_cache=False)
        
        # Find and remove contact
        for i, contact in enumerate(contacts):
            if contact.get('id') == contact_id:
                contacts.pop(i)
                
                if self._save_contacts(contacts):
                    return {"success": True, "message": "Contact deleted successfully"}
                else:
                    return {"success": False, "message": "Error saving file"}
        
        return {"success": False, "message": "Contact not found"}
    
    def delete_all(self) -> Dict[str, Any]:
        """
        Delete all contacts of user.
        
        Returns:
            Dict with keys: success, message, count
        """
        if not self.username:
            return {"success": False, "message": "Not logged in"}
        
        contacts = self._load_contacts(use_cache=False)
        count = len(contacts)
        
        if self._save_contacts([]):
            return {"success": True, "message": f"Deleted {count} contacts", "count": count}
        else:
            return {"success": False, "message": "Error saving file"}
    
    # ==================== SEARCH METHODS ====================
    
    def search(self, query: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search contacts by query string.
        
        Args:
            query: Search string
            fields: List of fields to search (default: all searchable fields)
        
        Returns:
            List of matching contacts
        """
        if not query or not query.strip():
            return self.get_all()
        
        contacts = self._load_contacts()
        query_normalized = self._normalize_text(query.strip())
        
        # Default search fields
        if not fields:
            fields = self.SEARCHABLE_FIELDS
        
        # Filter contacts
        results = []
        for contact in contacts:
            for field in fields:
                value = str(contact.get(field, ''))
                if query_normalized in self._normalize_text(value):
                    results.append(contact)
                    break  # Avoid duplicate
        
        return results
    
    def filter_by_group(self, group_name: str) -> List[Dict[str, Any]]:
        """
        Filter contacts by group.
        
        Args:
            group_name: Group name to filter
        
        Returns:
            List of contacts in group
        """
        contacts = self._load_contacts()
        
        if not group_name:
            # Return contacts without group
            return [c for c in contacts if not c.get('group', '').strip()]
        
        # Case-insensitive comparison
        group_lower = group_name.lower()
        return [c for c in contacts if c.get('group', '').lower() == group_lower]
    
    def assign_to_group(self, contact_id: int, group_name: str) -> Dict[str, Any]:
        """
        Assign contact to group (Assign Contact to Group - per FDD).
        
        Args:
            contact_id: ID of contact to assign
            group_name: Group name (empty string to remove from group)
        
        Returns:
            Dict with keys: success, message, contact
        """
        if not self.username:
            return {"success": False, "message": "Not logged in"}
        
        contacts = self._load_contacts(use_cache=False)
        
        for i, contact in enumerate(contacts):
            if contact.get('id') == contact_id:
                contact['group'] = group_name.strip() if group_name else ''
                contact['updated_at'] = datetime.now().isoformat()
                contacts[i] = contact
                
                if self._save_contacts(contacts):
                    return {
                        "success": True, 
                        "message": f"Assigned contact to group '{group_name}'" if group_name else "Removed contact from group",
                        "contact": contact
                    }
                else:
                    return {"success": False, "message": "Error saving file"}
        
        return {"success": False, "message": "Contact not found"}
    
    # ==================== SORT METHODS ====================
    
    def sort(self, field: str = 'name', reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Sort contacts by field.
        
        Args:
            field: Field to sort by (name, phone, email, created_at, updated_at)
            reverse: True = descending, False = ascending
        
        Returns:
            Sorted list of contacts
        """
        if field not in self.SORTABLE_FIELDS:
            field = 'name'  # Default
        
        contacts = self._load_contacts()
        
        try:
            sorted_contacts = sorted(
                contacts, 
                key=lambda c: self._get_sort_key(c, field),
                reverse=reverse
            )
            return sorted_contacts
        except Exception as e:
            print(f"[ContactListManager] Sort error: {e}")
            return contacts

    def sort_list(self, contacts: List[Dict[str, Any]], field: str = 'name', reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Sort an arbitrary list of contacts using the same sort logic as `sort`.

        Args:
            contacts: List of contact dicts to sort
            field: Field to sort by
            reverse: True for descending

        Returns:
            Sorted list of contacts
        """
        if field not in self.SORTABLE_FIELDS:
            field = 'name'

        try:
            sorted_contacts = sorted(
                contacts,
                key=lambda c: self._get_sort_key(c, field),
                reverse=reverse
            )
            return sorted_contacts
        except Exception as e:
            print(f"[ContactListManager] Sort list error: {e}")
            return contacts
    
    def sort_and_save(self, field: str = 'name', reverse: bool = False) -> Dict[str, Any]:
        """
        Sort and save to file.
        
        Args:
            field: Field to sort by
            reverse: True = descending, False = ascending
        
        Returns:
            Dict with keys: success, message
        """
        if not self.username:
            return {"success": False, "message": "Not logged in"}
        
        sorted_contacts = self.sort(field=field, reverse=reverse)
        
        if self._save_contacts(sorted_contacts):
            return {"success": True, "message": f"Sorted by {field}"}
        else:
            return {"success": False, "message": "Error saving file"}
    
    # ==================== UTILITY METHODS ====================
    
    def count(self) -> int:
        """Count total number of contacts."""
        return len(self._load_contacts())
    
    def get_groups(self) -> List[str]:
        """
        Get list of groups currently in use.
        
        Returns:
            List of unique group names
        """
        contacts = self._load_contacts()
        groups = set()
        
        for contact in contacts:
            group = contact.get('group', '').strip()
            if group:
                groups.add(group)
        
        return sorted(list(groups))
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about contact list.
        
        Returns:
            Dict with metrics
        """
        contacts = self._load_contacts()
        groups = self.get_groups()
        
        return {
            "total_contacts": len(contacts),
            "total_groups": len(groups),
            "groups": groups,
            "has_email": len([c for c in contacts if c.get('email', '').strip()]),
            "has_address": len([c for c in contacts if c.get('address', '').strip()]),
            "has_notes": len([c for c in contacts if c.get('notes', '').strip()])
        }


# ===== BACKWARD COMPATIBILITY WRAPPERS =====

def get_contact(username: str, contact_id: int) -> Dict[str, Any]:
    """Legacy wrapper."""
    manager = ContactListManager(username)
    return manager.get(contact_id)


def get_all_contacts(username: str) -> List[Dict[str, Any]]:
    """Legacy wrapper."""
    manager = ContactListManager(username)
    return manager.get_all()


def search_contacts(username: str, query: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Legacy wrapper."""
    manager = ContactListManager(username)
    return manager.search(query, fields)


def sort_contacts(username: str, field: str = 'name', reverse: bool = False) -> List[Dict[str, Any]]:
    """Legacy wrapper."""
    manager = ContactListManager(username)
    return manager.sort(field, reverse)
