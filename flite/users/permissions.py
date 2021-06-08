from rest_framework import permissions

from flite.users.models import Transaction


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class OwnerOnlyPermission(permissions.BasePermission):
    """
        Global permission check unauthorized user details access.
    """
    message = "You cannot access another user's account"

    def has_permission(self, request, view):
        kwargs = view.kwargs
        url_param_id = kwargs.get('user_id') or kwargs.get('sender_account_id') or kwargs.get('account_id')
        if not url_param_id:
            return Transaction.objects.filter(id=kwargs.get("transaction_id")).exists()
        return str(request.user.id) == str(url_param_id)
