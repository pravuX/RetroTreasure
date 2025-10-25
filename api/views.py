from django.shortcuts import render,redirect,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from rest_framework import status 
from app.models import CustomUser,Product,Cart
from .serializers import ProductSerializer,CartSerializer
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import uuid
import hashlib
import hmac
import base64
from django.db import IntegrityError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from app.models import Transaction


@api_view(["POST"])
def login_api(request):

    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password :
        return Response({"error": "Username and password required"}, status= status.HTTP_400_BAD_REQUEST)
    

    user = authenticate(username=username,password=password)


    if user :
        login(request,user)
        return Response({"message":"Login Successful" }, status=status.HTTP_200_OK)

    elif CustomUser.objects.filter(username=username).exists():

        return Response({"error":"Password doesnot match"},status=status.HTTP_401_UNAUTHORIZED)
    

    else :
        return Response({"error":"user doesnot exist "},status=status.HTTP_404_NOT_FOUND)
    


@api_view(['POST'])
def register_api(request):

    username = request.data.get("username")
    firstName = request.data.get("firstName")
    lastName = request.data.get("lastName")
    print(request.data)
    if len(firstName) < 2 or len(lastName) < 2:
        return Response ({"message":"Name must not be empty "},status = status.HTTP_400_BAD_REQUEST)
    

    if CustomUser.objects.filter(username=username).exists():

        return Response({"message":"username already exists "},status=status.HTTP_409_CONFLICT)
    
    else :
        password = request.data.get("password")
        user = CustomUser.objects.create_user(username=username,password=password)
        user.is_verified = False 
        user.first_name = firstName
        user.last_name = lastName
        user.save()
        return Response({"message":"User create successfully"},status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
def trending_product(request):

    trending_products = Product.objects.order_by('-sold_count')[:10]  
    serializer = ProductSerializer(trending_products,many=True)
    return Response(serializer.data)


@api_view(['GET','POST'])
def product_view(request):
    ...

@login_required(login_url="/login") 
@api_view(['POST'])
def add_to_cart(request,productId):
    if request.user.is_authenticated:

        data = request.data
        user=request.user
        product = get_object_or_404(Product,id=productId)

        cart_item, created = Cart.objects.get_or_create(user=user, product=product, status=0)

        if not created:
            cart_item.quantity += 1
            cart_item.save()
            return Response({"message": "Cart updated successfully", "quantity": cart_item.quantity}, status=200)

        return Response({"message":"Product added to cart "},status=status.HTTP_201_CREATED)
        
    else:
        return Response({"message":"user need to login before cart"},status=status.HTTP_401_UNAUTHORIZED)
    


@api_view(['POST'])
def decrement_cart(request, productId):
    # Get the product or 404
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=productId)

        # Get all matching cart entries
        cart_items = Cart.objects.filter(user=request.user, product=product).order_by('-id')

        if not cart_items.exists():
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        cart = cart_items.first()  # Use the most recent one

        if cart.quantity > 0:
            cart.quantity -= 1
            cart.save()
            return Response({"message": "Product quantity decremented."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Quantity already at zero."}, status=status.HTTP_400_BAD_REQUEST)
        
        

@api_view(['GET'])
def get_cart(request):
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user, status=0).select_related('product')
        serializer = CartSerializer(carts, many=True, context={'request': request})
        
        return Response(serializer.data, status=200)  # Directly returning the list

    return Response({'message': 'User not authenticated'}, status=401)

@api_view(['DELETE'])
def delete_cart(request,cartId):
    
    if Cart.objects.filter(id=cartId).exists():

        cart = Cart.objects.get(id=cartId)
        cart.delete()

        return Response({'message':"cart delete successfully"},status=status.HTTP_200_OK)
    
    return Response({'error':"cart not found"},status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def esewa_payment_api(request):
    # eSewa Configuration
    ESEWA_MERCHANT_CODE = "EPAYTEST"  # Change for production
    SUCCESS_URL = "http://127.0.0.1:8000/payment/success/"
    FAILURE_URL = "http://127.0.0.1:8000/payment/failure/"
    SECRET_KEY = b"8gBm/:&EnhH.1/q"  # Ensure it's in bytes

    # Validate total
    try:
        total = float(request.data.get("total", 0))
        if total <= 0:
            return Response({"error": "Invalid total amount"}, status=400)
    except ValueError:
        return Response({"error": "Invalid total amount format"}, status=400)

    # Generate a unique transaction ID
    transaction_uuid = str(uuid.uuid4())

    # Ensure the transaction ID is unique in the database
    while True:
        try:
            transaction = Transaction.objects.create(transaction_id=transaction_uuid, amount=total)
            break  # Exit loop if transaction is saved
        except IntegrityError:
            transaction_uuid = str(uuid.uuid4())  # Regenerate if duplicate exists

    # Format total to exactly two decimal places
    formatted_total = "{:.2f}".format(total)


    # Create message for signature (Ensure order matches eSewa's requirements)
    message = f"total_amount={formatted_total},transaction_uuid={transaction_uuid},product_code={ESEWA_MERCHANT_CODE}".encode('utf-8')


    # Generate HMAC-SHA256 signature
    hmac_sha256 = hmac.new(SECRET_KEY, message, hashlib.sha256)
    digest = hmac_sha256.digest()
    signature = base64.b64encode(digest).decode('utf-8')  # Convert to Base64 string

    # Debugging output (optional)
   
    return Response({
        "amount": formatted_total,
        "tax_amount": "0.00",
        "total_amount": formatted_total,
        "transaction_uuid": str(transaction_uuid),  # Always unique
        "product_code": ESEWA_MERCHANT_CODE,
        "product_service_charge": "0.00",
        "product_delivery_charge": "0.00",
        "success_url": SUCCESS_URL,
        "failure_url": FAILURE_URL,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "signature": signature,
    },status=status.HTTP_200_OK)

















