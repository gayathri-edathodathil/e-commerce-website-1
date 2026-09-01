from django.urls import path,include
from . import views

urlpatterns = [
    path('wishlist',views.wishlist,name='wishlist'),
    path('add_to_wishlist/<int:product_id>',views.add_to_wishlist,name='add_to_wishlist'),
    path('checkout/',views.checkout,name='checkout'),
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('add_to_cart/',views.add_to_cart,name='add_to_cart'),
    path('cart',views.cart,name='cart'),
    path('login',views.login,name='login'),
    path('signup',views.signup,name='signup'),
    path('logout',views.logout,name='logout'),
]
