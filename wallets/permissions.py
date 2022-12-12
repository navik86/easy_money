from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed, NotFound

from . import services


class PostOrSafeMethodsOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        """Checks permissins for all request types"""
        if request.method in permissions.SAFE_METHODS or request.method == "POST":
            return True
        else:
            raise MethodNotAllowed(request.method)


class SenderWalletOwnerPermission(permissions.BasePermission):

    message = "Current user have no rights to proceed the transaction"

    def has_permission(self, request, view):
        """Checks permissins for all request types"""
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            wallet = services.get_specific_wallet(request.data.get("sender"))
            if wallet:
                return wallet.user == request.user
            else:
                raise NotFound(detail="Sender wallet doesn't exist", code=404)