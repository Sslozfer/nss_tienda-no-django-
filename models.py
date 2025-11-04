import json
import os
from datetime import datetime
from collections import OrderedDict

class Category:
    def __init__(self, id, name, parent_id=None):
        self.id = id
        self.name = name
        self.parent_id = parent_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id
        }
    
    @classmethod
    def from_dict(cls, data):
        category = cls(data['id'], data['name'], data.get('parent_id'))
        return category
    
    def get_full_path(self, categories):
        path = []
        current = self
        while current:
            path.append(current.name)
            if current.parent_id:
                current = next((c for c in categories if c.id == current.parent_id), None)
            else:
                current = None
        return ' -> '.join(reversed(path))

class Product:
    def __init__(self, code, name, description="", price=0.0, stock=0, category_id=None):
        self.code = code
        self.name = name
        self.description = description
        self.price = float(price)
        self.stock = int(stock)
        self.category_id = category_id
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category_id': self.category_id,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        product = cls(
            data['code'],
            data['name'],
            data.get('description', ''),
            data.get('price', 0.0),
            data.get('stock', 0),
            data.get('category_id')
        )
        product.created_at = data.get('created_at', datetime.now().isoformat())
        return product

class Order:
    def __init__(self, id, customer_name, items, status='PENDING'):
        self.id = id
        self.customer_name = customer_name
        self.items = items  # list of {'code': str, 'qty': int}
        self.status = status
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'items': self.items,
            'status': self.status,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        order = cls(
            data['id'],
            data['customer_name'],
            data['items'],
            data.get('status', 'PENDING')
        )
        order.created_at = data.get('created_at', datetime.now().isoformat())
        return order

class RecentView:
    def __init__(self, identifier, stack=None):
        self.identifier = identifier
        self.stack = stack or []
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'identifier': self.identifier,
            'stack': self.stack,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        recent_view = cls(data['identifier'], data.get('stack', []))
        recent_view.updated_at = data.get('updated_at', datetime.now().isoformat())
        return recent_view