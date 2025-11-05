# Tienda Online – “Nadie se Salva Solo”  
### Trabajo Práctico Final – Laboratorio de Algoritmos y Estructuras de Datos

Este proyecto implementa el backend de una tienda online basada en cómics. La tienda, llamada **“Nadie se Salva Solo”**, está ubicada en San Telmo y busca extender sus operaciones al ámbito digital. El sistema incluye gestión de productos, historial de vistas, pedidos y categorías utilizando estructuras de datos eficientes en Python.

**Interfaz:** El sistema funciona por consola (CLI).  
**Objetivo:** Desarrollar el motor lógico del sistema, sin interfaz gráfica.

---

## Estructuras de Datos Utilizadas

| Requerimiento | Estructura de Datos | Implementación | Justificación |
|---------------|---------------------|----------------|---------------|
| Gestión de productos (búsqueda eficiente) | Hash Table (`dict`) | `ProductCacheService` | Permite acceso O(1) al producto por código único |
| Procesamiento de pedidos | Queue (`collections.deque`) | `OrderQueueService` | Garantiza FIFO (First-In-First-Out) para pedidos |
| Historial de productos vistos (máx. 5) | Stack limitada (`OrderedDict`) | `RecentViewStackService` | Guarda últimos vistos, descarta los más antiguos |
| Categorización jerárquica de productos | Árbol recursivo | `CategoryTreeService` | Permite navegar subcategorías y resolver rutas |

---

## Diseño y Arquitectura del Sistema

Se optó por una arquitectura modular y aislada por responsabilidades, en donde cada módulo cumple una función concreta. La interacción con el sistema se realiza a través de la clase principal `Store`, disponible en `main.py`, que organiza los servicios, accede al almacenamiento y despliega un menú principal con las funcionalidades.

### Estructura del proyecto:

```

TIENDA
┣ main.py                # Punto de entrada con menú
┣ models.py              # Modelos: Product, Order, Category, RecentView
┣ database.py            # Persistencia en JSON: CRUD de datos
┣ product_cache.py       # Cache de productos con dict (hash)
┣ order_queue.py         # Cola principal de pedidos (FIFO)
┣ recent_stack.py        # Historial de productos recientes (máx. 5)
┣ category_tree.py       # Funciones sobre el árbol de categorías
┣ services.py            # Integrador de servicios (opcional)
┗ README.md              # Documentación

````

Cada módulo fue escrito bajo el principio de responsabilidad única (SRP).

---

## Funcionalidades Principales

### Gestión de productos:
- Crear, actualizar, eliminar y buscar productos por código o nombre
- Agrupar productos por categoría

### Procesamiento de pedidos:
- Agregar pedidos con productos
- Procesar pedidos en FIFO
- Control de stock al procesar

### Historial de productos vistos:
- Se guardan los últimos 5 productos vistos por usuario
- Si supera 5, se elimina el más antiguo

### Categorías con jerarquía:
- Crear categorías, asignarlas como hijas de otra
- Eliminar categoría (trasladando subcategorías o productos)
- Ver árbol completo o navegar jerárquicamente

---

## Ejecución del Proyecto

### Requisitos
- Python 3.10+
- No se requieren dependencias adicionales

### Pasos para ejecutar:

```bash
# Clonar el repositorio
git clone https://github.com/Sslozfer/nss_tienda-no-django-.git

# Ejecutar el sistema
python main.py
````

## Ejemplos de Uso Interactivo

### Crear un producto:

```
Select option (1-8):
4. Create new product
Code: SPID001
Name: The Amazing Spider-Man #1
Price: 4500
Stock: 12
Category ID: 4
Product 'The Amazing Spider-Man #1' created
```

### Procesar pedidos en cola:

```
Select option (1-6):
1. Process next order (FIFO)
Order 412 processed
```

### Ver historial de producto visto:

```
Select option (1-4):
2. View user history
User: lector123
History: Batman #1, Spider-Man #1, Joker #3, ...
```

---

## Decisiones de Diseño

### Persistencia:

* Se usa `store_data.json` con una clase `JSONDatabase` que centraliza toda la gestión de datos.
* JSON facilita lectura y escritura sin dependencias ni configuración adicional.

### Eficiencia:

* Se utilizó `dict` para cachear productos y minimizar IO del disco.
* `deque` soporta operaciones O(1) para encolar y desencolar pedidos.

### Modularidad del código:

* El sistema está pensado para ser extensible: si en el futuro se usa una base de datos real (como PostgreSQL), solo habría que reescribir `database.py`.

---

## 🧠 Bibliografía Consultada

* W3schools - dsa: [https://www.w3schools.com/dsa/](https://www.w3schools.com/dsa/)
* Python `collections` module: [https://docs.python.org/3/library/collections.html](https://docs.python.org/3/library/collections.html)
* Python `json` module: [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html)
* PEP8 - Guía de estilo de Python: [https://peps.python.org/pep-0008/](https://peps.python.org/pep-0008/)

---

## 👥 Autores del Proyecto

|     Integrantes    | 
| -------------------| 
| Franco Chichizola  | 
| Santiago Lozano    | 


Trabajo entregado el **04 de noviembre de 2024**.

---

> *Gracias por revisar nuestro proyecto. Esperamos que te guste y cumpla con todos los requisitos evaluativos.*
> 
> *Post data: mira monster.*

