from django.contrib.auth.models import User 
from app.models import Product,Cart
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User 
        fields = ["id","username","password"]
        extra_kwargs = {"password":{"write_only":True}} 


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','price','description','image','stock','category','sold_count']



class CartSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='product.name')  # Get product name
    price = serializers.FloatField(source='product.price')  # Get product price
    image = serializers.SerializerMethodField()  # Custom method to handle image URL
    product_id =serializers.IntegerField(source='product.id')
    class Meta:
        model = Cart
        fields = ['id','name', 'price', 'quantity', 'image',"product_id"]  # Fields to include in JSON response

    def get_image(self, obj):
        """Returns full image URL if image exists"""
        request = self.context.get('request')
        
        if obj.product.image:
            return request.build_absolute_uri(obj.product.image.url)
        return None