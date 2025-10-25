from django.contrib import admin
from django.contrib.auth.models import User
from .models import Product, CustomUser,Cart,Order,Category,Transaction



admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Category)
admin.site.register(CustomUser)
admin.site.register(Transaction)

