from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('shop',views.shop,name='shop'),
    path('about',views.about,name='about'),
    path('contact',views.contact,name='contact'),
    path('product/<int:item_id>',views.productDetails,name='product')
]
