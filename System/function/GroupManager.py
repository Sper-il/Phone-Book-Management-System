"""
GroupManager - Unified class for all group management operations.
Manages CRUD groups following OOP design, independent without depending on other classes.
"""
from __future__ import annotations
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class GroupManager:
    """
    Manages all operations for groups.
    Features: CRUD groups, validate, statistics.
    """
    
    REQUIRED_FIELDS = ['name']
    EDITABLE_FIELDS = ['name', 'color', 'description']
    DEFAULT_COLORS = [
        '#EF4444', '#F97316', '#F59E0B', '#22C55E', '#14B8A6',
        '#3B82F6', '#6366F1', '#A855F7', '#EC4899', '#6B7280'
    ]
    
    def __init__(self, username: str = None):
        """
        Initialize GroupManager for a specific user.
        
        Args:
            username: User's login name (None for admin/shared groups)
        """
        self.username = username
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Determine data directory based on user type
        if username:
            self.data_dir = os.path.join(self.base_dir, 'Data', 'User', 'user_data')
            self.groups_file = os.path.join(self.data_dir, f'{username}_groups.json')
        else:
            # Shared/admin groups
            self.data_dir = os.path.join(self.base_dir, 'Data', 'Admin', 'admin_data')
            self.groups_file = os.path.join(self.data_dir, 'groups.json')
        
        self._cache: Optional[List[Dict[str, Any]]] = None
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    # ==================== PRIVATE METHODS ====================
    
    def _load_groups(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Load groups list from JSON file.
        
        Args:
            use_cache: Use cache if available
        
        Returns:
            List of group dicts
        """
        # Check cache first
        if use_cache and self._cache is not None:
            return self._cache
        
        if not os.path.exists(self.groups_file):
            self._cache = []
            return []
        
        try:
            with open(self.groups_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                groups = data if isinstance(data, list) else []
                self._cache = groups
                return groups
        except (json.JSONDecodeError, IOError) as e:
            print(f"[GroupManager] Error loading groups: {e}")
            self._cache = []
            return []
    
    def _save_groups(self, groups: List[Dict[str, Any]]) -> bool:
        """
        Save groups list to JSON file and update cache.
        
        Args:
            groups: List of groups to save
        
        Returns:
            True if successful, False if error
        """
        try:
            with open(self.groups_file, 'w', encoding='utf-8') as f:
                json.dump(groups, f, ensure_ascii=False, indent=2)
            # Update cache
            self._cache = groups
            return True
        except IOError as e:
            print(f"[GroupManager] Error saving groups: {e}")
            return False
    
    def _generate_id(self, groups: List[Dict[str, Any]]) -> int:
        """Generate new ID for group."""
        if not groups:
            return 1
        max_id = max((group.get('id', 0) for group in groups), default=0)
        return max_id + 1
    
    def _validate_group(self, group_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate group data.
        
        Returns:
            Tuple (is_valid, message)
        """
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if not group_data.get(field, '').strip():
                return False, f"Field {field} is required"
        
        # Validate name length
        name = group_data.get('name', '').strip()
        if len(name) < 2:
            return False, "Group name must be at least 2 characters"
        if len(name) > 50:
            return False, "Group name cannot exceed 50 characters"
        
        return True, ""
    
    def _check_duplicate_name(self, groups: List[Dict], name: str, exclude_id: int = None) -> bool:
        """
        Check if group name already exists.
        
        Args:
            groups: Current groups list
            name: Group name to check
            exclude_id: Group ID to exclude (used when updating)
        
        Returns:
            True if duplicate, False if OK
        """
        name_lower = name.lower().strip()
        
        for group in groups:
            if exclude_id and group.get('id') == exclude_id:
                continue
            
            existing_name = group.get('name', '').lower().strip()
            if name_lower == existing_name:
                return True
        return False
    
    # ==================== PUBLIC CRUD METHODS ====================
    
    def get(self, group_id: int) -> Dict[str, Any]:
        """
        Get a group by ID.
        
        Args:
            group_id: Group ID
        
        Returns:
            Dict with keys: success, group/message
        """
        groups = self._load_groups()
        
        for group in groups:
            if group.get('id') == group_id:
                return {"success": True, "group": group}
        
        return {"success": False, "message": "Group not found"}
    
    def get_by_name(self, name: str) -> Dict[str, Any]:
        """
        Get group by name.
        
        Args:
            name: Group name
        
        Returns:
            Dict with keys: success, group/message
        """
        groups = self._load_groups()
        name_lower = name.lower().strip()
        
        for group in groups:
            if group.get('name', '').lower().strip() == name_lower:
                return {"success": True, "group": group}
        
        return {"success": False, "message": "Group not found"}
    
    def get_all(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get all groups.
        
        Args:
            use_cache: Use cache if available
        
        Returns:
            List of group dicts
        """
        return self._load_groups(use_cache=use_cache)
    
    def reload(self) -> GroupManager:
        """Force reload data from file (clear cache)."""
        self._cache = None
        self._load_groups(use_cache=False)
        return self
    
    def add(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add new group.
        
        Args:
            group_data: Dict containing group information (name, color, description)
        
        Returns:
            Dict with keys: success, message, group
        """
        # Validate input
        is_valid, message = self._validate_group(group_data)
        if not is_valid:
            return {"success": False, "message": message}
        
        # Load existing groups
        groups = self._load_groups(use_cache=False)
        
        # Check duplicate name
        name = group_data.get('name', '').strip()
        if self._check_duplicate_name(groups, name):
            return {"success": False, "message": "Group name already exists"}
        
        # Create new group (per ER Diagram: is_shared field)
        new_group = {
            "id": self._generate_id(groups),
            "name": name,
            "color": group_data.get('color', self.DEFAULT_COLORS[len(groups) % len(self.DEFAULT_COLORS)]),
            "description": group_data.get('description', '').strip(),
            "is_shared": group_data.get('is_shared', 0),  # 0 = private, 1 = shared (per ER Diagram)
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Add to list
        groups.append(new_group)
        
        # Save
        if self._save_groups(groups):
            return {"success": True, "message": "Group added successfully", "group": new_group}
        else:
            return {"success": False, "message": "Error saving file"}
    
    def update(self, group_id: int, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update group information.
        
        Args:
            group_id: ID of group to update
            group_data: Dict containing new information
        
        Returns:
            Dict with keys: success, message, group
        """
        # Validate input
        is_valid, message = self._validate_group(group_data)
        if not is_valid:
            return {"success": False, "message": message}
        
        # Load existing groups
        groups = self._load_groups(use_cache=False)
        
        # Check duplicate name (excluding current group)
        name = group_data.get('name', '').strip()
        if self._check_duplicate_name(groups, name, exclude_id=group_id):
            return {"success": False, "message": "Group name already exists"}
        
        # Find and update group (preserve is_shared per ER Diagram)
        for i, group in enumerate(groups):
            if group.get('id') == group_id:
                updated_group = {
                    **group,
                    "name": name,
                    "color": group_data.get('color', group.get('color', self.DEFAULT_COLORS[0])),
                    "description": group_data.get('description', group.get('description', '')).strip(),
                    "is_shared": group_data.get('is_shared', group.get('is_shared', 0)),
                    "updated_at": datetime.now().isoformat()
                }
                groups[i] = updated_group
                
                if self._save_groups(groups):
                    return {"success": True, "message": "Group updated successfully", "group": updated_group}
                else:
                    return {"success": False, "message": "Error saving file"}
        
        return {"success": False, "message": "Group not found"}
    
    def delete(self, group_id: int) -> Dict[str, Any]:
        """
        Delete group by ID.
        
        Args:
            group_id: ID of group to delete
        
        Returns:
            Dict with keys: success, message
        """
        groups = self._load_groups(use_cache=False)
        
        # Find and remove group
        for i, group in enumerate(groups):
            if group.get('id') == group_id:
                group_name = group.get('name', '')
                groups.pop(i)
                
                if self._save_groups(groups):
                    return {
                        "success": True, 
                        "message": f"Deleted group '{group_name}'",
                        "group_name": group_name
                    }
                else:
                    return {"success": False, "message": "Error saving file"}
        
        return {"success": False, "message": "Group not found"}
    
    def delete_all(self) -> Dict[str, Any]:
        """
        Delete all groups.
        
        Returns:
            Dict with keys: success, message, count
        """
        groups = self._load_groups(use_cache=False)
        count = len(groups)
        
        if self._save_groups([]):
            return {"success": True, "message": f"Deleted {count} groups", "count": count}
        else:
            return {"success": False, "message": "Error saving file"}
    
    # ==================== UTILITY METHODS ====================
    
    def count(self) -> int:
        """Count total number of groups."""
        return len(self._load_groups())
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search groups by name or description.
        
        Args:
            query: Search string
        
        Returns:
            List of matching groups
        """
        if not query or not query.strip():
            return self.get_all()
        
        groups = self._load_groups()
        query_lower = query.lower().strip()
        
        results = []
        for group in groups:
            name = group.get('name', '').lower()
            description = group.get('description', '').lower()
            
            if query_lower in name or query_lower in description:
                results.append(group)
        
        return results
    
    def sort(self, field: str = 'name', reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Sort groups by field.
        
        Args:
            field: Field to sort by (name, created_at, updated_at)
            reverse: True = descending, False = ascending
        
        Returns:
            Sorted list of groups
        """
        groups = self._load_groups()
        
        if field not in ['name', 'created_at', 'updated_at']:
            field = 'name'
        
        try:
            sorted_groups = sorted(
                groups,
                key=lambda g: str(g.get(field, '')).lower() if field == 'name' else g.get(field, ''),
                reverse=reverse
            )
            return sorted_groups
        except Exception as e:
            print(f"[GroupManager] Sort error: {e}")
            return groups
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about groups.
        
        Returns:
            Dict with metrics
        """
        groups = self._load_groups()
        
        return {
            "total_groups": len(groups),
            "has_description": len([g for g in groups if g.get('description', '').strip()]),
            "colors_used": len(set(g.get('color', '') for g in groups if g.get('color'))),
            "group_names": [g.get('name', '') for g in groups]
        }
    
    def export_to_list(self) -> List[str]:
        """
        Export list of group names (for use in dropdown, select).
        
        Returns:
            List of group names
        """
        groups = self._load_groups()
        return [g.get('name', '') for g in groups if g.get('name', '').strip()]


# ===== BACKWARD COMPATIBILITY WRAPPERS =====

def get_group(username: str, group_id: int) -> Dict[str, Any]:
    """Legacy wrapper."""
    manager = GroupManager(username)
    return manager.get(group_id)


def get_all_groups(username: str = None) -> List[Dict[str, Any]]:
    """Legacy wrapper."""
    manager = GroupManager(username)
    return manager.get_all()


def add_group(username: str, group_data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy wrapper."""
    manager = GroupManager(username)
    return manager.add(group_data)


def update_group(username: str, group_id: int, group_data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy wrapper."""
    manager = GroupManager(username)
    return manager.update(group_id, group_data)


def delete_group(username: str, group_id: int) -> Dict[str, Any]:
    """Legacy wrapper."""
    manager = GroupManager(username)
    return manager.delete(group_id)
