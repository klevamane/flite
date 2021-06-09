import json

from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from ..models import User,UserProfile,Referral
from .factories import UserFactory, DepositFactory
from ...core.utils import FAILURE_MSGS

fake = Faker()


class TestUserListTestCase(APITestCase):
    """
    Tests /users list operations.
    """

    def setUp(self):
        self.url = reverse('user-list')
        self.user_data = model_to_dict(UserFactory.build())

    def test_post_request_with_no_data_fails(self):
        response = self.client.post(self.url, {})
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data_succeeds(self):
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(pk=response.data.get('id'))
        eq_(user.username, self.user_data.get('username'))
        ok_(check_password(self.user_data.get('password'), user.password))

    def test_post_request_with_valid_data_succeeds_and_profile_is_created(self):
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(UserProfile.objects.filter(user__username=self.user_data['username']).exists(),True)

    def test_post_request_with_valid_data_succeeds_referral_is_created_if_code_is_valid(self):

        referring_user = UserFactory()
        self.user_data.update({"referral_code":referring_user.userprofile.referral_code})
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_201_CREATED)

        eq_(Referral.objects.filter(referred__username=self.user_data['username'],owner__username=referring_user.username).exists(),True)


    def test_post_request_with_valid_data_succeeds_referral_is_not_created_if_code_is_invalid(self):

        self.user_data.update({"referral_code":"FAKECODE"})
        response = self.client.post(self.url, self.user_data)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUserDetailTestCase(APITestCase):
    """
    Tests /users detail operations.
    """

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('user-detail', kwargs={'pk': self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user.auth_token}')

    def test_get_request_returns_a_given_user(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_put_request_updates_a_user(self):
        new_first_name = fake.first_name()
        payload = {'first_name': new_first_name}
        response = self.client.put(self.url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=self.user.id)
        eq_(user.first_name, new_first_name)


class TestTransactions(APITestCase):
    """
       Tests user transactions
       /account
       /:user_id/withdrawals
       /:user_id/deposits

    """
    def setUp(self):
        self.user = UserFactory()
        self.user2 = UserFactory()
        self.user.balance.available_balance = 100
        self.user.balance.book_balance = 100
        self.user.balance.save()
        self.url = reverse("user-detail", kwargs={"pk": self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user.auth_token}")

        self.deposit_url = reverse("deposit-url", kwargs={"user_id": self.user.pk})
        self.withdrawal_url = reverse(
            "withdrawal-url", kwargs={"user_id": self.user.pk}
        )
        self.transactions_url = reverse(
            "user-transactions", kwargs={"account_id": self.user.pk}
        )
        self.p2p_transfer_url = reverse(
            "p2p-transfer-url",
            kwargs={
                "sender_account_id": self.user.pk,
                "recipient_account_id": self.user2.pk,
            },
        )
        self.transaction_url = reverse(
            "user-transaction", kwargs={"transaction_id": self.user.pk}
        )

        DepositFactory.create(owner=self.user)
        self.transaction_url = reverse(
            "user-transaction",
            kwargs={"transaction_id": self.user.transaction.first().id},
        )

    def test_user_can_make_a_deposit(self):
        response = self.client.post(self.deposit_url, {"amount": 100})
        eq_(response.status_code, status.HTTP_201_CREATED)
        eq_(self.user.balance.available_balance, 100)
        # asset after deposit
        self.user.balance.refresh_from_db()
        eq_(self.user.balance.available_balance, 200)

    def test_user_can_make_a_deposit_fails(self):
        """
        Deposits must be greater than 0
        """
        payload = {"amount": 0}
        response = self.client.post(self.deposit_url, payload)
        # asset after deposit
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(FAILURE_MSGS["must_be_greater"].format("Deposit", 0),
            json.loads(response.content).get("amount")[0])

    def test_user_can_make_a_withdrawal(self):
        response = self.client.post(self.withdrawal_url, {"amount": 10})
        eq_(response.status_code, status.HTTP_201_CREATED)
        eq_(self.user.balance.available_balance, 100)
        # asset after deposit
        self.user.balance.refresh_from_db()
        eq_(self.user.balance.available_balance, 90)
        eq_(self.user.balance.book_balance, 90)

    def test_user_can_make_a_withdrawal_fails(self):
        """
        A user should not be able to withdraw more
        than the amount in the available balance
        """

        payload = {"amount": self.user.balance.available_balance + 10}
        response = self.client.post(self.withdrawal_url, payload)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(FAILURE_MSGS["insufficient_funds"],
            json.loads(response.content)[0])

    def test_user_can_make_a_p2p_transfer(self):
        # assert sender before transfer
        eq_(self.user.balance.available_balance, 100)
        response = self.client.post(self.p2p_transfer_url, {"amount": 70})
        eq_(response.status_code, status.HTTP_201_CREATED)

        # assert sender after transfer
        self.user.balance.refresh_from_db()
        eq_(self.user.balance.available_balance, 30)
        eq_(self.user.balance.book_balance, 30)

        # assert recipient after transfer
        self.user2.balance.refresh_from_db()
        eq_(self.user2.balance.book_balance, 70)
        eq_(self.user2.balance.available_balance, 70)

    def test_user_can_make_a_p2p_transfer_fails(self):
        """
        Cannot make a p2p transfer due to insufficient balance
        """
        payload = {"amount": self.user.balance.book_balance + 10}
        # assert sender before transfer
        eq_(self.user.balance.available_balance, 100)
        response = self.client.post(self.p2p_transfer_url, payload)
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)
        eq_(FAILURE_MSGS["insufficient_funds"], json.loads(response.content)[0])

    def test_user_can_make_a_p2p_to_self_fails(self):
        """
        Cannot make a p2p transfer to the same user
        """
        payload = {"amount": self.user.balance.book_balance - 10}
        response = self.client.post(self._set_url("p2p-transfer-url",
                sender_account_id=self.user.pk,
                recipient_account_id=self.user.pk
                                                  ), payload)
        eq_(FAILURE_MSGS["no_self_p2p"], json.loads(response.content)[0])
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_fetch_all_transactions(self):
        response = self.client.get(self.transactions_url)
        # assert after fetching data
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(self.user.transaction.count(), 1)

    def test_user_can_fetch_a_single_transaction(self):
        response = self.client.get(self.transaction_url)
        eq_(response.status_code, status.HTTP_200_OK)

        transaction = json.loads(response.content)
        # ensure that the response transaction id equals
        # the query parameter transaction id
        eq_(transaction["id"], str(self.user.transaction.first().id))
        eq_(transaction["owner"], str(self.user.id))

    def test_user_can_fetch_a_single_transaction_fails(self):
        """
        It raise a Permission denied error
        when fetching a transaction that the
        logged in user doesn't own

        """

        invalid_tnx_id = self.user.id
        response = self.client.get(self._set_url(
            "user-transaction",
            transaction_id=invalid_tnx_id,
        ))
        eq_(response.status_code, status.HTTP_403_FORBIDDEN)

    def _set_url(self, reverse_name, **kwargs):
        return reverse(reverse_name, kwargs={**kwargs})
