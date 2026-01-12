import json
import csv
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# use System/test_user_data (explicit)
POSSIBLE_DIRS = [
    os.path.join(BASE_DIR, 'test_user_data')
]


def _find_data_dir():
    for d in POSSIBLE_DIRS:
        if os.path.isdir(d):
            print(f"[search] using data dir: {d}")
            return d
    print(f"[search] no data dir found; checked: {POSSIBLE_DIRS}", file=sys.stderr)
    return POSSIBLE_DIRS[0]


def _load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and 'contacts' in data:
                return data['contacts']
            return []
    except Exception as e:
        print(f"[search] error loading json {path}: {e}", file=sys.stderr)
        return []


def _load_csv(path):
    contacts = []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacts.append({
                    'id': int(row.get('id') or 0),
                    'name': row.get('name') or '',
                    'phone': row.get('phone') or '',
                    'group': row.get('group') or ''
                })
    except Exception as e:
        print(f"[search] error loading csv {path}: {e}", file=sys.stderr)
        return []
    return contacts


def load_all():
    data_dir = _find_data_dir()
    json_path = os.path.join(data_dir, 'contacts.json')
    csv_path = os.path.join(data_dir, 'contacts.csv')
    if os.path.isfile(json_path):
        return _load_json(json_path)
    if os.path.isfile(csv_path):
        return _load_csv(csv_path)
    return []


def search_by_name(keyword: str):
    keyword = (keyword or '').lower().strip()
    contacts = load_all()

    if not keyword:
        return contacts

    results = []
    for c in contacts:
        try:
            if keyword in (c.get('name') or '').lower():
                results.append(c)
        except Exception:
            continue

    return results
