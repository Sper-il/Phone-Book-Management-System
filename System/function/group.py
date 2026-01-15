import json
import os

def load_groups(json_path):
    """Đọc danh sách nhóm từ file JSON."""
    if not os.path.exists(json_path):
        return []
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading groups: {e}")
        return []

def save_groups_to_file(json_path, groups_data):
    """Ghi danh sách nhóm vào file JSON."""
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(groups_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving groups: {e}")
        return False

def add_group(json_path, group_name):
    """Thêm một nhóm mới."""
    groups = load_groups(json_path)
    
    # Tạo ID tự động (Auto-increment)
    new_id = 1
    if groups:
        new_id = max(g.get('id', 0) for g in groups) + 1
        
    new_group = {
        "id": new_id,
        "name": group_name
    }
    
    groups.append(new_group)
    if save_groups_to_file(json_path, groups):
        return new_group
    return None

def update_group(json_path, group_id, new_name):
    """Cập nhật tên nhóm."""
    groups = load_groups(json_path)
    updated = False
    
    for group in groups:
        if group.get('id') == group_id:
            group['name'] = new_name
            updated = True
            break
            
    if updated:
        save_groups_to_file(json_path, groups)
        return True
    return False

def delete_group(json_path, group_id):
    """Xóa nhóm theo ID."""
    groups = load_groups(json_path)
    initial_count = len(groups)
    
    # Lọc bỏ group có id trùng khớp
    groups = [g for g in groups if g.get('id') != group_id]
    
    if len(groups) < initial_count:
        save_groups_to_file(json_path, groups)
        return True
    return False