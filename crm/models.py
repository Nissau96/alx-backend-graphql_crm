# crm/models.py

import re
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_phone(value):
    """
    Validates that the phone number is in a format like +1234567890 or 123-456-7890.
    """
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    dashed_phone_regex = re.compile(r'^\d{3}-\d{3}-\d{4}$')
    if not phone_regex.match(value.replace("-", "")) and not dashed_phone_regex.match(value):
        raise ValidationError("Phone number must be entered in the format: '+999999999' or '123-456-7890'.")


class Customer(models.Model):
    name = models.CharField(max_length=100) # <-- Change this from 255 to 100
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True, validators=[validate_phone])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100) # <-- Change this from 255 to 100
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer.name}"


from django.db import models

# Create your models here.
