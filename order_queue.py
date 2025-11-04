from collections import deque
from models import Order, Product

class OrderQueueService:
    def __init__(self, database):
        self.database = database
        self._queue = deque()
        self._loaded = False
    
    def load_pending_orders(self):
        if not self._loaded:
            for order_data in self.database.orders:
                if order_data['status'] == 'PENDING':
                    self._queue.append(order_data['id'])
            self._loaded = True
    
    def add_order(self, order_id):
        self._queue.append(order_id)
    
    def process_next_order(self, product_cache):
        if not self._queue:
            return None
        
        order_id = self._queue.popleft()
        return self._process_single_order(order_id, product_cache)
    
    def _process_single_order(self, order_id, product_cache):
        order_data = next((o for o in self.database.orders if o['id'] == order_id), None)
        if not order_data:
            return None
        
        order = Order.from_dict(order_data)
        order.status = 'PROCESSING'
        self.database.update_order(order.to_dict())
        
        # Process each item in the order
        for item in order.items:
            product_code = item['code']
            quantity = item.get('qty', 1)
            
            product = product_cache.get_product(product_code)
            if not product:
                order.status = 'CANCELLED'
                self.database.update_order(order.to_dict())
                return order_id
            
            if product.stock < quantity:
                order.status = 'CANCELLED'
                self.database.update_order(order.to_dict())
                return order_id
            
            # Update stock
            product.stock -= quantity
            self.database.update_product(product.to_dict())
            product_cache.update_product(product)
        
        # Mark order as completed
        order.status = 'DONE'
        self.database.update_order(order.to_dict())
        return order_id
    
    def process_batch(self, batch_size, product_cache):
        processed = []
        for _ in range(min(batch_size, len(self._queue))):
            order_id = self.process_next_order(product_cache)
            if order_id:
                processed.append(order_id)
        return processed
    
    def get_queue_size(self):
        return len(self._queue)
    
    def clear_queue(self):
        self._queue.clear()
        self._loaded = False