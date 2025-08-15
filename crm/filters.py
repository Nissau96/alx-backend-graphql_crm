# crm/filters.py

import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    # Custom filter for phone number pattern (e.g., starts with a specific prefix)
    phone_pattern = django_filters.CharFilter(method='filter_by_phone_pattern', label="Phone starts with")

    # Ordering filter to allow sorting
    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('email', 'email'),
            ('created_at', 'created_at'),
        )
    )

    class Meta:
        model = Customer
        # Define fields and their lookup expressions for filtering
        fields = {
            'name': ['icontains'],
            'email': ['icontains'],
            'created_at': ['gte', 'lte'],
        }

    def filter_by_phone_pattern(self, queryset, name, value):
        # This custom method is linked to the 'phone_pattern' filter
        return queryset.filter(phone__startswith=value)


class ProductFilter(django_filters.FilterSet):
    # Custom filter for finding products with low stock
    low_stock = django_filters.BooleanFilter(method='filter_low_stock', label="Low Stock (less than 10)")

    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('price', 'price'),
            ('stock', 'stock'),
        )
    )

    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'price': ['gte', 'lte'],
            'stock': ['gte', 'lte'],
        }

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


class OrderFilter(django_filters.FilterSet):
    # Filters for related fields
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')

    # Challenge: Filter orders that contain a specific product ID
    product_id = django_filters.NumberFilter(field_name='products__id', lookup_expr='exact')

    order_by = django_filters.OrderingFilter(
        fields=(
            ('total_amount', 'total_amount'),
            ('order_date', 'order_date'),
        )
    )

    class Meta:
        model = Order
        fields = {
            'total_amount': ['gte', 'lte'],
            'order_date': ['gte', 'lte'],
        }