from django.urls import path
from .views import user_login
from .views import user_register, partner_register, create_cart, create_feedback, get_cartitems
urlpatterns = [
    path("login/", user_login),
    path("register/", user_register),
    path("staffregister/", partner_register),   
    path("create_feedback/", create_feedback),
    path("create_cart/", create_cart),
    path("cartitems/", get_cartitems),
]