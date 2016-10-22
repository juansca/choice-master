# from django.db import models
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib import messages


@receiver(user_signed_up)
def user_signed_up_callback(sender, request, user, **kwargs):
    messages.success(request, 'Se ha registrado exitosamente!')
