from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from home.models import category, product
from user.models import cart, Order, OrderItem

class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        self.admin = User.objects.create_superuser(username='adminuser', password='adminpassword123', email='admin@example.com')

        # Create category and products
        self.cat1 = category.objects.create(name='Electronics', desc='Tech gadgets')
        self.cat2 = category.objects.create(name='Clothing', desc='Fashion items')

        self.prod1 = product.objects.create(
            category=self.cat1,
            name='Smartphone',
            description='Latest flagship phone',
            availability=True,
            stock=10,
            price=999.99,
            rating=4.5
        )
        self.prod2 = product.objects.create(
            category=self.cat2,
            name='T-Shirt',
            description='Cotton t-shirt',
            availability=True,
            stock=20,
            price=29.99,
            rating=4.0
        )

    def test_category_list_and_detail(self):
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response = self.client.get(f'/api/categories/{self.cat1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Electronics')

    def test_product_list_and_filtering(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Filter by category
        response = self.client.get(f'/api/products/?category={self.cat1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Smartphone')

    def test_cart_operations(self):
        # Unauthenticated cart access
        response = self.client.get('/api/cart/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Authenticate user
        self.client.force_authenticate(user=self.user)

        # Add item to cart
        data = {'product_id': self.prod1.id, 'quantity': 2}
        response = self.client.post('/api/cart/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(cart.objects.filter(user=self.user).count(), 1)

        # List cart
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Update cart item quantity
        cart_item_id = response.data[0]['id']
        response = self.client.patch(f'/api/cart/{cart_item_id}/', {'quantity': 3}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(cart.objects.get(id=cart_item_id).quantity, 3)

        # Delete cart item
        response = self.client.delete(f'/api/cart/{cart_item_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(cart.objects.filter(user=self.user).count(), 0)

    def test_order_creation_and_stock_deduction(self):
        self.client.force_authenticate(user=self.user)

        # Add product to cart
        self.client.post('/api/cart/', {'product_id': self.prod1.id, 'quantity': 2}, format='json')

        # Place order
        shipping_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'address': '123 Main St',
            'city': 'New York',
            'postal_code': '10001',
            'country': 'United States',
            'payment_method': 'Simulated Payment'
        }

        response = self.client.post('/api/orders/', shipping_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_number', response.data)
        
        # Verify cart was cleared
        self.assertEqual(cart.objects.filter(user=self.user).count(), 0)

        # Verify stock deducted
        self.prod1.refresh_from_db()
        self.assertEqual(self.prod1.stock, 8)

        # Verify order in database
        order = Order.objects.get(order_number=response.data['order_number'])
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product_name, 'Smartphone')

    def test_order_status_update_permissions(self):
        # Create an order
        order = Order.objects.create(
            user=self.user,
            order_number='ORD-TEST-001',
            full_name='Test User',
            email='test@example.com',
            phone='1234567890',
            address='123 Main St',
            city='New York',
            postal_code='10001',
            country='United States',
            total_price=999.99,
            status='Confirmed'
        )

        # Regular user cannot change status
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'/api/orders/{order.id}/', {'status': 'Shipped'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin user can change status
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f'/api/orders/{order.id}/', {'status': 'Shipped'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'Shipped')
