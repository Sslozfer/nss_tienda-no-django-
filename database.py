import os
import json

class JSONDatabase:
    def __init__(self, filename='store_data.json'):
        self.filename = filename
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f) or {}

            data.setdefault('categories', [])
            data.setdefault('products', [])
            data.setdefault('orders', [])
            data.setdefault('recent_views', [])
            data.setdefault('next_order_id', 1)
            data.setdefault('next_category_id', 1)

            try:
                if data.get('orders'):
                    max_id = max((o.get('id', 0) for o in data['orders']), default=0)
                    data['next_order_id'] = max(data.get('next_order_id', 1), max_id + 1)
            except Exception:
                pass

            try:
                if data.get('categories'):
                    max_cat = max((c.get('id', 0) for c in data['categories']), default=0)
                    data['next_category_id'] = max(data.get('next_category_id', 1), max_cat + 1)
            except Exception:
                pass

            return data
        else:
            return {
                'categories': [],
                'products': [],
                'orders': [],
                'recent_views': [],
                'next_order_id': 1,
                'next_category_id': 1
            }

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    @property
    def categories(self):
        return self.data['categories']

    @property
    def products(self):
        return self.data['products']

    @property
    def orders(self):
        return self.data['orders']

    @property
    def recent_views(self):
        return self.data['recent_views']

    def get_next_order_id(self):
        order_id = self.data.get('next_order_id', 1)
        self.data['next_order_id'] = order_id + 1
        self.save()
        return order_id

    def get_next_category_id(self):
        category_id = self.data.get('next_category_id', 1)
        self.data['next_category_id'] = category_id + 1
        self.save()
        return category_id

    def add_category(self, category_data):
        self.categories.append(category_data)
        self.save()

    def update_category(self, category_data):
        for i, cat in enumerate(self.categories):
            if cat.get('id') == category_data.get('id'):
                self.categories[i] = category_data
                self.save()
                return
        self.add_category(category_data)

    def delete_category(self, category_id):
        self.categories[:] = [cat for cat in self.categories if cat.get('id') != category_id]
        self.save()

    def add_product(self, product_data):
        self.products.append(product_data)
        self.save()

    def update_product(self, product_data):
        for i, prod in enumerate(self.products):
            if prod.get('code') == product_data.get('code'):
                self.products[i] = product_data
                self.save()
                return
        self.add_product(product_data)

    def delete_product(self, product_code):
        self.products[:] = [prod for prod in self.products if prod.get('code') != product_code]
        self.save()

    def add_order(self, order_data):
        self.orders.append(order_data)
        self.save()

    def update_order(self, order_data):
        for i, o in enumerate(self.orders):
            if o.get('id') == order_data.get('id'):
                self.orders[i] = order_data
                self.save()
                return
        self.add_order(order_data)

    def delete_order(self, order_id):
        self.orders[:] = [o for o in self.orders if o.get('id') != order_id]
        self.save()

    def get_recent_view(self, identifier):
        for rv in self.recent_views:
            if rv.get('identifier') == identifier:
                return rv
        return None

    def add_recent_view(self, recent_view_data):
        self.recent_views.append(recent_view_data)
        self.save()

    def update_recent_view(self, recent_view_data):
        for i, rv in enumerate(self.recent_views):
            if rv.get('identifier') == recent_view_data.get('identifier'):
                self.recent_views[i] = recent_view_data
                self.save()
                return
        self.add_recent_view(recent_view_data)