from django.db import models
# Create your models here.

class category(models.Model):
    name=models.CharField(max_length=20)
    desc=models.TextField(default='Nothing')
    icon=models.ImageField(upload_to='icons')

    def __str__(self):
        return self.name

class product(models.Model):
    category=models.ForeignKey(category,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    description=models.TextField()
    availability=models.BooleanField()
    stock=models.PositiveIntegerField(default=50)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    rating=models.DecimalField(max_digits=2,decimal_places=1)
    img=models.ImageField(upload_to='product_pics')

    def __str__(self):
        return self.name