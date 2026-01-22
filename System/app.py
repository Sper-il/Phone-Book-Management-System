from flask import Flask, jsonify, render_template, request, send_from_directory, abort, session, redirect, url_for
from functools import wraps
from function.ContactListManager import ContactListManager
from function.GroupManager import GroupManager
from function.User import User
from function.AdminManager import AdminManager
from function.Admin import Admin
from function.ContactManager import ContactManager
import os
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

auth = User()
admin_auth = Admin()
admin_manager = AdminManager()

# ===== DECORATORS =====
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        if not session.get('is_admin', False):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        if session.get('is_admin', False):
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ===== VIEWS =====
@app.route("/")
def index():
    if 'user' in session:
        if session.get('is_admin', False):
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/dashboard")
@user_required
def dashboard():
    current_user = session.get('user', 'User')
    return render_template("user/Contact_List.html", current_user=current_user)

@app.route("/groups")
@user_required
def groups():
    current_user = session.get('user', 'User')
    return render_template("user/Group.html", current_user=current_user)

@app.route("/add-group")
@user_required
def add_group():
    return render_template("user/Add_New_Group.html")

@app.route("/add-contact")
@user_required
def add_contact():
    return render_template("user/Add_Contact.html")

@app.route("/login")
def login():
    """Common login page for both admin and user"""
    if 'user' in session:
        if session.get('is_admin'):
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return render_template("user/Login.html")

@app.route("/admin/login")
def admin_login():
    """Redirect admin login to common login page"""
    if 'user' in session and session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))

@app.route("/register")
def register():
    return render_template("user/Registration.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("user/Forgot_Password.html")

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    stats = admin_manager.get_system_stats()
    users = admin_manager.get_all_users()
    return render_template("admin/dashboard.html", stats=stats, users=users)

@app.route("/admin/groups")
@admin_required
def admin_groups():
    return render_template("admin/groups.html")

@app.route("/admin/contacts")
@admin_required
def admin_contacts():
    return render_template("admin/contacts.html")

# ===== AUTH API =====
@app.route("/api/login", methods=["POST"])
def api_unified_login():
    """Unified login for both admin and user"""
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    
    # Try admin login first
    success, message, admin_data = admin_auth.login(username, password)
    if success:
        session['user'] = username
        session['is_admin'] = True
        return jsonify({"success": True, "message": message, "redirect": "/admin/dashboard", "is_admin": True})
    
    # Try user login
    success, message, user_data = auth.login(username, password)
    if success:
        session['user'] = username
        session['is_admin'] = False
        return jsonify({"success": True, "message": message, "redirect": "/dashboard", "is_admin": False})
    
    return jsonify({"success": False, "message": "Invalid username or password"}), 401

@app.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    """Legacy admin login - redirect to unified login"""
    return api_unified_login()

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    security_question = data.get("security_question", "")
    security_answer = data.get("security_answer", "")
    success, message = auth.register(username, password, security_question, security_answer)
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400

@app.route("/api/security-question", methods=["GET"])
def api_security_question():
    username = request.args.get("username")
    question = auth.get_security_question(username)
    if question:
        return jsonify({"success": True, "question": question})
    return jsonify({"success": False, "message": "User not found"}), 404

@app.route("/api/verify-security-answer", methods=["POST"])
def api_verify_security_answer():
    """Verify security answer (FDD: Forgot Password flow)"""
    data = request.get_json() or {}
    username = data.get("username")
    answer = data.get("security_answer")
    
    success, message = auth.verify_security_answer(username, answer)
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400

@app.route("/api/reset-password", methods=["POST"])
def api_reset_password():
    data = request.get_json() or {}
    username = data.get("username")
    security_answer = data.get("security_answer")
    new_password = data.get("new_password")
    success, message = auth.reset_password(username, security_answer, new_password)
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400

@app.route("/logout", methods=["GET"])
def logout():
    """Logout route for direct link access"""
    session.clear()
    return redirect(url_for('login'))

@app.route("/api/logout", methods=["POST"])
def api_logout():
    """Logout API for AJAX calls"""
    session.clear()
    return jsonify({"success": True, "message": "Logged out"})

# ===== ADMIN USER MANAGEMENT API =====
@app.route("/admin/api/users", methods=["GET"])
@admin_required
def admin_get_users():
    users = admin_manager.get_all_users()
    return jsonify({"success": True, "users": users})

@app.route("/admin/api/stats", methods=["GET"])
@admin_required
def admin_get_stats():
    stats = admin_manager.get_system_stats()
    return jsonify({"success": True, "stats": stats})

@app.route("/admin/api/user/<username>", methods=["GET"])
@admin_required
def admin_get_user(username):
    user = admin_manager.get_user_by_username(username)
    if user:
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "message": "User not found"}), 404

