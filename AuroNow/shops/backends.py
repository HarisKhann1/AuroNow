from django.contrib.auth.backends import BaseBackend
from .models import ShopOwner

class ShopOwnerBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            owner = ShopOwner.objects.get(email=email)
            if owner.check_password(password):
                return owner
        except ShopOwner.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return ShopOwner.objects.get(pk=user_id)
        except ShopOwner.DoesNotExist:
            return None
