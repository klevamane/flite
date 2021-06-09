from django.test import TestCase
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import eq_, ok_
from .factories import UserFactory
from ..serializers import CreateUserSerializer, CreateDepositSerializer, CreateWithdrawalSerializer, \
    CreateP2PSerializer


class TestCreateUserSerializer(TestCase):

    def setUp(self):
        self.user_data = model_to_dict(UserFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = CreateUserSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = CreateUserSerializer(data=self.user_data)
        ok_(serializer.is_valid())

    def test_serializer_hashes_password(self):
        serializer = CreateUserSerializer(data=self.user_data)
        ok_(serializer.is_valid())

        user = serializer.save()
        ok_(check_password(self.user_data.get('password'), user.password))


class TestCreateDepositSerializer(TestCase):

    def setUp(self):
        self.serializer_class = CreateDepositSerializer

    def test_serializer_with_empty_data(self):
        serializer = self.serializer_class(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_amount_invalid_amount(self):
        serializer = self.serializer_class(data={"amount": 0})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_amount(self):
        serializer = self.serializer_class(data={"amount": 10})
        ok_(serializer.is_valid())


class TestCreateWithdrawalSerializer(TestCreateDepositSerializer):

    def setUp(self):
        self.serializer_class = CreateWithdrawalSerializer


class TestCreateP2PSerializer(TestCreateDepositSerializer):

    def setUp(self):
        self.serializer_class = CreateP2PSerializer
