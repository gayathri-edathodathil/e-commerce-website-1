from rest_framework import serializers
from home.models import category, product
from user.models import cart, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = category
        fields = ['id', 'name', 'desc', 'icon']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = product
        fields = [
            'id', 'category', 'category_name', 'name', 
            'description', 'availability', 'stock', 'price', 'rating', 'img'
        ]

class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = cart
        fields = ['id', 'product', 'product_detail', 'quantity', 'shippingAddress', 'totalprice']
        read_only_fields = ['id', 'shippingAddress', 'totalprice']

class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate_product_id(self, value):
        try:
            prod = product.objects.get(id=value)
        except product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        if not prod.availability or prod.stock <= 0:
            raise serializers.ValidationError("Product is currently out of stock.")
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_username', 'full_name', 'email',
            'phone', 'address', 'city', 'postal_code', 'country', 'order_note',
            'total_price', 'status', 'payment_method', 'payment_status', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'user', 'total_price', 'created_at', 'updated_at']

class OrderCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    city = serializers.CharField(max_length=50)
    postal_code = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=50, default='United States')
    order_note = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField(default='Simulated Payment')
