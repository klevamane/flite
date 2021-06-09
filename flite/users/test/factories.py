import factory

from flite.users.models import Transaction


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'users.User'
        django_get_or_create = ('username',)

    id = factory.Faker('uuid4')
    username = factory.Sequence(lambda n: f'testuser{n}')
    password = factory.Faker('password', length=10, special_chars=True, digits=True,
                             upper_case=True, lower_case=True)
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False


class BalanceFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'users.Balance'
        django_get_or_create = ('owner',)

    id = factory.Faker('uuid4')
    owner = factory.SubFactory(UserFactory)
    book_balance = '200.99'
    available_balance = '200.99'
    active = factory.Faker("boolean")


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.Transaction'

    owner = factory.SubFactory(UserFactory)
    reference = factory.Faker('pystr', min_chars=None, max_chars=20)
    status = True
    amount = 500
    new_balance = 500


class DepositFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.Deposit'
