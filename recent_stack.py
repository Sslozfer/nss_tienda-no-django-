from collections import OrderedDict
from models import RecentView
from datetime import datetime

class RecentViewStackService:
    def __init__(self, identifier, database, max_size=5):
        self.identifier = identifier
        self.database = database
        self.max_size = max_size
        
        recent_view_data = self.database.get_recent_view(identifier)
        if recent_view_data:
            self.recent_view = RecentView.from_dict(recent_view_data)
        else:
            self.recent_view = RecentView(identifier, [])
            self.database.add_recent_view(self.recent_view.to_dict())
        
        self._stack_dict = OrderedDict()
        for code in self.recent_view.stack:
            self._stack_dict[code] = None
    
    def add_product(self, product_code):
        if product_code in self._stack_dict:
            del self._stack_dict[product_code]
        
        self._stack_dict[product_code] = None
        
        while len(self._stack_dict) > self.max_size:
            self._stack_dict.popitem(last=False)
        
        self._save_to_db()
    
    def get_recent_products(self):
        return list(self._stack_dict.keys())
    
    def remove_product(self, product_code):
        if product_code in self._stack_dict:
            del self._stack_dict[product_code]
            self._save_to_db()
            return True
        return False
    
    def clear_stack(self):
        self._stack_dict.clear()
        self._save_to_db()
    
    def get_stack_size(self):
        return len(self._stack_dict)
    
    def _save_to_db(self):
        self.recent_view.stack = list(self._stack_dict.keys())
        self.recent_view.updated_at = datetime.now().isoformat()
        self.database.update_recent_view(self.recent_view.to_dict())

class RecentViewManager:
    def __init__(self, database):
        self.database = database
    
    def get_stack(self, identifier, max_size=5):
        return RecentViewStackService(identifier, self.database, max_size)
    
    def add_to_recent_view(self, identifier, product_code):
        stack = RecentViewStackService(identifier, self.database)
        stack.add_product(product_code)
    
    def get_recent_views(self, identifier):
        stack = RecentViewStackService(identifier, self.database)
        return stack.get_recent_products()