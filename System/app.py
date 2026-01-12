from flask import Flask, jsonify, render_template, request, send_from_directory, abort
from function.search import load_all, search_by_name
import os

# optional sorter
try:
    from function.sorter import ContactsSorter
except Exception:
    ContactsSorter = None

# create Flask app; templates folder is './templates' next to this file
app = Flask(__name__)

# ===== HOME / DASHBOARD =====
@app.route("/")
def dashboard():
    return render_template(
        "user/contact_list_dashboard_1/code.html"
    )

# Serve test_user_data files (contacts.json) from templates/test_user_data
@app.route('/test_user_data/<path:filename>')
def test_user_file(filename):
    # serve from System/test_user_data
    data_dir = os.path.join(app.root_path, 'test_user_data')
    if not os.path.isdir(data_dir):
        abort(404)
    return send_from_directory(data_dir, filename)

# ===== LOAD ALL CONTACTS =====
@app.route("/api/contacts")
def api_contacts():
    return jsonify(load_all())

# ===== SEARCH =====
@app.route("/api/search")
def api_search():
    keyword = request.args.get("keyword", "")
    sort = request.args.get('sort', 'asc')
    by = request.args.get('by', 'name')
    results = search_by_name(keyword)
    # apply simple sorting server-side to match client expectations
    try:
        reverse = (sort == 'desc')
        results = sorted(results, key=lambda c: (c.get(by) or '').lower(), reverse=reverse)
    except Exception:
        pass
    return jsonify(results)

# ===== SORT APPLY (optional) =====
@app.route('/api/sort_apply')
def api_sort_apply():
    sort = request.args.get('sort', 'asc')
    by = request.args.get('by', 'name')
    save_flag = request.args.get('save', '0') == '1'
    data_dir = os.path.join(app.root_path, 'test_user_data')
    json_path = os.path.join(data_dir, 'contacts.json')
    if not os.path.isfile(json_path):
        return jsonify({"error": "contacts.json not found"}), 404
    if ContactsSorter:
        s = ContactsSorter()
        s.load_json(json_path)
        s.sort_by(by, reverse=(sort == 'desc'))
        if save_flag:
            s.save_json(json_path)
        return jsonify(s.get_contacts())
    else:
        # fallback: read/ sort / return
        try:
            import json as _json
            with open(json_path, 'r', encoding='utf-8') as f:
                contacts = _json.load(f)
        except Exception:
            return jsonify({"error": "failed to read contacts.json"}), 500
        try:
            contacts_sorted = sorted(contacts, key=lambda c: (c.get(by) or '').lower(), reverse=(sort=='desc'))
        except Exception:
            contacts_sorted = contacts
        if save_flag:
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    _json.dump(contacts_sorted, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        return jsonify(contacts_sorted)

# ===== RUN =====
if __name__ == "__main__":
    # run on port 5501 to match UI launcher
    app.run(host='127.0.0.1', port=5501, debug=True)