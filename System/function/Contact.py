"""
Contact - Single contact entity
Public attributes: id, name, phone
"""
from typing import Optional
from datetime import datetime


class Contact:
    """
    Contact object representing a contact in the phonebook.
    
    Attributes:
        id: Unique contact ID (string)
        name: Contact name (string)
        phone: Phone number (string)
    """
    
    def __init__(self, id: str = None, name: str = "", phone: str = "", 
                 email: str = "", address: str = "", group: str = "", 
                 notes: str = "", avatar: str = ""):
        """
        Initialize Contact.
        
        Args:
            id: Contact ID
            name: Contact name
            phone: Phone number
            email: Email (optional)
            address: Address (optional)
            group: Group (optional)
            notes: Notes (optional)
            avatar: Avatar URL (optional)
        """
        self.id = id or str(datetime.now().timestamp()).replace('.', '')
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.group = group
        self.notes = notes
        self.avatar = avatar
        self.phone_normalized = ''.join(c for c in phone if c.isdigit())
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert Contact to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "phone_normalized": self.phone_normalized,
            "email": self.email,
            "address": self.address,
            "group": self.group,
            "notes": self.notes,
            "avatar": self.avatar,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        """Create Contact from dictionary."""
        contact = cls(
            id=data.get('id'),
            name=data.get('name', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            address=data.get('address', ''),
            group=data.get('group', ''),
            notes=data.get('notes', ''),
            avatar=data.get('avatar', '')
        )
        contact.phone_normalized = data.get('phone_normalized', contact.phone_normalized)
        contact.created_at = data.get('created_at', contact.created_at)
        contact.updated_at = data.get('updated_at', contact.updated_at)
        return contact
    
    def update(self, **kwargs):
        """Update contact attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at']:
                setattr(self, key, value)
        
        # Update phone_normalized if phone changed
        if 'phone' in kwargs:
            self.phone_normalized = ''.join(c for c in self.phone if c.isdigit())
        
        self.updated_at = datetime.now().isoformat()
    
    def __repr__(self):
        return f"Contact(id={self.id}, name={self.name}, phone={self.phone})"
    
    def __str__(self):
        return f"{self.name} - {self.phone}"
