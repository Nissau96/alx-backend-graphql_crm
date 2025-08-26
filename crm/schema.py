# crm/schema.py

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from django.db import transaction
from django.db.models import Sum

from crm.models import Customer
from crm.models import Product
from crm.models import Order
from crm.models import validate_phone

from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.core.exceptions import ValidationError, ObjectDoesNotExist


# --- GraphQL Types ---

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "stock", "created_at")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount", "created_at")


# --- Queries ---

class Query(graphene.ObjectType):
    hello = graphene.String()
    orders = graphene.List(OrderType, order_date_Gte=graphene.Date())

    def resolve_hello(self, info):
        return "world"
    
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    customer_by_id = graphene.Field(CustomerType, id=graphene.ID(required=True))

    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    product_by_id = graphene.Field(ProductType, id=graphene.ID(required=True))

    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    order_by_id = graphene.Field(OrderType, id=graphene.ID(required=True))

    # Resolvers for fetching single objects by ID remain the same
    def resolve_customer_by_id(root, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

    def resolve_product_by_id(root, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_order_by_id(root, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None


# --- Mutations ---

# 1. CreateCustomer Mutation
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, name, email, phone=None):
        try:
            if phone:
                validate_phone(phone)
            if Customer.objects.filter(email=email).exists():
                raise GraphQLError(f"A customer with email '{email}' already exists.")
            
            # Change from .create() to explicit .save()
            customer = Customer(name=name, email=email, phone=phone)
            customer.save()

            message = "Customer created successfully!"
            return CreateCustomer(customer=customer, message=message)
        except ValidationError as e:
            raise GraphQLError(e.messages[0])


# 2. BulkCreateCustomers Mutation
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers_data = graphene.List(graphene.NonNull(CustomerInput), required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, customers_data):
        successful_customers = []
        error_messages = []

        customers_to_create = []

        for i, customer_data in enumerate(customers_data):
            email = customer_data.get('email')
            # Basic pre-validation
            if Customer.objects.filter(email=email).exists():
                error_messages.append(f"Row {i + 1}: Customer with email '{email}' already exists.")
                continue
            if 'phone' in customer_data and customer_data.get('phone'):
                try:
                    validate_phone(customer_data.get('phone'))
                except ValidationError as e:
                    error_messages.append(f"Row {i + 1} ({email}): {e.messages[0]}")
                    continue

            customers_to_create.append(
                Customer(name=customer_data.name, email=email, phone=customer_data.get('phone'))
            )

        # Bulk create valid customers in a single transaction
        if customers_to_create:
            try:
                with transaction.atomic():
                    successful_customers = Customer.objects.bulk_create(customers_to_create)
            except Exception as e:
                # This catches database-level errors during bulk_create
                error_messages.append(f"An unexpected error occurred during bulk creation: {str(e)}")

        return BulkCreateCustomers(customers=successful_customers, errors=error_messages)


# 3. CreateProduct Mutation
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, name, price, stock=0):
        if price <= 0:
            raise GraphQLError("Price must be a positive number.")
        if stock < 0:
            raise GraphQLError("Stock cannot be negative.")
        
        # Change from .create() to explicit .save()
        product = Product(name=name, price=price, stock=stock)
        product.save()
        
        return CreateProduct(product=product)


# 4. CreateOrder Mutation
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except ObjectDoesNotExist:
            raise GraphQLError(f"Customer with ID '{customer_id}' does not exist.")

        if not product_ids:
            raise GraphQLError("At least one product must be selected for an order.")

        found_products = Product.objects.filter(pk__in=product_ids)

        if len(found_products) != len(product_ids):
            found_ids = {str(p.id) for p in found_products}
            invalid_ids = [pid for pid in product_ids if pid not in found_ids]
            raise GraphQLError(f"Invalid Product IDs found: {', '.join(invalid_ids)}")

        total_amount = found_products.aggregate(total=Sum('price'))['total'] or 0.00
        
        order_kwargs = {'customer': customer, 'total_amount': total_amount}
        if order_date:
            order_kwargs['order_date'] = order_date
        
        # Change from .create() to explicit .save()
        order = Order(**order_kwargs)
        order.save()
        
        order.products.set(found_products)
        
        return CreateOrder(order=order)


class UpdateLowStockProducts(graphene.Mutation):
    # 2. Define the output fields of the mutation
    class Arguments:
        # This mutation takes no input arguments
        pass

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    # 3. The core mutation logic
    @staticmethod
    def mutate(root, info):
        # Find all products with stock less than 10
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_product_list = []
        
        # Loop through them and increment stock by 10
        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated_product_list.append(product)
            
        success = True
        message = f"Successfully restocked {len(updated_product_list)} products."
        
        # Return the results
        return UpdateLowStockProducts(
            success=success, 
            message=message, 
            updated_products=updated_product_list
        )


# --- Root Mutation ---

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)