import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "templates","test_user_data", "contacts.csv")


def load_all():
    contacts = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)
    return contacts


def search_by_name(keyword: str):
    keyword = keyword.lower().strip()
    contacts = load_all()

    if not keyword:
        return contacts

    results = []
    for c in contacts:
        if keyword in c["name"].lower():
            results.append(c)

    return results
