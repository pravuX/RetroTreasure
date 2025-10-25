from django.db import models
from django.contrib.auth.models import AbstractUser
import os 
from django.conf import settings


class CustomUser(AbstractUser):

    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username 
    

class Category(models.Model):

    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name 
    

class Product(models.Model):
    name = models.CharField(max_length=40,blank=False,null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    description = models.CharField(max_length=600,default='')
    image= models.ImageField(upload_to='products',null=True,blank=False)
    stock = models.PositiveIntegerField(blank=False,default=1)
    category = models.ForeignKey(Category,default=1,on_delete=models.CASCADE)
    sold_count = models.PositiveIntegerField(default=0)

    def __str__(self):

        return self.name
    
    def delete(self, *args, **kwargs):
        # Delete image file from storage before deleting the Product instance
        if self.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(self.image))
            if os.path.exists(image_path):
                os.remove(image_path)

        super().delete(*args, **kwargs)



class Cart(models.Model):
    product = models.ForeignKey(Product,null=True,blank=False,on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser,null=True,blank=False,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True,null=True)
    status = models.BooleanField(default=0)

    def __str__(self):
        return f"{self.user} {self.product}"


class Order(models.Model):

    ...


class Transaction(models.Model):
    transaction_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Success", "Success"), ("Failed", "Failed")], default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"


