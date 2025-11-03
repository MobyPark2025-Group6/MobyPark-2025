import pytest
from unittest.mock import patch
from services.payment_service import PaymentService
from models.payment_models import PaymentCreate, PaymentRefund, PaymentUpdate

# ------------------------
# Sample Data
# ------------------------
sample_payment_data = [
    {
        "transaction": "PAY-123",
        "amount": 100.0,
        "initiator": "user1",
        "created_at": "28-10-2025 12:00:00",
        "completed": False,
        "hash": "HASH-1"
    },
    {
        "transaction": "PAY-456",
        "amount": 50.0,
        "initiator": "user2",
        "created_at": "28-10-2025 13:00:00",
        "completed": False,
        "hash": "HASH-2"
    }
]

# ------------------------
# Session Tests
# ------------------------
def test_get_session():
    assert PaymentService.get_session("admin-token")["role"] == "ADMIN"
    assert PaymentService.get_session("user-token")["role"] == "USER"
    assert PaymentService.get_session("invalid") is None

# ------------------------
# Payment Creation Tests
# ------------------------
@patch("services.payment_service.generate_payment_hash", return_value="PAY-FAKE")
@patch("services.payment_service.save_payment_data")
@patch("services.payment_service.load_payment_data", return_value=[])
def test_create_payment(mock_load, mock_save, mock_hash):
    session_user = {"username": "user1", "role": "USER"}
    payment = PaymentCreate(amount=50.0)
    result = PaymentService.create_payment(payment, session_user)

    assert result["initiator"] == "user1"
    assert result["amount"] == 50.0
    assert result["transaction"] == "PAY-FAKE"
    assert isinstance(result["created_at"], str)
    assert isinstance(result["hash"], str)
    mock_save.assert_called_once()

@patch("services.payment_service.generate_payment_hash", return_value="PAY-ZERO")
@patch("services.payment_service.save_payment_data")
@patch("services.payment_service.load_payment_data", return_value=[])
def test_create_payment_zero_amount(mock_load, mock_save, mock_hash):
    session_user = {"username": "user1", "role": "USER"}
    payment = PaymentCreate(amount=0.0)
    result = PaymentService.create_payment(payment, session_user)
    assert result["amount"] == 0.0
    assert result["transaction"] == "PAY-ZERO"

# ------------------------
# Payment Refund Tests
# ------------------------
@patch("services.payment_service.generate_payment_hash", return_value="PAY-REFUND")
@patch("services.payment_service.save_payment_data")
@patch("services.payment_service.load_payment_data", return_value=[])
def test_refund_payment(mock_load, mock_save, mock_hash):
    session_user = {"username": "admin", "role": "ADMIN"}
    refund = PaymentRefund(amount=30.0, coupled_to="PAY-123")
    result = PaymentService.refund_payment(refund, session_user)

    assert result["amount"] == -30.0
    assert result["processed_by"] == "admin"
    assert result["transaction"] == "PAY-REFUND"
    assert isinstance(result["created_at"], str)
    assert isinstance(result["hash"], str)
    mock_save.assert_called_once()

# ------------------------
# Payment Update Tests
# ------------------------
@patch("services.payment_service.load_payment_data", return_value=sample_payment_data.copy())
@patch("services.payment_service.save_payment_data")
def test_update_payment_success(mock_save, mock_load):
    update_data = PaymentUpdate(t_data={"note": "completed"}, validation="HASH-1")
    result = PaymentService.update_payment("PAY-123", update_data)

    assert result["completed"] is not False
    assert result["t_data"]["note"] == "completed"
    mock_save.assert_called_once()

@patch("services.payment_service.load_payment_data", return_value=[])
def test_update_payment_not_found(mock_load):
    update_data = PaymentUpdate(t_data={"note": "completed"}, validation="HASH-1")
    with pytest.raises(ValueError):
        PaymentService.update_payment("NON_EXISTENT", update_data)

@patch("services.payment_service.load_payment_data", return_value=sample_payment_data.copy())
def test_update_payment_invalid_validation(mock_load):
    update_data = PaymentUpdate(t_data={"note": "completed"}, validation="WRONG-HASH")
    with pytest.raises(PermissionError):
        PaymentService.update_payment("PAY-123", update_data)

# ------------------------
# Get User Payments Tests
# ------------------------
@patch("services.payment_service.load_payment_data", return_value=sample_payment_data.copy())
def test_get_user_payments(mock_load):
    result = PaymentService.get_user_payments("user1")
    assert len(result) == 1
    assert result[0]["initiator"] == "user1"

    result_empty = PaymentService.get_user_payments("nonexistent")
    assert result_empty == []

# ------------------------
# Get All User Payments Tests (Admin / Non-Admin)
# ------------------------
@patch("services.payment_service.load_payment_data", return_value=sample_payment_data.copy())
def test_get_all_user_payments_admin(mock_load):
    admin_session = {"username": "admin", "role": "ADMIN"}
    result = PaymentService.get_all_user_payments(admin_session, "user1")
    assert len(result) == 1

def test_get_all_user_payments_non_admin():
    user_session = {"username": "user1", "role": "USER"}
    with pytest.raises(PermissionError):
        PaymentService.get_all_user_payments(user_session, "user1")

# ------------------------
# Multiple Payments / Filtering
# ------------------------
@patch("services.payment_service.load_payment_data", return_value=sample_payment_data.copy())
def test_get_user_payments_multiple_users(mock_load):
    result_user1 = PaymentService.get_user_payments("user1")
    result_user2 = PaymentService.get_user_payments("user2")
    assert len(result_user1) == 1
    assert result_user1[0]["initiator"] == "user1"
    assert len(result_user2) == 1
    assert result_user2[0]["initiator"] == "user2"

# ------------------------
# Hash Generation Coverage (internal)
# ------------------------
@patch("services.payment_service.generate_payment_hash", return_value="PAY-HASH-MOCK")
@patch("services.payment_service.save_payment_data")
@patch("services.payment_service.load_payment_data", return_value=[])
def test_create_payment_hash(mock_load, mock_save, mock_hash):
    session_user = {"username": "user1", "role": "USER"}
    payment = PaymentCreate(amount=10.0)
    result = PaymentService.create_payment(payment, session_user)
    assert result["hash"] is not None
    assert result["transaction"] == "PAY-HASH-MOCK" 