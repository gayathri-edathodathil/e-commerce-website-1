from django.urls import path,include
from . import views

urlpatterns = [
    path('wishlist',views.wishlist,name='wishlist'),
    path('add_to_wishlist/<int:product_id>',views.add_to_wishlist,name='add_to_wishlist'),
    path('checkout/',views.checkout,name='checkout'),
    path('add_to_cart/',views.add_to_cart,name='add_to_cart'),
    path('cart',views.cart,name='cart'),
    path('login',views.login,name='login'),
    path('signup',views.signup,name='signup'),
    path('logout',views.logout,name='logout'),
]
