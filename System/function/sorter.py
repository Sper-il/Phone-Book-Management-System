from __future__ import annotations
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any


class ContactsSorter:
    """Load contacts from JSON or CSV, sort them by a given field, and save back.

    Each contact is represented as a dict with keys: id, name, phone, group (strings/ints).
    """

    def __init__(self, contacts: Optional[List[Dict[str, Any]]] = None):
        self._contacts: List[Dict[str, Any]] = contacts or []

    def load_json(self, path: str | Path) -> None:
        p = Path(path)
        with p.open('r', encoding='utf-8') as f:
            self._contacts = json.load(f)

    def load_csv(self, path: str | Path) -> None:
        p = Path(path)
        with p.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self._contacts = [dict(row) for row in reader]

    def get_contacts(self) -> List[Dict[str, Any]]:
        return list(self._contacts)

    def sort_by(self, field: str, reverse: bool = False, key: Optional[Callable[[Dict[str, Any]], Any]] = None) -> None:
        """Sort contacts in-place by field. If key is provided, it will be used on each contact.

        Common fields: 'name', 'phone', 'group'. Sorting is case-insensitive for strings.
        """
        if not key:
            field = str(field)
            if field == 'name' or field == 'group':
                key = lambda c: (c.get(field) or '').lower()
            elif field == 'phone':
                # normalize phone to digits for numeric-like sorting
                def _phone_key(c):
                    ph = c.get('phone') or ''
                    digits = ''.join(ch for ch in ph if ch.isdigit())
                    return int(digits) if digits else ph
                key = _phone_key
            else:
                key = lambda c: c.get(field)

        self._contacts.sort(key=key, reverse=reverse)

    def save_json(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('w', encoding='utf-8') as f:
            json.dump(self._contacts, f, ensure_ascii=False, indent=2)

    def save_csv(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not self._contacts:
            # write empty file with headers
            with p.open('w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'name', 'phone', 'group'])
            return
        keys = list(self._contacts[0].keys())
        with p.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in self._contacts:
                writer.writerow(r)


if __name__ == '__main__':
    # small self-test when run directly
    import sys
    p = Path(__file__).parent.parent / 'test_user_data' / 'contacts.json'
    if not p.exists():
        print('No test data found at', p)
        sys.exit(1)
    s = ContactsSorter()
    s.load_json(p)
    print('Loaded', len(s.get_contacts()), 'contacts')
    s.sort_by('name')
    print('First after sort:', s.get_contacts()[0].get('name'))
