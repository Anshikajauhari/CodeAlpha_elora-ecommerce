# ShopEase — Django E-commerce Starter

A basic full-stack e-commerce project using HTML, CSS, JavaScript, Django, and SQLite.

## Features
- Product catalogue and product detail pages
- Session-based shopping cart
- Django registration, login, and logout
- Checkout with delivery address and cash-on-delivery/demo payment
- Orders and order items stored in SQLite
- Django Admin for managing products and orders
- Responsive styling and quantity controls

## Requirements
- Python 3.10+
- pip

## Setup (Windows PowerShell)
```powershell
cd shopease
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py manage.py makemigrations shop
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```
Open http://127.0.0.1:8000/ for the store and http://127.0.0.1:8000/admin/ for the admin panel.

If PowerShell blocks activation, run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and use `.\.venv\Scripts\python.exe manage.py ...`.

## Add products
Log in to `/admin/`, open Products, and add a name, description, price, image URL (optional), and stock quantity. A few sample products are included automatically when the database has no products.

## Important notes
- Checkout is a demo/Cash on Delivery flow; it does not charge money.
- For a real deployment, add a payment provider, email verification, rate limiting, secure production settings, image uploads, shipping/tax rules, and tests.
- SQLite is fine for learning and local development. Consider PostgreSQL for production.
