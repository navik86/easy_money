import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from wallets.models import BONUSES, MAX_NUMBER_OF_WALLETS, Wallet


@pytest.fixture
def user():
    user, created = User.objects.get_or_create(email="user1@gmail.com")
    if created:
        user.set_password("user1user1")
        user.save()
    return user


@pytest.fixture
def user2():
    user, created = User.objects.get_or_create(
        email="user2@gmail.com", password="user2user2"
    )
    if created:
        user.set_password("user1user1")
        user.save()
    return user


@pytest.fixture
def auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def auth_client2(user2):
    client = APIClient()
    refresh = RefreshToken.for_user(user2)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


class TestWalletApi:
    """Class for testing /wallets api"""

    @pytest.mark.django_db
    def test_wallets_get_post(self, auth_client):
        """Testing get and post requests"""

        unauth_client = APIClient()
        response = unauth_client.post("/wallets/")
        assert response.status_code == 401

        for currency, bonus in BONUSES.items():
            response = auth_client.post(
                "/wallets/",
                data={"type": "Visa", "currency": currency},
            )
            response_body = response.json()
            print(response_body)
            assert response.status_code == 201
            assert response_body["type"] == "Visa"
            assert response_body["currency"] == currency

        response = auth_client.get("/wallets/")
        response_body = response.json()
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_wallets_post_invalid_fields(self, auth_client):
        """If fields are invalid"""

        response = auth_client.post(
            "/wallets/",
            data={
                "type": "Chtototam",
                "currency": "USD",
            },
        )
        assert response.status_code == 400

        response = auth_client.post(
            "/wallets/",
            data={
                "type": "Mastercard",
                "currency": "Xxx",
            },
        )
        assert response.status_code == 400

    @pytest.mark.django_db
    def test_wallets_creation_more_then_allowed(self, auth_client2):
        """If user tries to create more wallets then he is allowed to"""
        data = {"type": "Visa", "currency": "USD"}

        for i in range(MAX_NUMBER_OF_WALLETS):
            response = auth_client2.post("/wallets/", data=data)

        try:
            auth_client2.post("/wallets/", data=data)
        except ValidationError:
            assert True

    @pytest.mark.django_db
    def test_wallet_method_not_allowed(self, auth_client):
        """Testing if PUT, PATCH are allowed"""

        response = auth_client.put("/wallets/")
        assert response.status_code == 405

        response = auth_client.patch("/wallets/")
        assert response.status_code == 405


class TestWalletDetailApi:
    """Class to test /wallets/<str:name> api"""

    data = {
        "name": "FBH7ESKD",
        "type": "Visa",
        "currency": "USD",
        "balance": "3.00",
    }

    @pytest.mark.django_db
    def test_wallets_detail_get(self, user, auth_client, auth_client2):
        """Testing permission to view details for wallet with specific name"""

        Wallet.objects.create(**self.data, owner=user)
        response = auth_client2.get("/wallets/FBH7ESKD/")
        assert response.status_code == 404

        response = auth_client.get("/wallets/FBH7ESKD/")
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_wallets_detail_delete(self, user, auth_client, auth_client2):
        """Testing permission to delete wallet with specific name"""

        Wallet.objects.create(**self.data, owner=user)

        response = auth_client2.delete("/wallets/FBH7ESKD/")
        assert response.status_code == 404

        response = auth_client.delete("/wallets/FBH7ESKD/")
        assert response.status_code == 204

    @pytest.mark.django_db
    def test_wallet_method_not_allowed(self, user, auth_client):
        """Testing if PUT, PATCH are not allowed"""

        Wallet.objects.create(**self.data, owner=user)

        response = auth_client.put("/wallets/FBH7ESKD/")
        assert response.status_code == 405

        response = auth_client.patch("/wallets/FBH7ESKD/")
        assert response.status_code == 405
