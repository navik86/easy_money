import pytest
from accounts.models import User
from wallets.models import Wallet, Transaction, DEFAULT_COMMISSION
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from wallets.serializers import WalletSerializer, TransactionSerializer


@pytest.fixture()
def user1():
    """User fixture"""

    user, created = User.objects.get_or_create(email="user1@gmail.com")
    if created:
        user.set_password("user1user1")
        user.save()
    wallets = [
        {
            "name": "U1RUS1",
            "type": "Visa",
            "balance": 100,
            "currency": "RUS",
        },
        {
            "name": "U1RUS2",
            "type": "Visa",
            "balance": 100,
            "currency": "RUS",
        },
        {
            "name": "U1USD1",
            "type": "Visa",
            "balance": 100,
            "currency": "USD",
        },
        {
            "name": "U1EUR1",
            "type": "Visa",
            "balance": 100,
            "currency": "EUR",
        },
    ]
    for wallet in wallets:
        Wallet.objects.create(**wallet, owner=user)

    return user


@pytest.fixture
def user2():
    """Second user fixture"""

    user, created = User.objects.get_or_create(email="user2@gmail.com")
    if created:
        user.set_password("user2user2")
        user.save()

    wallets = [
        {
            "name": "U2RUS1",
            "type": "Visa",
            "balance": 100,
            "currency": "RUS",
        },
        {
            "name": "U2USD1",
            "type": "Visa",
            "balance": 100,
            "currency": "USD",
        },
        {
            "name": "U2USD2",
            "type": "Visa",
            "balance": 100,
            "currency": "USD",
        },
        {
            "name": "U2EUR1",
            "type": "Visa",
            "balance": 100,
            "currency": "EUR",
        },
    ]
    for wallet in wallets:
        Wallet.objects.create(**wallet, owner=user)

    return user


@pytest.fixture
def auth_client1(user1):
    client = APIClient()
    refresh = RefreshToken.for_user(user1)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def auth_client2(user2):
    client = APIClient()
    refresh = RefreshToken.for_user(user2)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture()
def create_transactions(user1, user2):
    """Fixture to create transactions"""
    transactions = [
        {"sender": "U1RUS1", "receiver": "U2RUS1", "transfer_amount": 10},
        {"sender": "U2USD1", "receiver": "U1USD1", "transfer_amount": 10},
        {"sender": "U2EUR1", "receiver": "U1EUR1", "transfer_amount": 10},
        {"sender": "U2USD1", "receiver": "U2USD2", "transfer_amount": 10},
    ]

    for transaction in transactions:
        Transaction.objects.create(
            sender=Wallet.objects.get(name=transaction["sender"]),
            receiver=Wallet.objects.get(name=transaction["receiver"]),
            transfer_amount=transaction["transfer_amount"],
        )


class TestTransactionApi:
    """Class to test /transaction api"""

    @pytest.mark.django_db
    def test_transaction_create_invalid_wallets(self, auth_client1):
        """Testing creation of a transaction with invalid wallets"""

        unauth_client = APIClient()
        response = unauth_client.post("/transactions/")
        assert response.status_code == 401

        response = auth_client1.post(
            "/transactions/",
            data={"receiver": "NoWallet", "sender": "U1RUS1", "transfer_amount": 10},
        )
        assert response.status_code == 404

        response = auth_client1.post(
            "/transactions/",
            data={"receiver": "U2RUS2", "sender": "NoWallet", "transfer_amount": 10},
        )
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_transaction_create_with_not_users_sender_wallet(self, auth_client1):
        """Testing user permision to create a transaction
        only if sender wallet is a current user wallet"""

        response = auth_client1.post(
            "/transactions/",
            data={"receiver": "U1RUS1", "sender": "U2RUS1", "transfer_amount": 10},
        )
        assert response.status_code == 404 or 403

    @pytest.mark.django_db
    def test_transaction_create_not_eq_currency(self, auth_client1):
        """Transaction can be procced only if wallets currencies are equal"""

        response = auth_client1.post(
            "/transactions/",
            data={"receiver": "U1USD1", "sender": "U1RUS1", "transfer_amount": 10},
        )
        assert response.status_code == 400

        response = auth_client1.post(
            "/transactions/",
            data={"receiver": "U1RUS2", "sender": "U1RUS1", "transfer_amount": 10},
        )
        assert response.status_code == 201

    @pytest.mark.django_db
    def test_transaction_create_transfer_amount_exceeds_balance(self, auth_client1):
        """Test if transaction fails when sender doesn't have enough funds"""

        response = auth_client1.post(
            "/transactions/",
            data={"receiver": "U1RUS2", "sender": "U1RUS1", "transfer_amount": 1000},
        )
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_transaction_create_fee_check(self, auth_client1, auth_client2):
        """Testing balances after transaction and fee calculation"""

        response = auth_client1.post(
            "/transactions/",
            data={"receiver": "U1RUS2", "sender": "U1RUS1", "transfer_amount": 10},
        )
        assert response.status_code == 201

        sender = Wallet.objects.get(name="U1RUS1")
        serializer = WalletSerializer(sender)
        assert float(serializer.data["balance"]) == 90

        receiver = Wallet.objects.get(name="U1RUS2")
        serializer = WalletSerializer(receiver)
        assert float(serializer.data["balance"]) == 110

        response = auth_client1.post(
            "/transactions/",
            data={"receiver": "U2USD1", "sender": "U1USD1", "transfer_amount": 10},
        )
        assert response.status_code == 201

        sender = Wallet.objects.get(name="U1USD1")
        serializer = WalletSerializer(sender)
        assert float(serializer.data["balance"]) == 90 - (DEFAULT_COMMISSION * 10)

        receiver = Wallet.objects.get(name="U1RUS2")
        serializer = WalletSerializer(receiver)
        assert float(serializer.data["balance"]) == 110

    @pytest.mark.django_db
    def test_transaction_get(self, auth_client1, user1):
        """Testing get request"""

        unauth_client = APIClient()
        response = unauth_client.get("/transactions/")
        assert response.status_code == 401

        response = auth_client1.get("/transactions/")
        transactions = response.json()
        assert response.status_code == 200

        user_wallets = user1.wallet_set.all()
        serializer_wallets = WalletSerializer(user_wallets, many=True)
        user_wallets_names = [wallet["name"] for wallet in serializer_wallets.data]
        for transaction in transactions:
            statement = (
                transaction["sender"] in user_wallets_names
                or transaction["receiver"] in user_wallets_names
            )
            assert statement

    @pytest.mark.django_db
    def test_wallet_method_not_allowed(self, auth_client1):
        """Testing if PUT, PATCH, DELETE are not allowed"""

        response = auth_client1.put("/transactions/")
        assert response.status_code == 405

        response = auth_client1.patch("/transactions/")
        assert response.status_code == 405

        response = auth_client1.delete("/transactions/")
        assert response.status_code == 405


