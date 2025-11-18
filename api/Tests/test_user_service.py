import pytest
from unittest.mock import patch
from fastapi import HTTPException

from services.user_service import UserService
from models.user_models import UserRegister, UserLogin, User


# ------------------------
# Sample/mock data
# ------------------------
def make_hashed_user(username="testuser", password="testpassword", uid="1"):
    hashed = UserService.hash_password(password)
    return {
        "id": uid,
        "username": username,
        "password": hashed,
        "name": "Test User",
        "email": "test.user@example.com",
        "phone": "123",
        "role": "USER",
        "created_at": "2025-01-01",
        "birth_year": 1990,
        "active": True,
    }


# ------------------------
# Existence and creation
# ------------------------
@patch("services.user_service.load_json", return_value=[])
@patch("services.user_service.save_user_data")
def test_create_user_success(mock_save, mock_load):
    user = UserRegister(username="newuser", password="pw", name="New User", email="n@example.com")
    res = UserService.create_user(user)
    assert res.message == "User created successfully"
    mock_save.assert_called_once()


@patch("services.user_service.load_json", return_value=[make_hashed_user(username="existing")])
def test_create_user_conflict(mock_load):
    user = UserRegister(username="existing", password="pw", name="Existing")
    with pytest.raises(HTTPException):
        UserService.create_user(user)


# ------------------------
# Authentication
# ------------------------
@patch("services.user_service.add_session")
@patch("services.user_service.load_json", return_value=[make_hashed_user(username="loginuser", password="secret")])
def test_authenticate_user_success(mock_load, mock_add_session):
    creds = UserLogin(username="loginuser", password="secret")
    resp = UserService.authenticate_user(creds)
    assert resp.message == "User logged in successfully"
    assert isinstance(resp.session_token, str)
    assert len(resp.session_token) > 0
    mock_add_session.assert_called_once()


@patch("services.user_service.load_json", return_value=[])
def test_authenticate_user_invalid(mock_load):
    creds = UserLogin(username="noone", password="bad")
    with pytest.raises(HTTPException):
        UserService.authenticate_user(creds)


# ------------------------
# Read / Update / Delete
# ------------------------
@patch("services.user_service.load_json", return_value=[make_hashed_user(username="readme")])
def test_get_user_by_username(mock_load):
    u = UserService.get_user_by_username("readme")
    assert u is not None
    assert u["username"] == "readme"
    assert u["email"] is not None


@patch("services.user_service.load_json", return_value=[make_hashed_user(username="upduser")])
@patch("services.user_service.save_user_data")
def test_update_user_success(mock_save, mock_load):
    # the update_user in service expects a model with a username attribute
    user_data = User(username="upduser", name="Updated", email="u@example.com")
    res = UserService.update_user(user_data)
    assert res.message == "User updated successfully"
    mock_save.assert_called_once()


@patch("services.user_service.load_json", return_value=[])
def test_update_user_not_found(mock_load):
    user_data = User(username="nope", name="X", email="x@example.com")
    with pytest.raises(HTTPException):
        UserService.update_user(user_data)


@patch("services.user_service.load_json", return_value=[make_hashed_user(username="deluser")])
@patch("services.user_service.save_user_data")
def test_delete_user_success(mock_save, mock_load):
    res = UserService.delete_user("deluser")
    assert res.message == "User deleted successfully"
    mock_save.assert_called_once()


@patch("services.user_service.load_json", return_value=[])
def test_delete_user_not_found(mock_load):
    with pytest.raises(HTTPException):
        UserService.delete_user("missing")
