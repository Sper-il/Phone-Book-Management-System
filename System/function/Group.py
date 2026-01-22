"""
Group - Single group entity
Public attributes: id, name
"""
from datetime import datetime


class Group:
    """
    Group object representing a contact group.
    
    Attributes:
        id: Unique group ID (string)
        name: Group name (string)
    """
    
    DEFAULT_COLORS = [
        '#EF4444', '#F97316', '#F59E0B', '#22C55E', '#14B8A6',
        '#3B82F6', '#6366F1', '#A855F7', '#EC4899', '#6B7280'
    ]
    
    def __init__(self, id: str = None, name: str = "", color: str = None, 
                 description: str = "", is_shared: int = 0):
        """
        Initialize Group.
        
        Args:
            id: Group ID
            name: Group name
            color: Color (hex code)
            description: Group description
            is_shared: 0 = private, 1 = shared
        """
        self.id = id or str(datetime.now().timestamp()).replace('.', '')
        self.name = name
        self.color = color or self.DEFAULT_COLORS[0]
        self.description = description
        self.is_shared = is_shared
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert Group to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "is_shared": self.is_shared,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Group':
        """Create Group from dictionary."""
        group = cls(
            id=data.get('id'),
            name=data.get('name', ''),
            color=data.get('color'),
            description=data.get('description', ''),
            is_shared=data.get('is_shared', 0)
        )
        group.created_at = data.get('created_at', group.created_at)
        group.updated_at = data.get('updated_at', group.updated_at)
        return group
    
    def update(self, **kwargs):
        """Update group attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
    
    def __repr__(self):
        return f"Group(id={self.id}, name={self.name})"
    
    def __str__(self):
        return self.name
