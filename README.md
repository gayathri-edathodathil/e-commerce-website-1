# Goru E-Commerce Application

An e-commerce platform built with **Django**, **PostgreSQL**, and **Django REST Framework (DRF)**. The project features a complete shopping flow—from product browsing and cart management to order processing, inventory tracking, order history, and an administrative order management dashboard—along with a RESTful API.

---

## Key Features

### 1. Storefront & Product Browsing
- **Curated Catalog**: Dynamic categories, product listings, and single product detail views.
- **Search & Filtering**: Search products by keyword and filter by category.
- **Cart Management**: Add items, update quantities, remove items, and track order totals in real time.

### 2. Complete Order Processing Workflow
- **Checkout**: Contact & shipping detail form with automatic pre-fill for logged-in users.
- **Simulated Payment**: Marks orders as **Confirmed** upon checkout completion without requiring live payment gateways.
- **Stock & Inventory Validation**:
  - Validates item availability against inventory stock before order placement.
  - Automatically decrements stock quantities in an **atomic transaction**.
  - Marks products as unavailable when stock reaches 0.
- **Unique Order Tracking**: Automatically generates unique order tracking numbers (format: `ORD-YYYYMMDD-XXXXXX`).
- **Order History & Detail Views**: Registered users can view their past orders, track live status updates, and review itemized order summaries.

### 3. Administrative Order Management
- **Django Admin Integration**: View, search, filter, and edit customer orders.
- **Inline Order Items**: Review itemized contents directly within each order record.
- **Status Lifecycle Management**: Update order statuses (e.g. `Pending`, `Confirmed`, `Shipped`, `Delivered`, `Cancelled`).

### 4. RESTful API (`/api/`)
- Fully exposed Django REST Framework endpoints powering third-party/mobile clients.
- Serializers, ViewSets, and Router configuration for Categories, Products, Cart, and Orders.

---

## Technology Stack

- **Backend Framework**: Django 4.x
- **Database Engine**: PostgreSQL
- **API Framework**: Django REST Framework (DRF)
- **Frontend / Styling**: HTML5, Vanilla CSS / Custom Goru Theme, JavaScript, Bootstrap 4
- **Testing Framework**: Django Test Suite (`django.test.TestCase`, `rest_framework.test.APITestCase`)

---

## Directory Structure

```
e-commerce-website-1/
├── Goru/                   # Django Project Settings & Routing
│   ├── settings.py         # App configs, Database settings, DRF config
│   ├── urls.py             # Root URL routing (Includes /api/)
│   └── wsgi.py
├── home/                   # Core E-Commerce App
│   ├── models.py           # Category & Product models (with stock management)
│   ├── views.py            # Home, Catalog, Product Detail, Search views
│   └── urls.py
├── user/                   # User Accounts, Cart & Order Logic
│   ├── models.py           # User Profile, Cart, Order, and OrderItem models
│   ├── views.py            # Auth, Cart, Checkout, Order Confirmation/History/Detail
│   ├── admin.py            # Custom Admin panel for Orders & OrderItems
│   └── urls.py
├── api/                    # Django REST Framework API App
│   ├── serializers.py      # DRF Serializers for Category, Product, Cart, Order
│   ├── views.py            # API ViewSets (Filtering, Search, Order Placement)
│   ├── urls.py             # API Router (/api/categories/, /api/products/, etc.)
│   └── tests.py            # Comprehensive Automated API Test Suite
├── templates/              # HTML Templates
│   ├── base.html           # Master layout template (with Account & Orders navigation)
│   ├── index.html          # Cleaned & modernized Home page hero section
│   ├── checkout.html       # Shipping details & checkout form
│   ├── order_confirmation.html # Order confirmation & tracking page
│   ├── order_history.html  # User order history table with status badges
│   └── order_detail.html   # Detailed order view
├── static/                 # Static Assets (CSS, JS, Images, Fonts)
├── manage.py               # Django CLI helper
└── README.md               # Project Documentation
```

---

## Setup & Installation Instructions

### 1. Prerequisites
- Python 3.10+
- PostgreSQL server installed and running on `localhost:5432`

### 2. Environment Setup
Clone the repository and set up a Python virtual environment:

```bash
# Navigate to project directory
cd e-commerce-website-1

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install django djangorestframework psycopg2-binary
```

### 3. Database Configuration
Ensure a PostgreSQL database exists and update settings in `Goru/settings.py` if necessary:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'goru',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Run Migrations & Create Superuser

```bash
# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create an administrative user
python manage.py createsuperuser
```

### 5. Start Local Server

```bash
python manage.py runserver
```

Access the application in your browser:
- **Web Front-end**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Dashboard**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **REST API Base**: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

---

## REST API Reference (`/api/`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/categories/` | List all product categories | No |
| `POST` | `/api/categories/` | Create category (Admin only) | Admin |
| `GET` | `/api/products/` | List all products (supports `?category=<id>` & `?search=<term>`) | No |
| `GET` | `/api/products/<id>/` | Product detail | No |
| `GET` | `/api/cart/` | View current user's active cart items | Yes |
| `POST` | `/api/cart/` | Add item to cart (`{ "product_id": 1, "quantity": 2 }`) | Yes |
| `DELETE` | `/api/cart/<id>/` | Remove item from cart | Yes |
| `GET` | `/api/orders/` | List current user's order history (Admin sees all) | Yes |
| `POST` | `/api/orders/` | Place order from active cart items | Yes |
| `GET` | `/api/orders/<id>/` | View order detail summary | Yes |
| `PATCH` | `/api/orders/<id>/` | Update order status (Admin only) | Admin |

---

## Running Automated Tests

Run the DRF API test suite to verify end-to-end functionality, stock deduction, and order placement rules:

```bash
python manage.py test api
```

Expected Output:
```text
Found 5 test(s).
System check identified no issues (0 silenced).
.....
----------------------------------------------------------------------
Ran 5 tests in 0.825s

OK
```
