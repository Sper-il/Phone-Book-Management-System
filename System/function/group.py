"""
Group module - Quản lý nhóm (OOP + reusing existing modules).
Tận dụng sorter.py để I/O và delete.py để xóa.
"""
from __future__ import annotations
import os
from typing import List, Dict, Any, Optional

# Import các module có sẵn để tái sử dụng
try:
    from .sorter import ContactsSorter
    from .delete import ContactDeleter
except ImportError:
    from sorter import ContactsSorter
    from delete import ContactDeleter

class GroupManager:
    """Quản lý CRUD cho Groups (Danh sách nhóm)."""
    
    def __init__(self, root_path: str):
        # SỬA: Lưu vào groups.json thay vì contact.json để tránh ghi đè danh bạ
        self.file_path = os.path.join(root_path, 'test_user_data', 'groups.json')
        
        # Dùng Sorter để xử lý Load/Save file (Tái sử dụng code I/O)
        self._io_handler = ContactsSorter()
        self._loaded = False

    def _ensure_loaded(self):
        """Đảm bảo dữ liệu đã được load từ file."""
        if not self._loaded:
            if os.path.isfile(self.file_path):
                self._io_handler.load_json(self.file_path)
            else:
                # Nếu file chưa tồn tại, khởi tạo danh sách rỗng
                self._io_handler._contacts = []
            self._loaded = True

    def get_all(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tất cả các nhóm."""
        self._ensure_loaded()
        return self._io_handler.get_contacts() # Tái sử dụng hàm get của Sorter

    def add(self, name: str) -> Dict[str, Any]:
        """Thêm nhóm mới."""
        self._ensure_loaded()
        groups = self.get_all()
        
        # Tự động tăng ID
        new_id = 1
        if groups:
            new_id = max(g.get('id', 0) for g in groups) + 1
        
        new_group = {"id": new_id, "name": name}
        groups.append(new_group)
        
        # Lưu file ngay lập tức
        self._io_handler.save_json(self.file_path)
        return new_group

    def update(self, group_id: int, name: str) -> bool:
        """Cập nhật tên nhóm."""
        self._ensure_loaded()
        groups = self.get_all()
        
        for group in groups:
            if group.get('id') == group_id:
                group['name'] = name
                self._io_handler.save_json(self.file_path)
                return True
        return False

    def delete(self, group_id: int) -> bool:
        """Xóa nhóm (Tái sử dụng delete.py)."""
        self._ensure_loaded()
        groups = self.get_all()
        
        # Tái sử dụng ContactDeleter để xóa theo ID
        deleter = ContactDeleter(groups)
        result = deleter.delete(group_id)
        
        if result.get("success"):
            # Nếu xóa thành công trong RAM, cần lưu xuống file
            self._io_handler.save_json(self.file_path)
            return True
        return False

# === Instance global để dễ gọi từ app.py ===
_group_manager: Optional[GroupManager] = None

def get_group_manager(root_path: str) -> GroupManager:
    global _group_manager
    if not _group_manager:
        _group_manager = GroupManager(root_path)
    return _group_manager