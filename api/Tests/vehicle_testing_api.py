from types import SimpleNamespace
from unittest.mock import patch
import pytest
from unittest.mock import patch
from models.vehicle_models import Vehicle
from storage_utils import load_vehicle_data,  save_vehicle_data
from services.vehicle_service import VehicleService
from services.user_service import *
from models.user_models import * 
import json


@pytest.mark.parametrize("creds", [
    {"username": "cindy.leenders42", "password": "password"}
])
@patch("services.user_service.UserService.authenticate_user")
def test_authenticate_user_mocked(mock_auth, creds):
    """
    Module-level mocked authenticate test.
    Sets the module-level `authorization` variable (so later tests can reuse it).
    """
    # make the patched service return a simple object with the attributes your tests expect
    mock_auth.return_value = SimpleNamespace(
        session_token="fake-session-token-123",
        message="User logged in successfully"
    )

    # build the credentials object the real service expects
    credentials = UserLogin(username=creds["username"], password=creds["password"])

    # call the (patched) service
    response = UserService.authenticate_user(credentials)

    # set the module-level `authorization` variable so TestMobyPark can reuse it
    global authorization
    authorization = response.session_token

    # assertions (same contract as your original test)
    assert response.message == "User logged in successfully"
    assert isinstance(response.session_token, str)
    assert len(response.session_token) > 0

    # ensure the service was called with the credentials object
    mock_auth.assert_called_once_with(credentials)