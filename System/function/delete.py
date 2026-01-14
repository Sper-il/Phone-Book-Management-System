"""
Delete module - Xoá contacts (OOP + backward compatibility)."""
from __future__ import annotations
from typing import List, Dict, Any, Optional


class ContactDeleter:
    """Xoá contact từ data source."""
    
    def __init__(self, data_source: Optional[List[Dict[str, Any]]] = None):
        self._data_source = data_source if data_source is not None else []
    
    def set_data(self, data_source: List[Dict[str, Any]]) -> 'ContactDeleter':
        """Set data source."""
        self._data_source = data_source
        return self
    
    def get_data(self) -> List[Dict[str, Any]]:
        """Get current data source."""
        return self._data_source
    
    def delete(self, item_id: int, current_user_id: Optional[int] = None, 
               owner_field: Optional[str] = None) -> Dict[str, Any]:
        """Xoá item theo ID."""
        if item_id is None:
            return {"success": False, "message": "ID không hợp lệ"}
        
        target = None
        for obj in self._data_source:
            if obj.get("id") == item_id:
                target = obj
                break
        
        if target is None:
            return {"success": False, "message": "Dữ liệu không tồn tại"}
        
        if owner_field is not None and current_user_id is not None:
            if target.get(owner_field) != current_user_id:
                return {"success": False, "message": "Không có quyền xoá"}
        
        self._data_source.remove(target)
        return {"success": True, "message": "Xoá thành công", "deleted_id": item_id}


# === Backward compatibility ===
def delete_item(item_id: int, data_source: List[Dict[str, Any]], 
                current_user_id: Optional[int] = None, 
                owner_field: Optional[str] = None) -> Dict[str, Any]:
    """Legacy wrapper - xoá item và modify original list."""
    return ContactDeleter(data_source).delete(item_id, current_user_id, owner_field)
