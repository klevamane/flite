from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .models import User, NewUserPhoneVerification, UserProfile, Referral, Balance, Transaction
from . import utils
from ..core.utils import FAILURE_MSGS, get_or_404


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',)
        read_only_fields = ('username', )


class CreateUserSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(required=False)


    def validate_referral_code(self, code):

        self.reffered_profile = UserProfile.objects.filter(referral_code=code.lower())
        is_valid_code = self.reffered_profile.exists()
        if not is_valid_code:
            raise serializers.ValidationError(
                "Referral code does not exist"
            )
        else:
            return code

    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        referral_code = None
        if 'referral_code' in validated_data:
            referral_code = validated_data.pop('referral_code',None)

        user = User.objects.create_user(**validated_data)

        if referral_code:
            referral =Referral()
            referral.owner = self.reffered_profile.first().user
            referral.referred = user
            referral.save()

        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'auth_token','referral_code')
        read_only_fields = ('auth_token',)
        extra_kwargs = {'password': {'write_only': True}}


class SendNewPhonenumberSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        phone_number = validated_data.get("phone_number", None)
        email = validated_data.get("email", None)

        obj, code = utils.send_mobile_signup_sms(phone_number, email)

        return {
            "verification_code":code,
            "id":obj.id
        }

    class Meta:
        model = NewUserPhoneVerification
        fields = ('id', 'phone_number', 'verification_code', 'email',)
        extra_kwargs = {'phone_number': {'write_only': True, 'required':True}, 'email': {'write_only': True}, }
        read_only_fields = ('id', 'verification_code')


class DepositWithdrawalBaseSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=1000_000, decimal_places=2)

    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError(FAILURE_MSGS["must_be_greater"].format("Deposit", 0))
        return amount


class CreateDepositSerializer(DepositWithdrawalBaseSerializer):
    def save(self, user):
        user.balance.make_deposit(self.validated_data["amount"])


class CreateWithdrawalSerializer(DepositWithdrawalBaseSerializer):
    def save(self, user):
        user.balance.make_withdrawal(self.validated_data["amount"])


class CreateP2PSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=1000_000, decimal_places=2)

    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError(FAILURE_MSGS["must_be_greater"].format("Transfer", 0))
        return amount

    def save(self, user, kwargs):
        sender = get_or_404(User, id=kwargs.pop("sender_account_id", None))
        recipient = get_or_404(User, id=kwargs.pop("recipient_account_id", None))
        if sender.id != user.id:
            raise PermissionDenied()
        if sender == recipient:
            raise serializers.ValidationError(FAILURE_MSGS["no_self_p2p"])
        sender.balance.make_p2p_transfer(self.validated_data["amount"], recipient.balance)


class ListTransactionsSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    class Meta:
        model = Transaction
        fields = "__all__"

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

