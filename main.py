import os
from datetime import datetime
from database import JSONDatabase
from models import Product, Category, Order, RecentView
from services import ProductCacheService, OrderQueueService, RecentViewManager, CategoryTreeService

class Store:
    def __init__(self):
        self.name = "Nadie se salva solo"
        self.database = JSONDatabase()
        self.product_cache = ProductCacheService(self.database)
        self.order_queue = OrderQueueService(self.database)
        self.recent_view_manager = RecentViewManager(self.database)
        self.category_tree = CategoryTreeService(self.database)
    
    def show_current_status(self):
        print("\n" + "="*50)
        print("CURRENT STORE STATUS")
        print("="*50)
        
        products = [Product.from_dict(p) for p in self.database.products]
        print(f"\nPRODUCTS ({len(products)}):")
        for product in products:
            category_name = "No category"
            if product.category_id:
                category_data = next((c for c in self.database.categories if c['id'] == product.category_id), None)
                if category_data:
                    category_name = category_data['name']
            print(f"  {product.code}: {product.name} | ${product.price} | Stock: {product.stock} | {category_name}")
        
        orders = [Order.from_dict(o) for o in self.database.orders]
        orders.sort(key=lambda x: x.created_at)
        print(f"\nORDERS ({len(orders)}):")
        for order in orders:
            created_date = datetime.fromisoformat(order.created_at).strftime('%d/%m %H:%M')
            print(f"  {order.id}: {order.customer_name} | {order.status} | {created_date}")
        
        categories = [Category.from_dict(c) for c in self.database.categories]
        print(f"\nCATEGORIES ({len(categories)}):")
        for category in categories:
            parent_name = "Root"
            if category.parent_id:
                parent_data = next((c for c in self.database.categories if c['id'] == category.parent_id), None)
                if parent_data:
                    parent_name = parent_data['name']
            print(f"  {category.name} (Parent: {parent_name})")
        
        histories = [RecentView.from_dict(rv) for rv in self.database.recent_views]
        print(f"\nVIEW HISTORIES ({len(histories)}):")
        for history in histories:
            print(f"  {history.identifier}: {history.stack}")
    
    def view_all_orders(self):
        print("\n--- ORDER HISTORY ---")
        
        print("\nOptions:")
        print("1. View all orders")
        print("2. View pending orders")
        print("3. View completed orders")
        print("4. View cancelled orders")
        print("5. View orders by customer")
        print("6. Back to order menu")
        
        option = input("\nSelect option (1-6): ").strip()
        
        if option == "6":
            return
        
        orders_data = self.database.orders
        
        if option == "1":
            orders = [Order.from_dict(o) for o in orders_data]
            orders.sort(key=lambda x: x.created_at, reverse=True)
            status_filter = "ALL"
        elif option == "2":
            orders = [Order.from_dict(o) for o in orders_data if o['status'] == 'PENDING']
            orders.sort(key=lambda x: x.created_at)
            status_filter = "PENDING"
        elif option == "3":
            orders = [Order.from_dict(o) for o in orders_data if o['status'] == 'DONE']
            orders.sort(key=lambda x: x.created_at, reverse=True)
            status_filter = "COMPLETED"
        elif option == "4":
            orders = [Order.from_dict(o) for o in orders_data if o['status'] == 'CANCELLED']
            orders.sort(key=lambda x: x.created_at, reverse=True)
            status_filter = "CANCELLED"
        elif option == "5":
            customer_name = input("Enter customer name: ").strip()
            orders = [Order.from_dict(o) for o in orders_data if customer_name.lower() in o['customer_name'].lower()]
            orders.sort(key=lambda x: x.created_at, reverse=True)
            status_filter = f"FOR CUSTOMER: {customer_name}"
        else:
            print("Invalid option")
            return
        
        print(f"\n{status_filter} ORDERS ({len(orders)}):")
        print("-" * 80)
        
        if not orders:
            print("No orders found")
            return
        
        for order in orders:
            print(f"\nOrder ID: {order.id}")
            print(f"Customer: {order.customer_name}")
            print(f"Status: {order.status}")
            print(f"Created: {datetime.fromisoformat(order.created_at).strftime('%Y-%m-%d %H:%M:%S')}")
            print("Items:")
            
            total_amount = 0
            for item in order.items:
                product_code = item['code']
                quantity = item.get('qty', 1)
                product = self.product_cache.get_product(product_code)
                
                if product:
                    product_name = product.name
                    price = product.price
                    subtotal = price * quantity
                    total_amount += subtotal
                    print(f"  - {quantity}x {product_name} @ ${price:.2f} = ${subtotal:.2f}")
                else:
                    print(f"  - {quantity}x {product_code} (Product not found)")
            
            print(f"Total: ${total_amount:.2f}")
            print("-" * 80)
    
    def delete_product(self):
        print("\n--- DELETE PRODUCT ---")
        code = input("Product code to delete: ").strip()
        
        if code:
            product_data = next((p for p in self.database.products if p['code'] == code), None)
            if product_data:
                product = Product.from_dict(product_data)
                print(f"Delete '{product.name}' (Code: {product.code})?")
                confirm = input("Type 'YES' to confirm: ").strip().upper()
                
                if confirm == 'YES':
                    self.product_cache.remove_product(code)
                    self.database.delete_product(code)
                    print(f"Product '{product.name}' deleted")
                else:
                    print("Deletion cancelled")
            else:
                print(f"Product '{code}' not found")
    
    def update_product_complete(self):
        print("\n--- UPDATE PRODUCT ---")
        code = input("Product code to update: ").strip()
        
        if code:
            product_data = next((p for p in self.database.products if p['code'] == code), None)
            if not product_data:
                print(f"Product '{code}' not found")
                return
            
            product = Product.from_dict(product_data)
            print(f"Current: {product.name} | ${product.price} | Stock: {product.stock}")
            
            print("\nLeave blank to keep current value:")
            new_name = input(f"New name [{product.name}]: ").strip()
            new_price = input(f"New price [{product.price}]: ").strip()
            new_stock = input(f"New stock [{product.stock}]: ").strip()
            new_desc = input(f"New description [{product.description}]: ").strip()
            
            if new_name:
                product.name = new_name
            if new_price:
                product.price = float(new_price)
            if new_stock:
                product.stock = int(new_stock)
            if new_desc:
                product.description = new_desc
            
            self.database.update_product(product.to_dict())
            self.product_cache.update_product(product)
            print("Product updated")
    
    def search_products_by_name(self):
        print("\n--- SEARCH PRODUCTS BY NAME ---")
        name_query = input("Enter product name (partial match): ").strip()
        
        if not name_query:
            print("Search query cannot be empty")
            return
        
        products = [Product.from_dict(p) for p in self.database.products 
                   if name_query.lower() in p['name'].lower()]
        
        if products:
            print(f"\nFound {len(products)} product(s):")
            for i, product in enumerate(products, 1):
                category_name = "No category"
                if product.category_id:
                    category_data = next((c for c in self.database.categories if c['id'] == product.category_id), None)
                    if category_data:
                        category_name = category_data['name']
                print(f"{i:2d}. {product.name} (Code: {product.code}) - ${product.price} - Stock: {product.stock} - {category_name}")
        else:
            print("No products found matching your search")
    
    def manage_products_complete(self):
        print("\n--- PRODUCT MANAGEMENT ---")
        
        while True:
            print("\nOptions:")
            print("1. View all products")
            print("2. Search product by code")
            print("3. Search product by name")
            print("4. Create new product")
            print("5. Update product information")
            print("6. Update stock only")
            print("7. Delete product")
            print("8. Return to main menu")
            
            option = input("\nSelect option (1-8): ").strip()
            
            if option == "1":
                products = [Product.from_dict(p) for p in self.database.products]
                print(f"\nProducts found: {len(products)}")
                for product in products:
                    category_name = "No category"
                    if product.category_id:
                        category_data = next((c for c in self.database.categories if c['id'] == product.category_id), None)
                        if category_data:
                            category_name = category_data['name']
                    print(f"  [{product.code}] {product.name} | ${product.price} | Stock: {product.stock} | {category_name}")
                    
            elif option == "2":
                code = input("Enter product code: ").strip()
                if code:
                    self.product_cache.initialize_cache()
                    product = self.product_cache.get_product(code)
                    
                    if product:
                        print(f"Found: {product.name} | Stock: {product.stock}")
                    else:
                        print(f"Product '{code}' not found")
            
            elif option == "3":
                self.search_products_by_name()
            
            elif option == "4":
                print("\nCreate new product:")
                code = input("Code: ").strip()
                name = input("Name: ").strip()
                price = input("Price: ").strip()
                stock = input("Stock: ").strip()
                
                if code and name and price and stock:
                    try:
                        # Check if code already exists
                        existing_product = next((p for p in self.database.products if p['code'] == code), None)
                        if existing_product:
                            print(f"Product with code '{code}' already exists")
                            continue
                            
                        # Show available categories
                        categories = [Category.from_dict(c) for c in self.database.categories]
                        if categories:
                            print("\nAvailable categories:")
                            for i, cat in enumerate(categories, 1):
                                print(f"  {cat.id}. {cat.get_full_path(categories)}")
                            
                            cat_choice = input("\nCategory ID (leave empty for no category): ").strip()
                            category_id = None
                            if cat_choice and cat_choice.isdigit():
                                category_id = int(cat_choice)
                                selected_cat = next((c for c in categories if c.id == category_id), None)
                                if selected_cat:
                                    print(f"Selected category: {selected_cat.get_full_path(categories)}")
                                else:
                                    print("Invalid category ID")
                        else:
                            print("No categories available")
                        
                        product = Product(
                            code=code,
                            name=name,
                            price=float(price),
                            stock=int(stock),
                            category_id=category_id
                        )
                        self.database.add_product(product.to_dict())
                        self.product_cache.update_product(product)
                        print(f"Product '{name}' created")
                    except Exception as error:
                        print(f"Error: {error}")
            
            elif option == "5":
                self.update_product_complete()
            
            elif option == "6":
                code = input("Product code: ").strip()
                new_stock = input("New stock: ").strip()
                
                if code and new_stock:
                    try:
                        product_data = next((p for p in self.database.products if p['code'] == code), None)
                        if product_data:
                            product = Product.from_dict(product_data)
                            product.stock = int(new_stock)
                            self.database.update_product(product.to_dict())
                            self.product_cache.update_product(product)
                            print(f"Stock updated to {new_stock}")
                        else:
                            print("Product not found")
                    except ValueError:
                        print("Invalid stock value")
            
            elif option == "7":
                self.delete_product()
            
            elif option == "8":
                break
            else:
                print("Invalid option")

    def create_category(self):
        """Crear nueva categoría"""
        print("\n--- CREATE CATEGORY ---")
        name = input("Category name: ").strip()
        
        if not name:
            print("Category name cannot be empty")
            return
        
        # Mostrar categorías disponibles para selección de padre
        categories = self.list_all_categories_for_selection()
        
        parent_id = input("\nParent category ID (leave empty for root): ").strip()
        parent_id = int(parent_id) if parent_id.isdigit() else None
        
        if parent_id:
            parent_exists = any(cat['id'] == parent_id for cat in self.database.categories)
            if not parent_exists:
                print("Invalid parent category ID")
                return
        
        try:
            category_id = self.database.get_next_category_id()
            category = Category(category_id, name, parent_id)
            self.database.add_category(category.to_dict())
            print(f"Category '{name}' created successfully")
            
            # Invalidar caché de categorías
            self.category_tree.invalidate_cache()
            
        except Exception as error:
            print(f"Error creating category: {error}")

    def list_all_categories_for_selection(self):
        """Listar todas las categorías con sus rutas completas para selección"""
        categories = [Category.from_dict(c) for c in self.database.categories]
        if not categories:
            print("No categories available")
            return []
        
        print("\nAvailable categories:")
        for category in categories:
            print(f"  {category.id}. {category.get_full_path(categories)}")
        
        return categories

    def show_category_tree(self):
        """Mostrar árbol completo de categorías"""
        print("\n--- CATEGORY TREE ---")
        
        categories = [Category.from_dict(c) for c in self.database.categories]
        root_categories = [cat for cat in categories if not cat.parent_id]
        
        if not root_categories:
            print("No categories created")
            return
        
        def print_tree(category, level=0, is_last=True):
            indent = "    " * level
            connector = "└── " if is_last else "├── "
            
            # Contar productos directos en esta categoría
            direct_count = len([p for p in self.database.products if p.get('category_id') == category.id])
            
            print(f"{indent}{connector}{category.name} ({direct_count} products)")
            
            # Mostrar productos directos
            direct_products = [Product.from_dict(p) for p in self.database.products 
                            if p.get('category_id') == category.id]
            for product in direct_products:
                print(f"{indent}    {product.name} (${product.price})")
            
            # Subcategorías
            children = [cat for cat in categories if cat.parent_id == category.id]
            children.sort(key=lambda x: x.name)
            total_children = len(children)
            for index, child in enumerate(children):
                is_last_child = (index == total_children - 1)
                print_tree(child, level + 1, is_last_child)
        
        for index, root_cat in enumerate(root_categories):
            is_last = (index == len(root_categories) - 1)
            print_tree(root_cat, 0, is_last)

    def browse_categories_hierarchical(self):
        """Navegar categorías jerárquicamente"""
        current_category_id = None
        
        while True:
            print("\n--- BROWSE CATEGORIES ---")
            
            categories = [Category.from_dict(c) for c in self.database.categories]
            
            if current_category_id:
                current_category = next((cat for cat in categories if cat.id == current_category_id), None)
                if current_category:
                    print(f"Current: {current_category.get_full_path(categories)}")
                else:
                    current_category_id = None
            
            # Obtener subcategorías
            if current_category_id:
                subcategories = [cat for cat in categories if cat.parent_id == current_category_id]
            else:
                subcategories = [cat for cat in categories if not cat.parent_id]
            
            # Obtener productos en esta categoría
            if current_category_id:
                products = [Product.from_dict(p) for p in self.database.products 
                        if p.get('category_id') == current_category_id]
            else:
                products = []
            
            if subcategories:
                print("\nSubcategories:")
                for i, category in enumerate(subcategories, 1):
                    product_count = len([p for p in self.database.products if p.get('category_id') == category.id])
                    print(f"{i:2d}. {category.name} ({product_count} products)")
            
            if products:
                print(f"\nProducts in this category ({len(products)}):")
                for i, product in enumerate(products, 1):
                    print(f"    {i:2d}. {product.name} (${product.price}) - Stock: {product.stock}")
            
            print("\nOptions:")
            if subcategories:
                print("Enter number to navigate to subcategory")
            if current_category_id:
                print("U - Go up one level")
            print("H - Go to root")
            print("B - Back to category menu")
            
            option = input("\nSelect option: ").strip().lower()
            
            if option == 'b':
                break
            elif option == 'h':
                current_category_id = None
            elif option == 'u' and current_category_id:
                current_category = next((cat for cat in categories if cat.id == current_category_id), None)
                if current_category and current_category.parent_id:
                    current_category_id = current_category.parent_id
                else:
                    current_category_id = None
            elif option.isdigit():
                num = int(option)
                if 1 <= num <= len(subcategories):
                    selected_category = subcategories[num - 1]
                    current_category_id = selected_category.id
                else:
                    print("Invalid category number")
            else:
                print("Invalid option")

    def search_products_by_category(self):
        """Buscar productos por categoría incluyendo subcategorías"""
        print("\n--- SEARCH BY CATEGORY ---")
        
        categories = [Category.from_dict(c) for c in self.database.categories]
        if not categories:
            print("No categories created")
            return
        
        print("Available categories:")
        for cat in categories:
            print(f"  {cat.id}. {cat.get_full_path(categories)}")
        
        try:
            category_id = int(input("\nCategory ID: ").strip())
            category = next((cat for cat in categories if cat.id == category_id), None)
            if not category:
                print("Invalid category ID")
                return
            
            all_categories = self.category_tree.get_subtree_categories(category_id)
            
            print(f"\nSearching in: {category.get_full_path(categories)}")
            print(f"Subcategories included: {len(all_categories)}")
            
            products = self.category_tree.get_products_in_subtree(category_id)
            
            print(f"\nProducts found: {len(products)}")
            for product in products:
                product_path = "No category"
                if product.category_id:
                    cat = next((c for c in categories if c.id == product.category_id), None)
                    if cat:
                        product_path = cat.get_full_path(categories)
                print(f"  {product.name}")
                print(f"    Category: {product_path}")
                print(f"    ${product.price} | Stock: {product.stock}")
                print()
                
        except (ValueError, Exception) as e:
            print("Invalid category ID")

    def delete_category(self):
        """Eliminar categoría - las subcategorías suben un nivel"""
        print("\n--- DELETE CATEGORY ---")
        
        categories = self.list_all_categories_for_selection()
        if not categories:
            return
        
        try:
            category_id = input("\nCategory ID to delete: ").strip()
            if not category_id:
                print("Operation cancelled")
                return
            
            category_id = int(category_id)
            category_data = next((c for c in self.database.categories if c['id'] == category_id), None)
            if not category_data:
                print("Invalid category ID")
                return
            
            category = Category.from_dict(category_data)
            all_categories = [Category.from_dict(c) for c in self.database.categories]
            
            # Obtener información completa
            all_subcategories = self.category_tree.get_subtree_categories(category.id)
            all_products = self.category_tree.get_products_in_subtree(category.id)
            direct_products = [Product.from_dict(p) for p in self.database.products 
                            if p.get('category_id') == category.id]
            direct_subcategories = [cat for cat in all_categories if cat.parent_id == category.id]
            
            print(f"\nCATEGORY TO DELETE: {category.get_full_path(all_categories)}")
            print(f"Direct subcategories: {len(direct_subcategories)}")
            print(f"Total subcategories in tree: {len(all_subcategories)}")
            print(f"Direct products: {len(direct_products)}")
            print(f"Total products in tree: {len(all_products)}")
            
            # Mostrar lo que pasará
            print(f"\n WARNING: This action will:")
            print(f"   • DELETE the category '{category.name}'")
            
            if direct_products:
                print(f"   • Move {len(direct_products)} direct products to 'No category'")
            
            if direct_subcategories:
                print(f"   • Move {len(direct_subcategories)} subcategories up one level:")
                for subcat in direct_subcategories:
                    new_parent = "ROOT"
                    if category.parent_id:
                        parent_cat = next((c for c in all_categories if c.id == category.parent_id), None)
                        if parent_cat:
                            new_parent = parent_cat.get_full_path(all_categories)
                    print(f"     - {subcat.name} -> {new_parent}")
            
            print(f"   • This action CANNOT be undone!")
            
            confirm = input("\nType 'DELETE' to confirm: ").strip().upper()
            if confirm == 'DELETE':
                # Mover productos directos a sin categoría
                moved_products_count = 0
                for product in direct_products:
                    product.category_id = None
                    self.database.update_product(product.to_dict())
                    moved_products_count += 1
                
                # Mover subcategorías un nivel arriba
                moved_subcategories_count = 0
                for subcat in direct_subcategories:
                    subcat.parent_id = category.parent_id
                    self.database.update_category(subcat.to_dict())
                    moved_subcategories_count += 1
                
                # Eliminar la categoría
                category_name = category.name
                self.database.delete_category(category.id)
                
                # Invalidar caché
                self.category_tree.invalidate_cache()
                
                print(f"\n Category '{category_name}' deleted successfully")
                
                if moved_products_count > 0:
                    print(f"   {moved_products_count} products moved to 'No category'")
                
                if moved_subcategories_count > 0:
                    print(f"   {moved_subcategories_count} subcategories moved up one level")
                    
                # Mostrar nueva estructura si había subcategorías
                if moved_subcategories_count > 0:
                    print(f"\nNew structure:")
                    for subcat in direct_subcategories:
                        new_path = subcat.get_full_path([cat for cat in all_categories if cat.id != category.id])
                        print(f"   - {new_path}")
                
            else:
                print("Deletion cancelled")
                    
        except (ValueError, Exception) as error:
            print(f"Error deleting category: {error}")

    def manage_categories_complete(self):
        """Gestión completa de categorías"""
        print("\n--- CATEGORY MANAGEMENT ---")
        
        while True:
            print("\nOptions:")
            print("1. View category tree")
            print("2. Browse categories hierarchically")
            print("3. Search products by category")
            print("4. Create new category")
            print("5. Delete category")
            print("6. Return to main menu")
            
            option = input("\nSelect option (1-6): ").strip()
            
            if option == "1":
                self.show_category_tree()
            
            elif option == "2":
                self.browse_categories_hierarchical()
            
            elif option == "3":
                self.search_products_by_category()
            
            elif option == "4":
                self.create_category()
            
            elif option == "5":
                self.delete_category()
            
            elif option == "6":
                break
            
            else:
                print("Invalid option")

    def process_real_orders(self):
        """Procesamiento de pedidos con historial incluido"""
        print("\n--- ORDER PROCESSING ---")
        
        while True:
            pending_orders = [Order.from_dict(o) for o in self.database.orders if o['status'] == 'PENDING']
            pending_orders.sort(key=lambda x: x.created_at)
            print(f"\nPending orders: {len(pending_orders)}")
            
            if pending_orders:
                for order in pending_orders:
                    created_time = datetime.fromisoformat(order.created_at).strftime('%H:%M:%S')
                    print(f"  {order.id}: {order.customer_name} | Items: {len(order.items)} | {created_time}")
            
            print("\nOptions:")
            print("1. Process next order (FIFO)")
            print("2. Process all pending orders")
            print("3. Create new order")
            print("4. View order details")
            print("5. View order history")
            print("6. Return to main menu")
            
            option = input("\nSelect option (1-6): ").strip()
            
            if option == "1":
                self.order_queue.load_pending_orders()
                order_id = self.order_queue.process_next_order(self.product_cache)
                if order_id:
                    print(f"Order {order_id} processed")
                else:
                    print("No orders to process")
                    
            elif option == "2":
                self.order_queue.load_pending_orders()
                processed_count = 0
                while True:
                    order_id = self.order_queue.process_next_order(self.product_cache)
                    if order_id:
                        print(f"Order {order_id} processed")
                        processed_count += 1
                    else:
                        break
                print(f"{processed_count} orders processed")
                
            elif option == "3":
                self.create_order_interactive()
            
            elif option == "4":
                self.view_order_details()
            
            elif option == "5":
                self.view_all_orders()
            
            elif option == "6":
                break
            
            else:
                print("Invalid option")

    def view_order_details(self):
        """Ver detalles de pedido específico"""
        print("\n--- VIEW ORDER DETAILS ---")
        order_id = input("Enter order ID: ").strip()
        
        if not order_id:
            print("Order ID cannot be empty")
            return
        
        try:
            order_id = int(order_id)
            order_data = next((o for o in self.database.orders if o['id'] == order_id), None)
            if not order_data:
                print("Invalid order ID")
                return
            
            order = Order.from_dict(order_data)
            print(f"\nOrder {order.id}:")
            print(f"Customer: {order.customer_name}")
            print(f"Status: {order.status}")
            print(f"Created: {datetime.fromisoformat(order.created_at).strftime('%Y-%m-%d %H:%M:%S')}")
            print("Items:")
            
            total = 0
            for item in order.items:
                product = self.product_cache.get_product(item['code'])
                product_name = product.name if product else item['code']
                quantity = item.get('qty', 1)
                price = product.price if product else 0
                subtotal = price * quantity
                total += subtotal
                print(f"  - {quantity}x {product_name} @ ${price:.2f} = ${subtotal:.2f}")
            
            print(f"Total: ${total:.2f}")
            
        except (ValueError, Exception):
            print("Invalid order ID")

    def manage_user_search_history(self):
        """Gestión del historial de búsqueda de usuarios"""
        print("\n--- USER SEARCH HISTORY ---")
        
        histories = [RecentView.from_dict(rv) for rv in self.database.recent_views]
        
        if histories:
            print("Existing user histories:")
            for history in histories:
                products = []
                for code in history.stack:
                    product = self.product_cache.get_product(code)
                    if product:
                        products.append(product.name)
                    else:
                        products.append(f"{code} (not found)")
                print(f"  {history.identifier}: {', '.join(products)}")
        else:
            print("No user histories registered")
        
        while True:
            print("\nOptions:")
            print("1. Simulate product view by user")
            print("2. View user history")
            print("3. Clear user history")
            print("4. Return to main menu")
            
            option = input("\nSelect option (1-4): ").strip()
            
            if option == "1":
                user_id = input("User/session identifier: ").strip()
                code = input("Product code viewed: ").strip()
                
                if user_id and code:
                    product = self.product_cache.get_product(code)
                    if product:
                        self.recent_view_manager.add_to_recent_view(user_id, code)
                        current_stack = self.recent_view_manager.get_recent_views(user_id)
                        print(f"'{product.name}' added to user history")
                        print(f"Current history: {current_stack}")
                    else:
                        print(f"Product '{code}' does not exist")
            
            elif option == "2":
                user_id = input("User identifier to query: ").strip()
                if user_id:
                    history_data = self.database.get_recent_view(user_id)
                    if history_data:
                        history = RecentView.from_dict(history_data)
                        products = []
                        for code in history.stack:
                            product = self.product_cache.get_product(code)
                            if product:
                                products.append(f"{product.name} ({code})")
                            else:
                                products.append(f"{code} (deleted)")
                        print(f"History for user {user_id}: {', '.join(products)}")
                    else:
                        print(f"No history for user {user_id}")
            
            elif option == "3":
                user_id = input("User identifier to clear: ").strip()
                if user_id:
                    history_data = self.database.get_recent_view(user_id)
                    if history_data:
                        history = RecentView.from_dict(history_data)
                        history.stack = []
                        self.database.update_recent_view(history.to_dict())
                        print(f"History cleared for user {user_id}")
                    else:
                        print(f"No history for user {user_id}")
            
            elif option == "4":
                break
            
            else:
                print("Invalid option")

    def initialize_system(self):
        print("Initializing Store System...")
        
        self.product_cache.initialize_cache()
        cache_stats = self.product_cache.get_cache_stats()
        print(f"Product Cache: {cache_stats['cached_products']} products loaded")
        
        self.order_queue.load_pending_orders()
        queue_size = self.order_queue.get_queue_size()
        print(f"Order Queue: {queue_size} pending orders loaded")
        
        print("All services initialized successfully")

    def run(self):
        print(f"\n{self.name} - STORE MANAGEMENT SYSTEM")
        
        self.initialize_system()
        
        while True:
            print("\n" + "="*40)
            print("MAIN MENU")
            print("="*40)
            print("1. Product Management")
            print("2. Order Processing") 
            print("3. User Search History")
            print("4. Categories")
            print("5. Current Status")
            print("6. Exit")
            print("="*40)
            
            option = input("\nSelect option (1-6): ").strip()
            
            if option == "1":
                self.manage_products_complete()
            elif option == "2":
                self.process_real_orders()
            elif option == "3":
                self.manage_user_search_history()
            elif option == "4":
                self.manage_categories_complete()
            elif option == "5":
                self.show_current_status()
            elif option == "6":
                print(f"\nThank you for using {self.name} system")
                break
            else:
                print("Invalid option")

def main():
    store = Store()
    store.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    except Exception as error:
        print(f"\nError: {error}")