class TestTransactionIdDetailApi:
    """Test /transaction/<int:id>"""

    @pytest.mark.django_db
    def test_transaction_id_get(self, auth_client1, create_transactions):
        """Testing get request"""

        user1_wallet = Wallet.objects.get(name="U1RUS1")
        serializer_transaction = TransactionSerializer(
            user1_wallet.senders.all().first()
        )
        print(serializer_transaction.data)
        id = serializer_transaction.data["id"]

        unauth_client = APIClient()
        response = unauth_client.get(f"/transactions/{id}/")
        assert response.status_code == 401

        response = auth_client1.get(f"/transactions/{id}/")
        assert response.status_code == 200

        user2_wallet = Wallet.objects.get(name="U2USD2")
        serializer_transaction = TransactionSerializer(
            user2_wallet.receivers.all().first()
        )
        id = serializer_transaction.data["id"]

        response = auth_client1.get(f"/transactions/{id}/")
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_transaction_method_not_allowed(self, auth_client1):
        """Testing if DELETE, POST, PUT, PATCH are not allowed"""

        response = auth_client1.put("/transactions/15/")
        assert response.status_code == 405

        response = auth_client1.patch("/transactions/15/")
        assert response.status_code == 405

        response = auth_client1.delete("/transactions/15/")
        assert response.status_code == 405

        response = auth_client1.post("/transactions/14/", data={"sender": "U1RUS1"})
        assert response.status_code == 405


class TestTransactionOfWalletApi:
    @pytest.mark.django_db
    def test_transaction_wallet_get(self, auth_client1, create_transactions):
        """Testing get request"""

        unauth_client = APIClient()
        user1_wallet_name = "U1RUS1"
        response = unauth_client.get(f"/transactions/{user1_wallet_name}/")
        assert response.status_code == 401

        response = auth_client1.get(f"/transactions/{user1_wallet_name}/")
        response_transactions = response.json()
        assert response.status_code == 200

        user1_wallet = Wallet.objects.get(name=user1_wallet_name)
        serialized_wallet_sender_transactions = TransactionSerializer(
            user1_wallet.senders.all(), many=True
        )

        serialized_wallet_receive_transactions = TransactionSerializer(
            user1_wallet.receivers.all(), many=True
        )

        for transaction in response_transactions:
            statement = (
                transaction in serialized_wallet_sender_transactions.data
                or transaction in serialized_wallet_receive_transactions
            )
            assert statement

        user2_wallet_name = "U2RUS1"
        try:
            response = auth_client1.get(f"/transactions/{user2_wallet_name}/")
        except Wallet.DoesNotExist:
            assert True

    @pytest.mark.django_db
    def test_transaction_method_not_allowed(self, auth_client1, create_transactions):
        """Testing if DELETE, POST, PUT, PATCH are not allowed"""

        wallet = "U1RUS1"
        response = auth_client1.put(f"/transactions/{wallet}/")
        assert response.status_code == 405

        response = auth_client1.patch(f"/transactions/{wallet}/")
        assert response.status_code == 405

        response = auth_client1.delete(f"/transactions/{wallet}/")
        assert response.status_code == 405

        response = auth_client1.post(f"/transactions/{wallet}/")
        assert response.status_code == 405
