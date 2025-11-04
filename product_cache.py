from models import Product

class ProductCacheService:
    def __init__(self, database):
        self.database = database
        self._cache = {}
        self._initialized = False
    
    def initialize_cache(self):
        if not self._initialized:
            for product_data in self.database.products:
                product = Product.from_dict(product_data)
                self._cache[product.code] = product
            self._initialized = True
    
    def get_product(self, code):
        product = self._cache.get(code)
        if product is not None:
            return product
        
        # Cache miss - search in database
        for product_data in self.database.products:
            if product_data['code'] == code:
                product = Product.from_dict(product_data)
                self._cache[code] = product
                return product
        return None
    
    def update_product(self, product):
        self._cache[product.code] = product
    
    def remove_product(self, code):
        self._cache.pop(code, None)
    
    def clear_cache(self):
        self._cache.clear()
        self._initialized = False
    
    def get_cache_stats(self):
        return {
            'cached_products': len(self._cache),
            'initialized': self._initialized
        }