@app.route("/admin/api/user/<username>", methods=["DELETE"])
@admin_required
def admin_delete_user(username):
    success, message = admin_manager.delete_user(username)
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400

@app.route("/admin/api/users/search", methods=["GET"])
@admin_required
def admin_search_users():
    query = request.args.get("query", "")
    users = admin_manager.search_users(query)
    return jsonify({"success": True, "users": users})

# ===== ADMIN CONTACTS API =====
@app.route("/admin/api/contacts", methods=["GET"])
@admin_required
def admin_get_contacts():
    """Get admin's contacts using ContactListManager"""
    admin_username = session.get('user')
    # For admin, use None username to access admin data directory
    manager = ContactListManager(admin_username)
    contacts = manager.get_all()
    return jsonify(contacts)

@app.route("/admin/api/contact", methods=["POST"])
@admin_required
def admin_add_update_contact():
    """Add or update admin's contact using ContactManager"""
    admin_username = session.get('user')
    data = request.get_json() or {}
    contact_id = data.get("id")
    
    manager = ContactManager(admin_username)
    
    if contact_id:
        result = manager.update(contact_id, data)
    else:
        result = manager.add(data)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400

@app.route("/admin/api/contact", methods=["DELETE"])
@admin_required
def admin_delete_contact():
    """Delete admin's contact using ContactListManager"""
    admin_username = session.get('user')
    data = request.get_json() or {}
    contact_id = data.get("id")
    
    if not contact_id:
        return jsonify({"success": False, "message": "ID is required"}), 400
    
    try:
        contact_id = int(contact_id)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid ID"}), 400
    
    manager = ContactListManager(admin_username)
    result = manager.delete(contact_id)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 404

# ===== ADMIN GROUPS API =====
@app.route("/admin/api/groups", methods=["GET"])
@admin_required
def admin_get_groups():
    """Get admin's groups using GroupManager"""
    admin_username = session.get('user')
    # Use None for shared admin groups
    manager = GroupManager(username=None)
    groups = manager.get_all()
    
    # Calculate contact_count for each group
    contact_manager = ContactListManager(admin_username)
    all_contacts = contact_manager.get_all()
    
    for group in groups:
        group_name = group.get('name', '')
        count = sum(1 for c in all_contacts if str(c.get('group', '')).lower() == str(group_name).lower())
        group['contact_count'] = count
    
    return jsonify({"success": True, "groups": groups})

@app.route("/admin/api/groups", methods=["POST", "PUT"])
@admin_required
def admin_add_update_group():
    """Add or update admin's group using GroupManager"""
    data = request.get_json() or {}
    group_id = data.get("id")
    
    manager = GroupManager(username=None)
    
    if group_id:
        result = manager.update(group_id, data)
    else:
        result = manager.add(data)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400

@app.route("/admin/api/groups/<int:group_id>", methods=["DELETE"])
@admin_required
def admin_delete_group(group_id):
    """Delete admin's group using GroupManager"""
    manager = GroupManager(username=None)
    result = manager.delete(group_id)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 404

@app.route("/admin/api/groups/<int:group_id>/contacts", methods=["GET"])
@admin_required
def admin_get_group_contacts(group_id):
    """Get contacts in a specific group using ContactListManager"""
    admin_username = session.get('user')
    manager = ContactListManager(admin_username)
    # Lookup group name from GroupManager (admin/shared groups)
    gm = GroupManager(username=None)
    group_res = gm.get(group_id)
    if not group_res.get('success'):
        return jsonify({"success": False, "message": "Group not found"}), 404

    group_name = group_res['group'].get('name', '')

    # Get all contacts and filter by group name (contacts store group as name)
    all_contacts = manager.get_all()
    contacts = [c for c in all_contacts if str(c.get('group', '')).lower() == str(group_name).lower()]

    return jsonify({"success": True, "contacts": contacts})

# ===== USER CONTACTS API =====
@app.route("/api/contacts")
@user_required
def api_contacts():
    username = session.get('user')
    if not username:
        return jsonify([])
    manager = ContactListManager(username)
    contacts = manager.get_all()
    return jsonify(contacts)

@app.route("/api/search")
@user_required
def api_search():
    username = session.get('user')
    if not username:
        return jsonify([])
    keyword = request.args.get("keyword", "")
    sort = request.args.get('sort', 'asc')
    by = request.args.get('by', 'name')
    
    manager = ContactListManager(username)
    results = manager.search(keyword) if keyword else manager.get_all()
    # Sort the filtered results (don't sort the full data unintentionally)
    try:
        results = manager.sort_list(results, field=by, reverse=(sort == 'desc'))
    except AttributeError:
        # Backwards compatibility: if sort_list missing, fall back to sort()
        results = manager.sort(field=by, reverse=(sort == 'desc'))

    return jsonify(results)

