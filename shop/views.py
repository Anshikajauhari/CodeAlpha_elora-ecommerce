from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Order, OrderItem

def _cart(request):
    return request.session.setdefault("cart", {})

def _cart_items(request):
    cart = request.session.get("cart", {})
    items, total, count = [], Decimal("0.00"), 0
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(pk=int(product_id))
            quantity = max(1, int(quantity))
        except (Product.DoesNotExist, ValueError, TypeError):
            continue
        line_total = product.price * quantity
        items.append({"product": product, "quantity": quantity, "line_total": line_total})
        total += line_total
        count += quantity
    return items, total, count

def home(request):
    products = Product.objects.all()
    if not products.exists():
        samples = [
            ("Peel Hydrating Serum", "A lightweight botanical serum for a fresh, dewy everyday glow.", "1299.00", 15, "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=900"),
            ("Daily Balance Cleanser", "A gentle daily cleanser inspired by plant-based skin rituals.", "899.00", 20, "https://images.unsplash.com/photo-1556229010-6c3f2c9ca5f8?w=900"),
            ("Nourishing Face Oil", "A comforting face oil for a simple evening self-care ritual.", "1499.00", 12, "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?w=900"),
        ]
        # The first three samples are reliable starter entries; products can also be added in admin.
        for name, desc, price, stock, image_url in samples[:3]:
            Product.objects.get_or_create(name=name, defaults={"description": desc, "price": price, "stock": stock, "image_url": image_url})
        products = Product.objects.all()
    _, _, cart_count = _cart_items(request)
    return render(request, "shop/home.html", {"products": products, "cart_count": cart_count})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    _, _, cart_count = _cart_items(request)
    return render(request, "shop/product_detail.html", {"product": product, "cart_count": cart_count})

def add_to_cart(request, product_id):
    if request.method != "POST":
        return redirect("home")
    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get("cart", {})
    current = int(cart.get(str(product_id), 0))
    if product.stock < 1:
        messages.error(request, "This product is currently out of stock.")
    elif current >= product.stock:
        messages.warning(request, "You have already added all available stock.")
    else:
        cart[str(product_id)] = current + 1
        request.session["cart"] = cart
        messages.success(request, f"{product.name} added to your cart.")
    return redirect(request.POST.get("next") or "cart")

def cart_view(request):
    items, total, cart_count = _cart_items(request)
    return render(request, "shop/cart.html", {"items": items, "total": total, "cart_count": cart_count})

def update_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, pk=product_id)
        try:
            quantity = int(request.POST.get("quantity", "1"))
        except ValueError:
            quantity = 1
        cart = request.session.get("cart", {})
        if quantity <= 0:
            cart.pop(str(product_id), None)
        elif quantity <= product.stock:
            cart[str(product_id)] = quantity
        else:
            messages.error(request, f"Only {product.stock} unit(s) are available.")
        request.session["cart"] = cart
    return redirect("cart")

def remove_from_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        cart.pop(str(product_id), None)
        request.session["cart"] = cart
    return redirect("cart")

@login_required
def checkout(request):
    items, total, cart_count = _cart_items(request)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("home")
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        address = request.POST.get("address", "").strip()
        phone = request.POST.get("phone", "").strip()
        if not full_name or not address or not phone:
            messages.error(request, "Please fill in all delivery details.")
        else:
            with transaction.atomic():
                # Recheck inventory and prices on the server before creating an order.
                fresh = []
                valid = True
                for item in items:
                    product = Product.objects.select_for_update().get(pk=item["product"].pk)
                    if item["quantity"] > product.stock:
                        valid = False
                        messages.error(request, f"Not enough stock for {product.name}. Please update your cart.")
                        break
                    fresh.append((product, item["quantity"]))
                if valid:
                    fresh_total = sum((p.price * q for p, q in fresh), Decimal("0.00"))
                    order = Order.objects.create(user=request.user, full_name=full_name, address=address, phone=phone, total=fresh_total)
                    for product, quantity in fresh:
                        OrderItem.objects.create(order=order, product=product, product_name=product.name, unit_price=product.price, quantity=quantity)
                        product.stock -= quantity
                        product.save(update_fields=["stock"])
                    request.session["cart"] = {}
                    messages.success(request, "Your order has been placed.")
                    return redirect("order_detail", order_id=order.pk)
    return render(request, "shop/checkout.html", {"items": items, "total": total, "cart_count": cart_count})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    _, _, cart_count = _cart_items(request)
    return render(request, "shop/orders.html", {"orders": orders, "cart_count": cart_count})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    _, _, cart_count = _cart_items(request)
    return render(request, "shop/order_detail.html", {"order": order, "cart_count": cart_count})

def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account is ready.")
            return redirect("home")
    else:
        form = UserCreationForm()
    _, _, cart_count = _cart_items(request)
    return render(request, "shop/register.html", {"form": form, "cart_count": cart_count})
