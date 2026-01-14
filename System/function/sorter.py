"""Sorter module - Load, sort và save contacts (OOP + backward compatibility)."""
from __future__ import annotations
import json, csv
from pathlib import Path
from typing import List, Dict, Optional, Any


class ContactsSorter:
    """Load/sort/save contacts từ JSON hoặc CSV."""

    def __init__(self, contacts: Optional[List[Dict[str, Any]]] = None):
        self._contacts: List[Dict[str, Any]] = contacts or []

    def load_json(self, path: str | Path) -> 'ContactsSorter':
        try:
            with Path(path).open('r', encoding='utf-8') as f:
                data = json.load(f)
                self._contacts = data if isinstance(data, list) else data.get('contacts', [])
        except Exception as e:
            print(f"[Sorter] JSON error: {e}")
            self._contacts = []
        return self

    def load_csv(self, path: str | Path) -> 'ContactsSorter':
        try:
            with Path(path).open('r', encoding='utf-8') as f:
                self._contacts = [dict(row) for row in csv.DictReader(f)]
        except Exception as e:
            print(f"[Sorter] CSV error: {e}")
            self._contacts = []
        return self

    def get_contacts(self) -> List[Dict[str, Any]]:
        return list(self._contacts)

    def sort_by(self, field: str = 'name', reverse: bool = False) -> 'ContactsSorter':
        if field == 'phone':
            key = lambda c: int(''.join(ch for ch in (c.get('phone') or '') if ch.isdigit()) or '0')
        else:
            key = lambda c: (c.get(field) or '').lower()
        self._contacts.sort(key=key, reverse=reverse)
        return self

    def save_json(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('w', encoding='utf-8') as f:
            json.dump(self._contacts, f, ensure_ascii=False, indent=2)

    def save_csv(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not self._contacts:
            with p.open('w', encoding='utf-8', newline='') as f:
                csv.writer(f).writerow(['id', 'name', 'phone', 'group'])
            return
        with p.open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=self._contacts[0].keys())
            w.writeheader()
            w.writerows(self._contacts)


# === Backward compatibility ===
_sorter: Optional[ContactsSorter] = None

def _get_sorter() -> ContactsSorter:
    global _sorter
    if not _sorter:
        _sorter = ContactsSorter()
    return _sorter

def load_json(path: str) -> List[Dict[str, Any]]:
    """Legacy wrapper - load từ JSON."""
    return _get_sorter().load_json(path).get_contacts()

def load_csv(path: str) -> List[Dict[str, Any]]:
    """Legacy wrapper - load từ CSV."""
    return _get_sorter().load_csv(path).get_contacts()

def sort_contacts(contacts: List[Dict[str, Any]], field: str = 'name', 
                  reverse: bool = False) -> List[Dict[str, Any]]:
    """Legacy wrapper - sort danh sách contacts."""
    return ContactsSorter(contacts).sort_by(field, reverse).get_contacts()
