from django.conf import settings
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=160)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ("placed", "Placed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shop_orders")
    full_name = models.CharField(max_length=160)
    address = models.TextField()
    phone = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="placed")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} — {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=160)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product_name}"