@app.route('/api/sort_apply')
@user_required
def api_sort_apply():
    username = session.get('user')
    if not username:
        return jsonify({"error": "User not logged in"}), 401
    sort = request.args.get('sort', 'asc')
    by = request.args.get('by', 'name')
    
    manager = ContactListManager(username)
    contacts = manager.sort(field=by, reverse=(sort == 'desc'))
    return jsonify(contacts)

@app.route('/api/filter')
@user_required
def api_filter_by_group():
    """Filter contacts by group (FDD: Filter Contact)"""
    username = session.get('user')
    if not username:
        return jsonify({"error": "User not logged in"}), 401
    
    group = request.args.get('group', '')
    
    manager = ContactListManager(username)
    contacts = manager.filter_by_group(group)
    return jsonify(contacts)

@app.route("/api/delete", methods=["POST"])
@user_required
def api_delete_contact():
    username = session.get('user')
    if not username:
        return jsonify({"success": False, "message": "User not logged in"}), 401
    
    data = request.get_json() or {}
    item_id = data.get("id")
    
    try:
        item_id = int(item_id)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid ID"}), 400
    
    manager = ContactListManager(username)
    result = manager.delete(item_id)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 500

@app.route("/api/contact", methods=["POST"])
@user_required
def api_add_or_update_contact():
    """Add or update contact using unified ContactManager"""
    username = session.get('user')
    if not username:
        return jsonify({"success": False, "message": "User not logged in"}), 401
    
    data = request.get_json() or {}
    contact_id = data.get("id")
    
    manager = ContactManager(username)
    
    # Use add or update based on presence of ID
    if contact_id:
        result = manager.update(contact_id, data)
    else:
        result = manager.add(data)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400

# ===== USER GROUPS API =====
@app.route("/api/groups", methods=["GET"])
@user_required
def api_get_groups():
    """Get user's groups using GroupManager"""
    username = session.get('user')
    manager = GroupManager(username)
    groups = manager.get_all()
    
    # Calculate contact_count for each group
    contact_manager = ContactListManager(username)
    all_contacts = contact_manager.get_all()
    
    for group in groups:
        group_name = group.get('name', '')
        count = sum(1 for c in all_contacts if str(c.get('group', '')).lower() == str(group_name).lower())
        group['contact_count'] = count
    
    return jsonify({"success": True, "groups": groups})

@app.route("/api/groups", methods=["POST"])
@user_required
def api_add_group():
    """Add new group using GroupManager"""
    username = session.get('user')
    data = request.get_json() or {}
    
    manager = GroupManager(username)
    result = manager.add(data)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400

@app.route("/api/groups/<int:group_id>", methods=["DELETE"])
@user_required
def api_delete_group(group_id):
    """Delete user's group using GroupManager"""
    username = session.get('user')
    manager = GroupManager(username)
    result = manager.delete(group_id)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 404

# ===== CONTACT EDIT API =====
@app.route("/api/contact/<int:contact_id>", methods=["GET"])
@user_required
def api_get_contact(contact_id):
    """Get single contact by ID"""
    username = session.get('user')
    manager = ContactManager(username)
    result = manager.get(contact_id)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 404

@app.route("/api/contact/<int:contact_id>", methods=["PUT"])
@user_required
def api_update_contact(contact_id):
    """Update contact by ID"""
    username = session.get('user')
    data = request.get_json() or {}
    
    manager = ContactManager(username)
    result = manager.update(contact_id, data)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400

@app.route("/api/contact/<int:contact_id>/assign-group", methods=["PUT"])
@user_required
def api_assign_contact_to_group(contact_id):
    """Assign contact to group (FDD: Assign Contact to Group)"""
    username = session.get('user')
    data = request.get_json() or {}
    group_name = data.get("group", "")
    
    manager = ContactListManager(username)
    result = manager.assign_to_group(contact_id, group_name)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400

# ===== USER PROFILE API =====
@app.route("/api/profile", methods=["GET"])
@user_required
def api_get_profile():
    """Get current user's profile"""
    username = session.get('user')
    result = auth.get_profile(username)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 404

@app.route("/api/profile", methods=["PUT"])
@user_required
def api_update_profile():
    """Update current user's profile"""
    username = session.get('user')
    data = request.get_json() or {}
    
    result = auth.update_profile(username, data)
    
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400

# ===== ERROR HANDLERS =====
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('403.html'), 404

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5501, debug=True)
