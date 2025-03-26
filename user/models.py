from django.db import models
from django.contrib.auth.models import User
from home.models import product
# Create your models here.

class wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='wishlist')
    product= models.ForeignKey(product,on_delete=models.CASCADE)

class cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='cart')
    product= models.ForeignKey(product,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    shippingAddress=models.TextField()
    totalprice=models.DecimalField(max_digits=10,decimal_places=2)
    