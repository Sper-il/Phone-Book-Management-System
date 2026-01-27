# System Folder - Phone Book Management System

Đây là thư mục chính chứa toàn bộ mã nguồn của ứng dụng Quản lý Danh bạ Điện thoại.

## 📁 Cấu trúc thư mục

```
System/
├── app.py                      # File chính của ứng dụng Flask
├── README.md                   # File này
├── Data/                       # Thư mục lưu trữ dữ liệu
│   ├── Admin/                  # Dữ liệu của Admin
│   │   ├── admin_account/      # Tài khoản admin
│   │   │   └── admins.json
│   │   └── admin_data/         # Dữ liệu admin (contacts, groups)
│   │       ├── groups.json
│   │       └── admin_contacts.json
│   └── User/                   # Dữ liệu của User
│       ├── user_account/       # Tài khoản user
│       │   └── users.json
│       └── user_data/          # Dữ liệu user
│           ├── {username}_contacts.json
│           └── {username}_groups.json
├── function/                   # Các class Python (OOP)
│   ├── __init__.py
│   ├── BaseAuthentication.py
│   ├── User.py
│   ├── Admin.py
│   ├── AdminManager.py
│   ├── Contact.py
│   ├── ContactManager.py
│   ├── ContactListManager.py
│   ├── Group.py
│   └── GroupManager.py
└── templates/                  # Giao diện HTML
    ├── 403.html                # Trang lỗi Access Denied
    ├── admin/                  # Giao diện Admin
    │   ├── dashboard.html
    │   ├── contacts.html
    │   ├── groups.html
    │   ├── user_detail.html
    │   ├── login.html
    │   └── login_redirect.html
    └── user/                   # Giao diện User
        ├── index.html
        ├── Login.html
        ├── Registration.html
        ├── Forgot_Password.html
        ├── Contact_List.html
        ├── Add_Contact.html
        ├── Group.html
        └── Add_New_Group.html
```

---

## 🚀 File app.py - Ứng dụng chính

File `app.py` là điểm khởi đầu của ứng dụng Flask, chứa:

### Routes chính

| Route | Method | Mô tả |
|-------|--------|-------|
| `/` | GET | Trang chủ (redirect đến login/dashboard) |
| `/login` | GET | Trang đăng nhập User |
| `/register` | GET | Trang đăng ký |
| `/forgot-password` | GET | Trang quên mật khẩu |
| `/dashboard` | GET | Dashboard User (danh sách liên hệ) |
| `/groups` | GET | Quản lý nhóm User |
| `/add-contact` | GET | Thêm liên hệ mới |
| `/add-group` | GET | Thêm nhóm mới |
| `/admin/login` | GET | Trang đăng nhập Admin |
| `/admin/dashboard` | GET | Dashboard Admin |
| `/admin/contacts` | GET | Quản lý liên hệ Admin |
| `/admin/groups` | GET | Quản lý nhóm Admin |

### API Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/api/login` | POST | Đăng nhập (User/Admin) |
| `/api/register` | POST | Đăng ký tài khoản |
| `/api/logout` | POST | Đăng xuất |
| `/api/contacts` | GET | Lấy danh sách liên hệ |
| `/api/add` | POST | Thêm liên hệ |
| `/api/delete` | POST | Xóa liên hệ |
| `/api/groups` | GET/POST | Lấy/Thêm nhóm |
| `/api/groups/<id>` | DELETE | Xóa nhóm |
| `/admin/api/users` | GET | Lấy danh sách user |
| `/admin/api/contacts` | GET/POST | Quản lý liên hệ admin |
| `/admin/api/groups` | GET/POST | Quản lý nhóm admin |

---

## 📦 Thư mục function/ - Các Class Python

### 1. BaseAuthentication.py
Lớp cơ sở cho xác thực người dùng.

```python
class BaseAuthentication:
    - base_dir: str              # Đường dẫn gốc
    + _hash_password(password)   # Mã hóa mật khẩu SHA-256
    + _load_json(file_path)      # Đọc file JSON
    + _save_json(file_path, data)# Ghi file JSON
```

