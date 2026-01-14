"""
Search module - Tìm kiếm contacts (OOP + backward compatibility)."""
from __future__ import annotations
import os
from typing import List, Dict, Any, Optional

try:
    from .sorter import ContactsSorter
except ImportError:
    from sorter import ContactsSorter


class ContactSearcher:
    """Tìm kiếm contacts từ file JSON/CSV."""
    
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_user_data')
    DEFAULT_FIELDS = ['name', 'phone']
    
    def __init__(self, data_dir: Optional[str] = None):
        self._data_dir = data_dir or self.DATA_DIR
        self._sorter = ContactsSorter()
        self._loaded = False
    
    def load(self) -> 'ContactSearcher':
        """Load contacts từ JSON hoặc CSV."""
        self._sorter = ContactsSorter()  # Reset sorter
        for ext in ['json', 'csv']:
            path = os.path.join(self._data_dir, f'contacts.{ext}')
            if os.path.isfile(path):
                getattr(self._sorter, f'load_{ext}')(path)
                self._loaded = True
                break
        return self
    
    def reload(self) -> 'ContactSearcher':
        """Force reload contacts từ file."""
        self._loaded = False
        return self.load()
    
    def get_all(self) -> List[Dict[str, Any]]:
        if not self._loaded: self.load()
        return self._sorter.get_contacts()
    
    def search(self, keyword: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Tìm kiếm theo keyword trong các fields."""
        if fields is None:
            fields = self.DEFAULT_FIELDS
        kw = (keyword or '').lower().strip()
        if not kw: return self.get_all()
        return [c for c in self.get_all() 
                if any(kw in (c.get(f) or '').lower() for f in fields)]
    
    def search_by_name(self, keyword: str) -> List[Dict[str, Any]]:
        return self.search(keyword, ['name'])
    
    def search_by_phone(self, keyword: str) -> List[Dict[str, Any]]:
        return self.search(keyword, ['phone'])
    
    def search_by_name_or_phone(self, keyword: str) -> List[Dict[str, Any]]:
        return self.search(keyword, ['name', 'phone'])
    
    def sort(self, field: str = 'name', reverse: bool = False) -> List[Dict[str, Any]]:
        if not self._loaded: self.load()
        return self._sorter.sort_by(field, reverse).get_contacts()


# === Backward compatibility ===
_searcher: Optional[ContactSearcher] = None

def _get_searcher(force_reload: bool = False) -> ContactSearcher:
    global _searcher
    if not _searcher:
        _searcher = ContactSearcher().load()
    elif force_reload:
        _searcher.reload()
    return _searcher

def reload_contacts() -> None:
    """Force reload contacts từ file."""
    _get_searcher(force_reload=True)

def load_all() -> List[Dict[str, Any]]:
    """Legacy wrapper - load tất cả contacts (always fresh)."""
    return _get_searcher(force_reload=True).get_all()

def search_by_name(keyword: str) -> List[Dict[str, Any]]:
    """Legacy wrapper - tìm theo tên."""
    return _get_searcher(force_reload=True).search_by_name(keyword)

def search_by_phone(keyword: str) -> List[Dict[str, Any]]:
    """Legacy wrapper - tìm theo số điện thoại."""
    return _get_searcher(force_reload=True).search_by_phone(keyword)

def search_by_name_or_phone(keyword: str) -> List[Dict[str, Any]]:
    """Legacy wrapper - tìm theo tên hoặc SĐT."""
    return _get_searcher(force_reload=True).search_by_name_or_phone(keyword)
