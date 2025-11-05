from database import JSONDatabase
from models import Product, Category, Order, RecentView
import json
import os

def initialize_sample_data():
    """Initialize the database with sample data"""
    
    # Remove existing file if it exists
    if os.path.exists('store_data.json'):
        os.remove('store_data.json')
    
    database = JSONDatabase()
    
    categories = [
        Category(1, "Electrónicos"),
        Category(2, "Computadoras", 1),
        Category(3, "Smartphones", 1),
        Category(4, "Tablets", 1),
        Category(5, "Ropa"),
        Category(6, "Hombres", 5),
        Category(7, "Mujeres", 5),
        Category(8, "Hogar"),
        Category(9, "Muebles", 8),
        Category(10, "Electrodomésticos", 8)
    ]
    
    for category in categories:
        database.add_category(category.to_dict())

    products = [
        Product("LAP-001", "Laptop Gaming", "Laptop para gaming de alta gama", 1200.00, 15, 2),
        Product("LAP-002", "Laptop Oficina", "Laptop para trabajo y estudio", 800.00, 25, 2),
        Product("PHN-001", "iPhone 15", "Smartphone Apple última generación", 999.00, 30, 3),
        Product("PHN-002", "Samsung Galaxy", "Smartphone Android premium", 850.00, 20, 3),
        Product("TAB-001", "iPad Pro", "Tablet profesional Apple", 1100.00, 12, 4),
        Product("TAB-002", "Tablet Android", "Tablet Android versátil", 300.00, 18, 4),
        Product("CAM-001", "Camisa Casual", "Camisa de algodón para hombre", 45.00, 50, 6),
        Product("PAN-001", "Pantalón Jeans", "Jeans clásico para hombre", 60.00, 40, 6),
        Product("VES-001", "Vestido Verano", "Vestido ligero para mujer", 55.00, 35, 7),
        Product("SOF-001", "Sofá 3 Plazas", "Sofá moderno para sala", 450.00, 8, 9),
        Product("MES-001", "Mesa Centro", "Mesa de centro diseño moderno", 120.00, 15, 9),
        Product("REF-001", "Refrigerador", "Refrigerador eficiente energía", 700.00, 10, 10),
        Product("LAV-001", "Lavadora", "Lavadora automática 15kg", 550.00, 12, 10)
    ]
    
    for product in products:
        database.add_product(product.to_dict())
    
    orders = [
        Order(1, "Juan Pérez", [
            {"code": "PHN-001", "qty": 1},
            {"code": "TAB-002", "qty": 1}
        ], "DONE"),
        Order(2, "María García", [
            {"code": "LAP-001", "qty": 1},
            {"code": "CAM-001", "qty": 2}
        ], "PENDING"),
        Order(3, "Carlos López", [
            {"code": "REF-001", "qty": 1}
        ], "PENDING")
    ]
    
    for order in orders:
        database.add_order(order.to_dict())
    
    recent_views = [
        RecentView("user_juan", ["PHN-001", "TAB-002", "LAP-001"]),
        RecentView("user_maria", ["LAP-001", "CAM-001", "VES-001"]),
        RecentView("user_carlos", ["REF-001", "LAV-001", "SOF-001"])
    ]
    
    for recent_view in recent_views:
        database.add_recent_view(recent_view.to_dict())
    
    print("✅ Datos de ejemplo inicializados correctamente!")
    print(f"📦 {len(categories)} categorías creadas")
    print(f"📱 {len(products)} productos creados")
    print(f"📋 {len(orders)} pedidos creados")
    print(f"👀 {len(recent_views)} historiales de vista creados")

if __name__ == "__main__":
    initialize_sample_data()