### 2. User.py
Quản lý xác thực và tài khoản User. Kế thừa từ `BaseAuthentication`.

```python
class User(BaseAuthentication):
    + register(username, password, fullname, phone, security_question, security_answer)
    + login(username, password)
    + reset_password(username, new_password)
    + verify_security_answer(username, answer)
    + get_user_by_username(username)
    + get_profile(username)
    + update_profile(username, data)
```

### 3. Admin.py
Quản lý xác thực Admin. Kế thừa từ `User`.

```python
class Admin(User):
    + login(username, password)  # Override để check admin
    + register(username, password)
    + is_admin(username)
    + get_all_admins()
```

### 4. AdminManager.py
Quản lý hệ thống cho Admin.

```python
class AdminManager:
    - users_file: str
    + get_all_users()            # Lấy tất cả user
    + get_user_by_username(username)
    + delete_user(username)      # Xóa user
    + update_user_password(username, new_password)
    + get_system_stats()         # Thống kê hệ thống
    + search_users(query)        # Tìm kiếm user
```

### 5. Contact.py
Data class đại diện cho một liên hệ.

```python
@dataclass
class Contact:
    - id: int
    - name: str
    - phone: str
    - group: str (optional)
    - notes: str (optional)
    - created_at: str
    - updated_at: str
```

### 6. ContactManager.py
Quản lý CRUD liên hệ cơ bản.

```python
class ContactManager:
    - username: str
    - data_dir: str
    + get(contact_id)            # Lấy 1 liên hệ
    + get_all()                  # Lấy tất cả liên hệ
    + add(contact_data)          # Thêm liên hệ
    + update(contact_id, data)   # Cập nhật liên hệ
    + update_partial(contact_id, data)
    + delete(contact_id)         # Xóa liên hệ
```

### 7. ContactListManager.py
Quản lý danh sách liên hệ với các tính năng nâng cao.

```python
class ContactListManager:
    - username: str
    - _cache: list               # Cache để tăng hiệu suất
    + get(contact_id)
    + get_all()
    + reload()                   # Tải lại từ file
    + add(contact_data)
    + update(contact_id, data)
    + delete(contact_id)
    + delete_all()               # Xóa tất cả
    + search(keyword, fields)    # Tìm kiếm
    + filter_by_group(group_name)# Lọc theo nhóm
    + assign_to_group(contact_id, group_name)
    + sort(field, ascending)     # Sắp xếp
    + sort_list(contacts, field, ascending)
    + count()                    # Đếm số liên hệ
    + get_groups()               # Lấy danh sách nhóm từ liên hệ
```

### 8. Group.py
Data class đại diện cho một nhóm.

```python
@dataclass
class Group:
    - id: int
    - name: str
    - color: str (optional, default: #3B82F6)
    - description: str (optional)
    - is_shared: int (0 hoặc 1)
    - created_at: str
    - updated_at: str
```

### 9. GroupManager.py
Quản lý CRUD nhóm liên hệ.

```python
class GroupManager:
    - username: str              # None = admin groups
    - groups_file: str
    + get(group_id)              # Lấy 1 nhóm
    + get_by_name(name)          # Lấy theo tên
    + get_all()                  # Lấy tất cả nhóm
    + add(group_data)            # Thêm nhóm
    + update(group_id, data)     # Cập nhật nhóm
    + delete(group_id)           # Xóa nhóm
    + search(keyword)            # Tìm kiếm nhóm
    + sort(field, ascending)     # Sắp xếp
```

---

## 💾 Thư mục Data/ - Lưu trữ dữ liệu

Dữ liệu được lưu dưới dạng JSON files.

### Cấu trúc Data/Admin/
```
Admin/
├── admin_account/
│   └── admins.json          # Danh sách tài khoản admin
└── admin_data/
    ├── groups.json          # Nhóm dùng chung cho admin
    └── admin_contacts.json  # Liên hệ của admin
```

### Cấu trúc Data/User/
```
User/
├── user_account/
│   └── users.json           # Danh sách tài khoản user
└── user_data/
    ├── john_doe_contacts.json    # Liên hệ của user john_doe
    ├── john_doe_groups.json      # Nhóm của user john_doe
    └── ...                       # Mỗi user có file riêng
```

