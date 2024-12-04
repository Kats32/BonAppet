from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cart, Food

@receiver(post_save, sender=Cart)
def update_purchase_count(sender, instance, created, **kwargs):
    if created:  # only increment if the order is new
        food_item = instance.food_item
        food_item.purchase_count += instance.quantity  # increment by the order quantity
        food_item.save()
