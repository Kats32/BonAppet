from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from ChatBot.models import Food
from UserData.models import Customer, DeliveryPartners, Users, Cart, Feedback
from ChatBot.models import Food
from django.contrib.auth.hashers import check_password
from decimal import Decimal
from django.http import JsonResponse
import json

@csrf_exempt
def user_login(request):
    if request.method != 'POST':
        return JsonResponse({"response": "Invalid request method"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"response": "Invalid JSON format"}, status=200)

    email = data.get("user_mail", "")
    password = data.get("password", "")
    print(email, password)
    
    try:
        user = Users.objects.get(email=email)
        if check_password(password, user.password):
            if user.is_customer:
                customer = Customer.objects.get(user=user)
                return JsonResponse({"response": "Login successful", "user_type": "Customer"}, status=200)
            elif user.is_partner:
                partner = DeliveryPartners.objects.get(user=user)
                return JsonResponse({"response": "Login successful", "user_type": "Delivery Partner"}, status=200)
        else:
            return JsonResponse({"response": "Login failed: Incorrect password"}, status=401)
    except ObjectDoesNotExist:
        return JsonResponse({"response": "Login failed: User not found"}, status=401)

@csrf_exempt
def partner_register(request):
    if request.method != 'POST':
        return JsonResponse({"response": "Invalid request method"}, status=405)
    try:
        info = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"response": "Invalid JSON format"}, status=400)
    employee_mail = info.get("user_mail", "")
    name = info.get("name", "")
    password = info.get("password", "")
    repassword = info.get("repassword", "")
    phone_no = info.get("phone", "")
    veh_model = info.get("model", "")
    license_no = info.get("license", "")
    veh_id = info.get("vehicle_id", "")
    print(info)
    if password != repassword:
        return JsonResponse({"error": "Passwords do not match"}, status=401)
    if Users.objects.filter(email=employee_mail).exists():
        return JsonResponse({"error": "Registration failed. User already exists."}, status=401)
    #user = Users.objects.create_user(request=request, email=employee_mail, password=password)
    partner = Users.objects.create_partner(request=request,  email=employee_mail, password=password, name=name, phone_number=phone_no, vehicle_model=veh_model, license_number=license_no, vehicle_id=veh_id)
    partner.save()
    return JsonResponse({"response": "Registration successful"}, status=200)


@csrf_exempt
def user_register(request):
    if request.method != 'POST':
        return JsonResponse({"response": "Invalid request method"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"response": "Invalid JSON format"}, status=400)

    user_mail = data.get("user_mail", "")
    user_name = data.get("user_name", "")
    password = data.get("password", "")
    repassword = data.get("repassword", "")
    phone_no = data.get("phone","")
    add = data.get("address","")
    print(data)
    if password != repassword:
        return JsonResponse({"response": "Passwords do not match"}, status=401)

    if Users.objects.filter(email=user_mail).exists():
        return JsonResponse({"response": "Registration Failed, User Exists"}, status=200)

    customer = Users.objects.create_customer(request=request, email=user_mail, password=password, user_name=user_name, phone_number = phone_no,address=add)
    customer.save()

    return JsonResponse({"response": "Registration Success"}, status=200)

def create_feedback(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"response": "Invalid JSON format"}, status=400)
    user_mail = data.get("user_mail", "")
    feedback = data.get("feedback", "")
    try:
        user = Users.objects.get(email=user_mail)
    except ObjectDoesNotExist:
        return JsonResponse({"response": "User not found"}, status=404)
    feedback = Feedback.objects.create(user=user, content=feedback)
    feedback.save()
    return JsonResponse({"response": "Feedback submitted successfully"}, status=200)

def create_cart(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"response": "Invalid JSON format"}, status=400)
    user_mail = data.get("user_mail", "")
    food_id = data.get("food_id", "")
    quantity = data.get("quantity", "")
    try:
        user = Users.objects.get(email=user_mail)
    except ObjectDoesNotExist:
        return JsonResponse({"response": "User not found"}, status=404)
    try:
        food = Food.objects.get(food_id=food_id)
    except ObjectDoesNotExist:
        return JsonResponse({"response": "Food not found"}, status=404)
    cart = Cart.objects.create(user=user, food=food, quantity=quantity)
    cart.save()
    return JsonResponse({"response": "Item added to cart"}, status=200)
def create_feedback(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"response": "Invalid JSON format"}, status=400)
    user_mail = data.get("user_mail", "")
    feedback = data.get("feedback", "")
    try:
        user = Users.objects.get(email=user_mail)
    except ObjectDoesNotExist:
        return JsonResponse({"response": "User not found"}, status=404)
    feedback = Feedback.objects.create(user=user, content=feedback)
    feedback.save()
    return JsonResponse({"response": "Feedback submitted successfully"}, status=200)

def create_cart(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"response": "Invalid JSON format"}, status=400)
    user_mail = data.get("user_mail", "")
    food_id = data.get("food_id", "")
    quantity = data.get("quantity", "")
    try:
        user = Users.objects.get(email=user_mail)
    except ObjectDoesNotExist:
        return JsonResponse({"response": "User not found"}, status=404)
    try:
        food = Food.objects.get(food_id=food_id)
    except ObjectDoesNotExist:
        return JsonResponse({"response": "Food not found"}, status=404)
    cart = Cart.objects.create(user=user, food=food, quantity=quantity)
    cart.save()
    return JsonResponse({"response": "Item added to cart"}, status=200)

@csrf_exempt
def get_cartitems(request):
    if request.method != 'POST':
        return JsonResponse({"response": "Invalid request method"}, status=405)
    try:
        info = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    user_id = info.get("customer_id", "")
    if not user_id:
        return JsonResponse({"error": "customer_id is required"}, status=400)
    try:
        customer = Customer.objects.get(user_id_suf=user_id)
    except Customer.DoesNotExist:
        return JsonResponse({"error": "Customer not found"}, status=400)
    cart_items = Cart.objects.filter(user=customer)
    cart_data = []
    for item in cart_items:
        if item.food and isinstance(item.food.price, (int, float, Decimal)):
            cart_data.append({
                'name': item.food.name,
                'quantity': item.quantity,
                'price': float(item.food.price)
            })
        else:
            return JsonResponse({"error": "Invalid food price data in cart"}, status=405)
    response = JsonResponse({"cart_items": cart_data})
    response.status_code = 200
    return response