### Định dạng dữ liệu

**users.json:**
```json
[
  {
    "username": "john_doe",
    "password": "hashed_password",
    "fullname": "John Doe",
    "phone": "0123456789",
    "security_question": "Your pet's name?",
    "security_answer": "hashed_answer",
    "created_at": "2026-01-22T10:00:00"
  }
]
```

**{username}_contacts.json:**
```json
[
  {
    "id": 1,
    "name": "Alice Johnson",
    "phone": "0987654321",
    "group": "Family",
    "notes": "Sister",
    "created_at": "2026-01-22T10:00:00",
    "updated_at": "2026-01-22T10:00:00"
  }
]
```

**{username}_groups.json:**
```json
[
  {
    "id": 1,
    "name": "Family",
    "color": "#3B82F6",
    "description": "Family members",
    "is_shared": 0,
    "created_at": "2026-01-22T10:00:00",
    "updated_at": "2026-01-22T10:00:00"
  }
]
```

---

## 🎨 Thư mục templates/ - Giao diện

### Công nghệ sử dụng
- **Tailwind CSS** - Framework CSS
- **Google Material Symbols** - Icons
- **JavaScript (Vanilla)** - Xử lý logic phía client

### templates/user/ - Giao diện User

| File | Mô tả |
|------|-------|
| `index.html` | Trang chủ/Landing page |
| `Login.html` | Đăng nhập |
| `Registration.html` | Đăng ký tài khoản |
| `Forgot_Password.html` | Khôi phục mật khẩu |
| `Contact_List.html` | Danh sách liên hệ (Dashboard chính) |
| `Add_Contact.html` | Form thêm liên hệ mới |
| `Group.html` | Quản lý nhóm |
| `Add_New_Group.html` | Form thêm nhóm mới |

### templates/admin/ - Giao diện Admin

| File | Mô tả |
|------|-------|
| `login.html` | Đăng nhập Admin |
| `login_redirect.html` | Chuyển hướng sau đăng nhập |
| `dashboard.html` | Dashboard quản trị (User Management) |
| `user_detail.html` | Chi tiết thông tin user |
| `contacts.html` | Quản lý liên hệ Admin |
| `groups.html` | Quản lý nhóm Admin |

### templates/403.html
Trang lỗi Access Denied khi truy cập không có quyền.

---

## ⚡ Các tính năng chính

### Tính năng User
- ✅ Đăng ký / Đăng nhập / Đăng xuất
- ✅ Khôi phục mật khẩu qua câu hỏi bảo mật
- ✅ Xem danh sách liên hệ
- ✅ Thêm liên hệ mới
- ✅ Xóa liên hệ / Xóa tất cả
- ✅ Tìm kiếm theo tên, số điện thoại, nhóm
- ✅ Tìm kiếm nâng cao: `gr:TenNhom`
- ✅ Sắp xếp theo tên, số điện thoại, nhóm
- ✅ Quản lý nhóm (thêm, xóa)
- ✅ Gán liên hệ vào nhóm

### Tính năng Admin
- ✅ Đăng nhập Admin riêng biệt
- ✅ Xem danh sách tất cả User
- ✅ Xem chi tiết User
- ✅ Xóa User
- ✅ Thống kê hệ thống
- ✅ Quản lý liên hệ Admin
- ✅ Quản lý nhóm Admin (dùng chung)

### Giao diện
- ✅ Responsive design
- ✅ Toast notifications (thay thế alert)
- ✅ Custom confirm dialogs (thay thế confirm)
- ✅ Giao diện tiếng Anh

---

## 🔧 Cách chạy ứng dụng

```bash
cd System
python app.py
```

Truy cập: http://127.0.0.1:5501

---

## 📝 Ghi chú

- Mật khẩu được mã hóa bằng SHA-256
- Dữ liệu lưu dạng JSON, không cần database
- Mỗi user có file contacts và groups riêng biệt
- Admin dùng chung file groups.json
