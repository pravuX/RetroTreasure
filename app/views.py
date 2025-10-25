from django.shortcuts import render, redirect 
from django. contrib.auth import logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from .models import Cart, Transaction
from django.http import JsonResponse
import json 
import base64


def paymentSuccess(request):

    user = request.user 
    data_encoded = request.GET.get('data')

    data_bytes = base64.urlsafe_b64decode(data_encoded + '==')  # add padding if needed
    data_json = data_bytes.decode('utf-8')
    payment_data = json.loads(data_json)
    print(payment_data)

        # Example: get the values
    transaction_code = payment_data.get('transaction_code')
    status = payment_data.get('status')
    amount = payment_data.get('total_amount')  # might be "1,300.0" string
    transaction_id = payment_data.get('transaction_uuid')            
    product_code = payment_data.get('product_code')
    transcaction = Transaction.objects.get(transaction_id=transaction_id)

    transcaction.status = "Success"
    transcaction.save()



         # Optional: clean the amount string
    amount = float(amount.replace(",", ""))



    try :
        carts = Cart.objects.filter(user=user,status=0).first()



        carts.status = 1

        carts.save()

    except(Cart.DoesNotExist):
        pass 


    return redirect("home_page")




    

@api_view(["GET"])
def esewa_failure(request):

    return JsonResponse({"status": "failure", "message": "Payment failed!"})



def login_page(request):
    return render(request,"app/login_page.html")


def register_page(request):
    return render(request,"app/register_page.html")


def logout_page(request):
    logout(request)
    return redirect('login_page')

def send_mail(request):
    ...


@login_required(login_url="login_page")
def dashboard_view(request):

    information = {}

    return render(request,"app/dashboard.html",{"information":information})


def home_page(request):
    return render(request,"app/home_page.html")

def products_page(request):
    return render(request,"app/products_page.html")

def cart_page(request):
    return render(request,"app/cart_page.html")

