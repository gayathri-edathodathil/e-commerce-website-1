import uuid
import datetime
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import transaction

from home.models import category, product
from user.models import cart, Order, OrderItem
from .serializers import (
    CategorySerializer, ProductSerializer, CartItemSerializer,
    CartAddSerializer, OrderSerializer, OrderCreateSerializer
)

class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        queryset = product.objects.all().order_by('id')
        category_id = self.request.query_params.get('category')
        search_query = self.request.query_params.get('search') or self.request.query_params.get('q')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return cart.objects.filter(user=self.request.user).order_by('id')

    def create(self, request, *args, **kwargs):
        serializer = CartAddSerializer(data=request.data)
        serializer.is_validate_obj = serializer.is_valid(raise_exception=True)
        
        prod_id = serializer.validated_data['product_id']
        qty = serializer.validated_data['quantity']
        prod = get_object_or_404(product, id=prod_id)

        if prod.stock < qty:
            return Response(
                {"error": f"Only {prod.stock} units available in stock."},
                status=status.HTTP_400_BAD_REQUEST
            )

        totalprice = prod.price * qty
        cart_item, created = cart.objects.get_or_create(
            user=request.user,
            product=prod,
            defaults={'quantity': qty, 'totalprice': totalprice, 'shippingAddress': ''}
        )

        if not created:
            cart_item.quantity += qty
            if prod.stock < cart_item.quantity:
                return Response(
                    {"error": f"Cannot add more. Stock limit of {prod.stock} reached."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.totalprice = prod.price * cart_item.quantity
            cart_item.save()

        result_serializer = CartItemSerializer(cart_item)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        new_qty = request.data.get('quantity')
        
        if new_qty is not None:
            try:
                new_qty = int(new_qty)
            except ValueError:
                return Response({"error": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)
                
            if new_qty <= 0:
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            if instance.product.stock < new_qty:
                return Response(
                    {"error": f"Stock limit exceeded. Only {instance.product.stock} available."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            instance.quantity = new_qty
            instance.totalprice = instance.product.price * new_qty
            instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        user_cart = cart.objects.filter(user=request.user)
        if not user_cart.exists():
            return Response(
                {"error": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Stock check
        for item in user_cart:
            if item.product.stock < item.quantity:
                return Response(
                    {"error": f"Insufficient stock for {item.product.name}. Stock: {item.product.stock}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        grand_total = sum(item.product.price * item.quantity for item in user_cart)
        order_num = f"ORD-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                order_number=order_num,
                full_name=data['full_name'],
                email=data['email'],
                phone=data['phone'],
                address=data['address'],
                city=data['city'],
                postal_code=data['postal_code'],
                country=data.get('country', 'United States'),
                order_note=data.get('order_note', ''),
                total_price=grand_total,
                status='Confirmed',
                payment_method=data.get('payment_method', 'Simulated Payment'),
                payment_status='Paid'
            )

            for item in user_cart:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity
                )
                item.product.stock -= item.quantity
                if item.product.stock <= 0:
                    item.product.availability = False
                item.product.save()

            user_cart.delete()

        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin/staff users can modify order status."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "Only admin/staff users can modify order status."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)
