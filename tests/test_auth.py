import pytest
from rest_framework.test import APIClient

test_data = {"email": "user1@gmail.com", "password": "string11111"}

invalid_data = {"email": "user2", "password": "string22222"}


@pytest.mark.django_db
def test_create_user(client):
    """Testing post request /auth/users/"""
    response = client.post("/auth/users/", data=test_data)
    response_body = response.json()
    assert response.status_code == 201
    assert response_body["email"] == "user1@gmail.com"
    assert response_body["id"] != "1"


@pytest.mark.django_db
def test_invalid_email(client):
    """Testing emptyinvalid email /auth/users/"""
    response = client.post("/auth/users/", data=invalid_data)
    response_body = response.json()
    assert response.status_code == 400
    assert response_body["email"] == ["Enter a valid email address."]
