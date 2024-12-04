from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat, name="chat"),
    path("insert-food/", views.insert_food, name="insert-food"),
    path("test/", views.test_vector, name="test"),
    path("clear/", views.clear_chat, name="clear"),
    path("fooditems/", views.get_fooditems, name="food-items"),
    path("topfive_restaurants/", views.topfive_restaurants, name="top-five-rest"),
    path("restaurant_details/", views.restauarant_details, name="restaurant-details"),
]