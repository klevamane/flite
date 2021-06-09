from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User, NewUserPhoneVerification, Transaction
from .permissions import IsUserOrReadOnly, OwnerOnlyPermission
from .serializers import (
    CreateUserSerializer,
    UserSerializer,
    SendNewPhonenumberSerializer,
    CreateDepositSerializer,
    CreateWithdrawalSerializer,
    CreateP2PSerializer,
    ListTransactionsSerializer,
)
from . import utils


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)


class UserCreateViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        return UserSerializer if self.action == "list" else CreateUserSerializer


class SendNewPhonenumberVerifyViewSet(mixins.CreateModelMixin,mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Sending of verification code
    """
    queryset = NewUserPhoneVerification.objects.all()
    serializer_class = SendNewPhonenumberSerializer
    permission_classes = (AllowAny,)


    def update(self, request, pk=None,**kwargs):
        verification_object = self.get_object()
        code = request.data.get("code")

        if code is None:
            return Response({"message":"Request not successful"}, 400)

        if verification_object.verification_code != code:
            return Response({"message":"Verification code is incorrect"}, 400)

        code_status, msg = utils.validate_mobile_signup_sms(verification_object.phone_number, code)

        content = {
                'verification_code_status': str(code_status),
                'message': msg,
        }
        return Response(content, 200)


# class DepositCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
class DepositCreateViewSet(viewsets.ViewSet):
    permission_classes = (OwnerOnlyPermission,)

    def create(self, request, *args, **kwargs):
        serializer = CreateDepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        ctx = {
            "status": "complete",
            "amount": serializer.data["amount"],
            "transaction_type": "deposit"

        }
        return Response(ctx, status=status.HTTP_201_CREATED)


class WithdrawalCreateViewSet(viewsets.ViewSet):
    permission_classes = (OwnerOnlyPermission,)

    def create(self, request, *args, **kwargs):
        serializer = CreateWithdrawalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user)
        ctx = {
            "status": "complete",
            "amount": serializer.data["amount"],
            "transaction_type": "withdrawal"

        }
        return Response(ctx, status=status.HTTP_201_CREATED)


class P2PCreateViewSet(viewsets.ViewSet):
    permission_classes = (OwnerOnlyPermission, )

    def create(self, request, *args, **kwargs):
        serializer = CreateP2PSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request.user, kwargs)

        ctx = {
            "status": "complete",
            "amount": serializer.data["amount"],
            "transaction_type": "p2p transfer"
        }
        return Response(ctx, status=status.HTTP_201_CREATED)


class ListTransactionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ListTransactionsSerializer
    permission_classes = (OwnerOnlyPermission,)

    def get_queryset(self):
        return Transaction.objects.filter(owner=self.request.user).select_subclasses()


class RetrieveTransactionViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ListTransactionsSerializer
    permission_classes = (OwnerOnlyPermission,)
    lookup_url_kwarg = "transaction_id"

    def get_queryset(self):
        return Transaction.objects.filter(owner=self.request.user).select_subclasses()

