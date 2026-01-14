from flask import Flask, jsonify, render_template, request, send_from_directory, abort
from function.search import load_all, search_by_name
from function.delete import delete_item
import os

# optional sorter
try:
    from function.sorter import ContactsSorter
except Exception:
    ContactsSorter = None

app = Flask(__name__)

# ===== HOME / DASHBOARD =====
@app.route("/")
def dashboard():
    return render_template(
        "user/contact_list_dashboard_1/code.html"
    )

@app.route("/dashboard1")
def dashboard1():
    return render_template("user/contact_list_dashboard_1/code.html")

@app.route("/dashboard2")
def dashboard2():
    return render_template("user/contact_list_dashboard_2/code.html")

@app.route("/dashboard3")
def dashboard3():
    return render_template("user/contact_list_dashboard_3/code.html")

@app.route("/add-contact")
def add_contact():
    return render_template("user/add_contact_modal/code.html")

# ===== AUTH SCREENS =====
@app.route("/login")
def login():
    return render_template("login_screen/code.html")

@app.route("/register")
def register():
    return render_template("registration_screen/code.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password_screen/code.html")

# ===== SERVE TEST DATA FILES =====
@app.route('/test_user_data/<path:filename>')
def test_user_file(filename):
    data_dir = os.path.join(app.root_path, 'System', 'test_user_data')
    if not os.path.isdir(data_dir):
        abort(404)
    return send_from_directory(data_dir, filename)

# ===== LOAD ALL CONTACTS =====
@app.route("/api/contacts")
def api_contacts():
    import json, os

    # app.root_path == System/
    data_dir = os.path.join(app.root_path, 'test_user_data')
    json_path = os.path.join(data_dir, 'contacts.json')

    if not os.path.isfile(json_path):
        print("❌ Không tìm thấy:", json_path)
        return jsonify([])

    with open(json_path, 'r', encoding='utf-8') as f:
        return jsonify(json.load(f))


# ===== SEARCH =====
@app.route("/api/search")
def api_search():
    keyword = request.args.get("keyword", "")
    sort = request.args.get('sort', 'asc')
    by = request.args.get('by', 'name')
    results = search_by_name(keyword)
    try:
        reverse = (sort == 'desc')
        results = sorted(
            results,
            key=lambda c: (c.get(by) or '').lower(),
            reverse=reverse
        )
    except Exception:
        pass
    return jsonify(results)

# ===== SORT APPLY (optional) =====
@app.route('/api/sort_apply')
def api_sort_apply():
    sort = request.args.get('sort', 'asc')
    by = request.args.get('by', 'name')
    save_flag = request.args.get('save', '0') == '1'

    data_dir = os.path.join(app.root_path, 'System', 'test_user_data')
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
        try:
            import json as _json
            with open(json_path, 'r', encoding='utf-8') as f:
                contacts = _json.load(f)
        except Exception:
            return jsonify({"error": "failed to read contacts.json"}), 500

        try:
            contacts = sorted(
                contacts,
                key=lambda c: (c.get(by) or '').lower(),
                reverse=(sort == 'desc')
            )
        except Exception:
            pass

        if save_flag:
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    _json.dump(contacts, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        return jsonify(contacts)

# ===== DELETE CONTACT =====
@app.route("/api/delete", methods=["POST"])
def api_delete_contact():
    import json, os

    data = request.get_json() or {}
    try:
        item_id = int(data.get("id"))
    except:
        return jsonify({"success": False, "message": "ID không hợp lệ"}), 400

    data_dir = os.path.join(app.root_path, 'test_user_data')
    json_path = os.path.join(data_dir, 'contacts.json')

    if not os.path.isfile(json_path):
        return jsonify({"success": False, "message": "Không tìm thấy contacts.json"}), 404

    with open(json_path, 'r', encoding='utf-8') as f:
        contacts = json.load(f)

    contacts = [c for c in contacts if c.get("id") != item_id]

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)

    return jsonify({"success": True})

# ===== ADD OR UPDATE CONTACT =====
@app.route("/api/contact", methods=["POST"])
def api_add_or_update_contact():
    import json, os

    data = request.get_json() or {}
    
    data_dir = os.path.join(app.root_path, 'test_user_data')
    json_path = os.path.join(data_dir, 'contacts.json')

    # Load existing contacts
    if os.path.isfile(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            contacts = json.load(f)
    else:
        contacts = []

    # Check if updating or adding
    contact_id = data.get("id")
    if contact_id:
        # Update existing contact
        for i, contact in enumerate(contacts):
            if contact.get("id") == contact_id:
                contacts[i] = data
                break
        else:
            return jsonify({"success": False, "message": "Không tìm thấy contact"}), 404
    else:
        # Add new contact with auto-generated ID
        if contacts:
            max_id = max(c.get("id", 0) for c in contacts)
            data["id"] = max_id + 1
        else:
            data["id"] = 1
        contacts.append(data)

    # Save to file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)

    return jsonify({"success": True, "contact": data})


# ===== RUN =====
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5501, debug=True)