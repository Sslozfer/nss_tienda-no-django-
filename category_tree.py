from models import Category, Product

class CategoryTreeService:
    def __init__(self, database):
        self.database = database
        self._cache = {}
    
    def get_subtree_categories(self, category_id):
        if category_id in self._cache:
            return self._cache[category_id].copy()
        
        categories_dict = {cat['id']: Category.from_dict(cat) for cat in self.database.categories}
        
        def build_tree(node_id):
            node = categories_dict.get(node_id)
            if not node:
                return []
            
            subtree = [node]
            children = [cat for cat in categories_dict.values() if cat.parent_id == node_id]
            for child in children:
                subtree.extend(build_tree(child.id))
            return subtree
        
        result = build_tree(category_id)
        self._cache[category_id] = result.copy()
        return result
    
    def get_products_in_subtree(self, category_id):
        categories = self.get_subtree_categories(category_id)
        category_ids = [cat.id for cat in categories]
        
        products = []
        for product_data in self.database.products:
            if product_data.get('category_id') in category_ids:
                products.append(Product.from_dict(product_data))
        return products
    
    def get_category_hierarchy(self, category_id=None):
        categories_dict = {cat['id']: Category.from_dict(cat) for cat in self.database.categories}
        
        def build_node(cat_id):
            category = categories_dict.get(cat_id)
            if not category:
                return {}
            
            node = {
                'id': category.id,
                'name': category.name,
                'product_count': len([p for p in self.database.products if p.get('category_id') == cat_id]),
                'children': {}
            }
            
            children = [cat for cat in categories_dict.values() if cat.parent_id == cat_id]
            for child in children:
                node['children'][child.name] = build_node(child.id)
            
            return node
        
        if category_id is None:
            root_categories = [cat for cat in categories_dict.values() if not cat.parent_id]
            hierarchy = {}
            for root in root_categories:
                hierarchy[root.name] = build_node(root.id)
            return hierarchy
        else:
            return build_node(category_id)
    
    def invalidate_cache(self, category_id=None):
        if category_id:
            keys_to_remove = [key for key in self._cache.keys() if key == category_id]
            for key in keys_to_remove:
                self._cache.pop(key, None)
        else:
            self._cache.clear()