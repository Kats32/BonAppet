from typing import Any
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinLengthValidator, MaxValueValidator 
from django.contrib.auth.hashers import make_password, check_password
from ChatBot.models import Food

class BAUserManager(BaseUserManager):

    def create_user(self, email, password, is_customer=False, is_partner=False, request=None, **extra_fields):
        if not email:
            raise ValueError('Email is required!')
        email = self.normalize_email(email)
        user = Users(email=email,is_customer=is_customer,is_partner=is_partner, **extra_fields)
        if not password:
            raise ValueError('Password is required.')
        user.set_password(password)
        user.save()
        return user
    
    def create_customer(self, request ,email, password, user_name, phone_number, address, **extra_fields):
        '''if 'email' in extra_fields:
            extra_fields.pop('email')
        if 'password' in extra_fields:
            extra_fields.pop('password')'''
        extra_fields.setdefault('is_customer', True)
        user = self.create_user(request=request, email=email, password=password, **extra_fields)
        customer = Customer.objects.create(
            user = user,
            user_name = user_name,
            phone_number = phone_number,
            address = address
        )
        return customer
    
    def create_partner(self, request, email, password, name, phone_number, vehicle_model, license_number, vehicle_id, **extra_fields):
        extra_fields.setdefault('is_partner', True)
        user = self.create_user(request=request, email=email, password=password, **extra_fields)
        partner = DeliveryPartners.objects.create(
            user = user,
            name = name,
            phone_number = phone_number,
            vehicle_model = vehicle_model,
            license_number = license_number,
            vehicle_id = vehicle_id 
        )
        return partner
class Users(AbstractBaseUser, PermissionsMixin):
    is_customer = models.BooleanField(default=False)
    is_partner = models.BooleanField(default=False)
    email = models.EmailField(max_length=45, unique=True, blank=False)
    password = models.CharField(max_length=200, validators=[MinLengthValidator(8)], blank=False)

    objects = BAUserManager()

    USERNAME_FIELD = 'email'
class Customer(models.Model):
    user = models.OneToOneField("Users", on_delete=models.CASCADE, null=True)
    user_pid = models.CharField(default="BA4")
    user_id_suf = models.AutoField(primary_key=True, default=1)
    user_name = models.CharField(max_length=75, blank=False, default="Your name")
    phone_number = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], blank=False)
    address = models.TextField(max_length=450, blank=False, default="ABC street, Nowhere city")

    def __str__(self):
        return f"{self.user_pid}{self.user_id_suf}"
    def welcome_message(self):
        return f"Glad to have you on board, {self.user_pid}{self.user_id_suf}! Share your cravings with us!"
    
class DeliveryPartners(models.Model):
    user = models.OneToOneField("Users", on_delete=models.CASCADE, null=True)
    employee_pid = models.CharField(default="BAdp2")
    employee_id_suf = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=False)
    phone_number = models.BigIntegerField(validators=[MaxValueValidator(9999999999)], blank=False)
    vehicle_model = models.CharField(max_length=50)
    license_number = models.CharField(max_length=15)
    vehicle_id = models.CharField(max_length=10, blank=False)

    objects = BAUserManager()

    def __str__(self):
        return f"{self.employee_pid}{self.employee_id_suf}"
    def welcome_message(self):
        return f"Welcome to the BonAppet Family, {self.employee_pid}{self.employee_id_suf}! Let's get started!"
    
class Feedback(models.Model):
    user = models.ForeignKey("Customer", on_delete=models.CASCADE, default=16)
    content = models.TextField(max_length=450)
    
@receiver(post_save, sender= [Users, DeliveryPartners])
def send_message(sender, instance, created, **kwargs):
        if created:
            print(instance.welcome_message())

class Cart(models.Model):
    user = models.ForeignKey('UserData.Customer', on_delete=models.CASCADE, default=9)
    food = models.ForeignKey('ChatBot.Food', on_delete=models.CASCADE, default=1)  
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name}"