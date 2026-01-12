from flask import Flask, jsonify, render_template, request
from function.search import load_all, search_by_name

# ✅ PHẢI tạo app trước
app = Flask(__name__)

# ===== HOME / DASHBOARD =====
@app.route("/")
def dashboard():
    return render_template(
        "user/contact_list_dashboard_1/code.html"
    )

# ===== LOAD ALL CONTACTS =====
@app.route("/api/contacts")
def api_contacts():
    return jsonify(load_all())

# ===== SEARCH =====
@app.route("/api/search")
def api_search():
    keyword = request.args.get("keyword", "")
    return jsonify(search_by_name(keyword))

# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)
