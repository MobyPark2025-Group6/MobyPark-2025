
from unittest.mock import Mock
import pytest
from fastapi import HTTPException, status

from services.reservation_service import ReservationService

@pytest.fixture
def mock_validation_service(mocker):
    """Fixture to provide mocked ValidationService"""
    return {
        'validate_token': mocker.patch('services.validation_service.ValidationService.validate_session_token'),
        'check_admin': mocker.patch('services.validation_service.ValidationService.check_valid_admin'),
        'check_employee': mocker.patch('services.validation_service.ValidationService.check_valid_employee')
    }

@pytest.fixture
def mock_storage_functions(mocker):
    """Fixture to provide mocked database functions"""
    save_reservation = mocker.patch('services.reservation_service.save_reservation')
    save_parking_lot = mocker.patch('services.reservation_service.save_parking_lot')
    return {
        'load_data': mocker.patch('services.reservation_service.load_data_db_table'),
        'get_item': mocker.patch('services.reservation_service.get_item_db'),
        'save_reservation': save_reservation,
        'save_parking_lot': save_parking_lot,
        'create_data': save_reservation.create_reservation,
        'change_data': save_parking_lot.change_plt,
        'delete_data': save_reservation.delete_reservation
    }

@pytest.fixture
def mock_datetime(mocker):
    """Fixture to mock datetime.now() for consistent timestamps"""
    mock_dt = mocker.patch('services.reservation_service.datetime')
    mock_dt.now.return_value.timestamp.return_value = 1234567890
    return mock_dt

@pytest.fixture
def sample_reservation_data():
    """Fixture providing sample ReservationRegister data"""
    return Mock(
        user_id="user123",
        lot_id="lot1",
        vehicle_id="vehicle1",
        start_time="2024-12-01T10:00:00",
        end_time="2024-12-01T12:00:00"
    )

@pytest.fixture
def existing_reservations():
    """Fixture providing existing reservations"""
    return [
        {
            "id": "1",
            "user_id": "user456",
            "lot_id": "lot1",
            "vehicle_id": "vehicle2",
            "start_time": "2024-12-01T14:00:00",
            "end_time": "2024-12-01T16:00:00",
            "created_at": 1234567800
        },
        {
            "id": "2",
            "user_id": "user789",
            "lot_id": "lot2",
            "vehicle_id": "vehicle3",
            "start_time": "2024-12-02T10:00:00",
            "end_time": "2024-12-02T12:00:00",
            "created_at": 1234567850
        }
    ]

@pytest.fixture
def mock_parking_lots():
    return {
        "lot1": {
            "id": "lot1",
            "name": "Lot 1",
            "capacity": 10,
            "reserved": 0
        }
    }

class TestCreateReservation:
    """Tests for ReservationService.create_reservation"""
    
    def test_user_creates_reservation_for_themselves(
        self,
        mock_validation_service,
        mock_storage_functions,
        mock_datetime,
        sample_reservation_data,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that a regular user can create a reservation for themselves"""
        token = "valid_token"
        user_id = "user123"
        
        # Setup load_data to return different data based on table
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return mock_parking_lots.copy()
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup validation mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_validation_service['check_employee'].return_value = False
        
        # Execute
        result = ReservationService.create_reservation(sample_reservation_data, token)
        
        # Assertions
        assert result["status"] == "Success"
        assert result["reservation"]["id"] == "3"  # len(existing) + 1
        assert result["reservation"]["user_id"] == user_id
        assert result["reservation"]["lot_id"] == "lot1"
        assert result["reservation"]["vehicle_id"] == "vehicle1"
        assert result["reservation"]["start_time"] == "2024-12-01T10:00:00"
        assert result["reservation"]["end_time"] == "2024-12-01T12:00:00"
        assert result["reservation"]["created_at"] == 1234567890
        
        # Verify create_data was called for reservation
        mock_storage_functions['create_data'].assert_called_once()
        create_args = mock_storage_functions['create_data'].call_args[0]
        assert create_args[0]["user_id"] == user_id
        
        # Verify change_data was called for parking lot
        mock_storage_functions['change_data'].assert_called_once()
        change_args = mock_storage_functions['change_data'].call_args[0]
        assert change_args[0]["reserved"] == 1  # Was 0, now 1
    
    def test_user_id_is_overwritten_for_non_admin(
        self,
        mock_validation_service,
        mock_storage_functions,
        mock_datetime,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that user_id is overwritten with session user for non-admins"""
        token = "valid_token"
        session_user_id = "user123"
        
        # Create reservation data with same user_id as session
        reservation_data = Mock(
            user_id=session_user_id,
            lot_id="lot1",
            vehicle_id="vehicle1",
            start_time="2024-12-01T10:00:00",
            end_time="2024-12-01T12:00:00"
        )
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return mock_parking_lots.copy()
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": session_user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute
        result = ReservationService.create_reservation(reservation_data, token)
        
        # Assertions - user_id should be the session user's id
        assert result["reservation"]["user_id"] == session_user_id
    
    def test_admin_can_create_reservation_for_other_users(
        self,
        mock_validation_service,
        mock_storage_functions,
        mock_datetime,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that an admin can create a reservation for any user"""
        token = "admin_token"
        admin_id = "admin123"
        target_user_id = "user456"
        
        # Create reservation data for another user
        reservation_data = Mock(
            user_id=target_user_id,
            lot_id="lot1",
            vehicle_id="vehicle1",
            start_time="2024-12-01T10:00:00",
            end_time="2024-12-01T12:00:00"
        )
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return mock_parking_lots.copy()
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks - admin user
        mock_validation_service['validate_token'].return_value = {
            "id": admin_id,
            "username": "admin"
        }
        mock_validation_service['check_admin'].return_value = True
        mock_validation_service['check_employee'].return_value = False
        
        # Execute
        result = ReservationService.create_reservation(reservation_data, token)
        
        # Assertions - user_id should remain as target_user_id
        assert result["reservation"]["user_id"] == target_user_id
    
    def test_non_admin_cannot_create_reservation_for_others(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that a regular user cannot create a reservation for another user"""
        token = "valid_token"
        session_user_id = "user123"
        other_user_id = "user456"
        
        # Create reservation data for another user
        reservation_data = Mock(
            user_id=other_user_id,  # Different from session user
            lot_id="lot1",
            vehicle_id="vehicle1",
            start_time="2024-12-01T10:00:00",
            end_time="2024-12-01T12:00:00"
        )
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return mock_parking_lots.copy()
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": session_user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_validation_service['check_employee'].return_value = False
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.create_reservation(reservation_data, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in exc_info.value.detail
        
        # Verify nothing was saved
        mock_storage_functions['create_data'].assert_not_called()
        mock_storage_functions['change_data'].assert_not_called()
    
    def test_first_reservation_gets_id_1(
        self,
        mock_validation_service,
        mock_storage_functions,
        mock_datetime,
        sample_reservation_data,
        mock_parking_lots
    ):
        """Test that the first reservation gets ID '1'"""
        token = "valid_token"
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return []
            elif table_name == "parking_lots":
                return mock_parking_lots.copy()
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks with empty reservations list
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute
        result = ReservationService.create_reservation(sample_reservation_data, token)
        
        # Assertions
        assert result["reservation"]["id"] == "1"
        
        # Verify create_data was called
        mock_storage_functions['create_data'].assert_called_once()
        create_args = mock_storage_functions['create_data'].call_args[0]
        assert create_args[0]["id"] == "1"
    
    def test_invalid_token_raises_exception(
        self,
        mock_validation_service,
        sample_reservation_data
    ):
        """Test that an invalid token raises an exception"""
        token = "invalid_token"
        
        # Mock ValidationService to raise exception
        mock_validation_service['validate_token'].side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.create_reservation(sample_reservation_data, token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_reservation_data_fields_are_preserved(
        self,
        mock_validation_service,
        mock_storage_functions,
        mock_datetime,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that all reservation data fields are correctly saved"""
        token = "valid_token"
        
        reservation_data = Mock(
            user_id="user123",
            lot_id="lot1",
            vehicle_id="special_vehicle",
            start_time="2025-01-15T08:30:00",
            end_time="2025-01-15T17:30:00"
        )
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return mock_parking_lots.copy()
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute
        result = ReservationService.create_reservation(reservation_data, token)
        
        # Assertions - verify all fields
        reservation = result["reservation"]
        assert reservation["lot_id"] == "lot1"
        assert reservation["vehicle_id"] == "special_vehicle"
        assert reservation["start_time"] == "2025-01-15T08:30:00"
        assert reservation["end_time"] == "2025-01-15T17:30:00"
    
    def test_created_at_timestamp_is_set(
        self,
        mock_validation_service,
        mock_storage_functions,
        mock_datetime,
        sample_reservation_data,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that created_at timestamp is properly set"""
        token = "valid_token"
        expected_timestamp = 1234567890
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return mock_parking_lots.copy()
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_datetime.now.return_value.timestamp.return_value = expected_timestamp
        
        # Execute
        result = ReservationService.create_reservation(sample_reservation_data, token)
        
        # Assertions
        assert result["reservation"]["created_at"] == expected_timestamp
        mock_datetime.now.assert_called_once()
    
    def test_reservations_list_is_properly_updated(
        self,
        mock_validation_service,
        mock_storage_functions,
        mock_datetime,
        sample_reservation_data,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that the new reservation is created with correct data"""
        token = "valid_token"
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return mock_parking_lots.copy()
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute
        result = ReservationService.create_reservation(sample_reservation_data, token)
        
        # Verify create_data was called with correct reservation
        create_args = mock_storage_functions['create_data'].call_args[0]
        assert create_args[0]["id"] == "3"
        assert create_args[0]["user_id"] == "user123"
    
    def test_parking_lot_not_found_raises_404(
        self,
        mock_validation_service,
        mock_storage_functions,
        sample_reservation_data
    ):
        """Test that referencing a non-existent parking lot raises 404"""
        token = "valid_token"
        
        def load_data_side_effect(table_name):
            if table_name == "parking_lots":
                return {}  # Empty parking lots
            return []
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.create_reservation(sample_reservation_data, token)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Parking lot not found" in exc_info.value.detail
    
    def test_full_parking_lot_raises_400(
        self,
        mock_validation_service,
        mock_storage_functions,
        sample_reservation_data
    ):
        """Test that attempting to reserve in a full parking lot raises 400"""
        token = "valid_token"
        
        # Create a full parking lot
        full_parking_lots = {
            "lot1": {
                "id": "lot1",
                "name": "Lot 1",
                "capacity": 5,
                "reserved": 5  # Full
            }
        }
        
        def load_data_side_effect(table_name):
            if table_name == "parking_lots":
                return full_parking_lots
            return []
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.create_reservation(sample_reservation_data, token)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "No available spots" in exc_info.value.detail
    
    def test_parking_lot_reserved_count_increments(
        self,
        mock_validation_service,
        mock_storage_functions,
        mock_datetime,
        sample_reservation_data,
        existing_reservations
    ):
        """Test that parking lot reserved count increments after reservation"""
        token = "valid_token"
        
        # Create parking lot with available space
        parking_lots = {
            "lot1": {
                "id": "lot1",
                "name": "Lot 1",
                "capacity": 10,
                "reserved": 3
            }
        }
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return parking_lots.copy()
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute
        result = ReservationService.create_reservation(sample_reservation_data, token)
        
        # Verify parking lot data was updated with incremented count
        mock_storage_functions['change_data'].assert_called_once()
        change_args = mock_storage_functions['change_data'].call_args[0]
        assert change_args[0]["reserved"] == 4  # Was 3, now 4
    
    def test_parking_lot_at_capacity_minus_one_allows_reservation(
        self,
        mock_validation_service,
        mock_storage_functions,
        mock_datetime,
        sample_reservation_data,
        existing_reservations
    ):
        """Test that a parking lot with one spot remaining allows reservation"""
        token = "valid_token"
        
        # Create parking lot with one spot remaining
        parking_lots = {
            "lot1": {
                "id": "lot1",
                "name": "Lot 1",
                "capacity": 10,
                "reserved": 9  # One spot left
            }
        }
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return parking_lots.copy()
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute
        result = ReservationService.create_reservation(sample_reservation_data, token)
        
        # Assertions - should succeed
        assert result["status"] == "Success"
        
        # Verify parking lot is now full
        change_args = mock_storage_functions['change_data'].call_args[0]
        assert change_args[0]["reserved"] == 10  # Now full

class TestGetReservationsList:
    """Tests for ReservationService.get_reservations_list"""

    def test_regular_user_can_access_own_reservations(
        self, 
        mock_validation_service, 
        mock_storage_functions
    ):
        """Test that a regular user can retrieve their own reservations"""
        user_id = "user123"
        token = "valid_token"
        
        reservations = [
            {"id": "1", "user_id": user_id, "lot_id": "lot1", "vehicle_id": "v1", "start_time": 1234567800, "end_time": 1234567900},
            {"id": "2", "user_id": "other_user", "lot_id": "lot1", "vehicle_id": "v2", "start_time": 1234567910, "end_time": 1234567950},
            {"id": "3", "user_id": user_id, "lot_id": "lot2", "vehicle_id": "v3", "start_time": 1234568000, "end_time": 1234568100}
        ]
        
        # Setup mock returns
        mock_validation_service["validate_token"].return_value = {"id": user_id, "username": "testuser"}
        mock_validation_service["check_admin"].return_value = False
        mock_validation_service["check_employee"].return_value = False
        mock_storage_functions['load_data'].return_value = reservations
        
        # Execute
        result = ReservationService.get_reservations_list(user_id, token)
        
        # Assertions
        assert len(result) == 2
        assert all(res.user_id == user_id for res in result)
        assert result[0].lot_id == "lot1"
        assert result[1].lot_id == "lot2"
        
        # Verify method calls
        mock_validation_service["validate_token"].assert_called_once_with(token)
        mock_storage_functions['load_data'].assert_called_once_with("reservations")
    
    def test_admin_can_access_any_user_reservations(
        self, 
        mock_validation_service, 
        mock_storage_functions
    ):
        """Test that an admin can retrieve any user's reservations"""
        admin_id = "admin123"
        target_user_id = "user456"
        token = "admin_token"
        
        reservations = [
            {"id": "res1", "user_id": target_user_id, "lot_id": "lot1", "vehicle_id": "v1", "start_time": 1234567800, "end_time": 1234567900},
            {"id": "res2", "user_id": "other_user", "lot_id": "lot2", "vehicle_id": "v2", "start_time": 1234567910, "end_time": 1234567950}
        ]
        
        # Setup - admin user
        mock_validation_service["validate_token"].return_value = {"id": admin_id, "username": "admin"}
        mock_validation_service["check_admin"].return_value = True
        mock_validation_service["check_employee"].return_value = False
        mock_storage_functions['load_data'].return_value = reservations
        
        # Execute
        result = ReservationService.get_reservations_list(target_user_id, token)
        
        # Assertions
        assert len(result) == 1
        assert result[0].user_id == target_user_id
    
    def test_regular_user_cannot_access_other_users_reservations(
        self, 
        mock_validation_service
    ):
        """Test that a regular user cannot access another user's reservations"""
        user_id = "user123"
        other_user_id = "user456"
        token = "valid_token"

        # Setup - regular user trying to access other user's data
        mock_validation_service["validate_token"].return_value = {"id": user_id, "username": "testuser"}
        mock_validation_service["check_admin"].return_value = False
        mock_validation_service["check_employee"].return_value = False
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservations_list(other_user_id, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Cannot access other user's reservations" in exc_info.value.detail
    
    def test_invalid_token_raises_exception(
        self, 
        mock_validation_service
    ):
        """Test that an invalid token raises an exception"""
        user_id = "user123"
        token = "invalid_token"
        
        mock_validation_service["validate_token"].side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservations_list(user_id, token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_user_with_no_reservations_returns_empty_list(
        self, 
        mock_validation_service, 
        mock_storage_functions
    ):
        """Test that a user with no reservations gets an empty list"""
        user_id = "user123"
        token = "valid_token"
        
        # Setup
        mock_validation_service["validate_token"].return_value = {"id": user_id, "username": "testuser"}
        mock_validation_service["check_admin"].return_value = False
        mock_validation_service["check_employee"].return_value = False
        mock_storage_functions['load_data'].return_value = [
            {"id": "res1", "user_id": "other_user", "table": "T1"}
        ]
        
        # Execute
        result = ReservationService.get_reservations_list(user_id, token)
        
        # Assertions
        assert len(result) == 0
    
    def test_token_user_mismatch_first_check(
        self, 
        mock_validation_service
    ):
        """Test the first authorization check catches token/user mismatch for non-admins"""
        requesting_user_id = "user123"
        target_user_id = "user456"
        token = "valid_token"

        # Setup - token belongs to different user, not admin
        mock_validation_service["validate_token"].return_value = {"id": requesting_user_id, "username": "testuser"}
        mock_validation_service["check_admin"].return_value = False
        mock_validation_service["check_employee"].return_value = False
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservations_list(target_user_id, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Cannot access other user's reservations" in exc_info.value.detail

class TestGetReservation:
    """Tests for ReservationService.get_reservation"""

    def test_user_can_access_own_reservation(
        self, 
        mock_validation_service, 
        mock_storage_functions,
        existing_reservations
    ):
        """Test that a user can retrieve their own reservation"""
        res_id = "1"
        token = "valid_token"
        user_id = "user456"
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id, 
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_validation_service['check_employee'].return_value = False
        mock_storage_functions['get_item'].return_value = [existing_reservations[0]]
        
        # Execute
        result = ReservationService.get_reservation(res_id, token)
        
        # Assertions
        assert result["id"] == res_id
        assert result["user_id"] == user_id
        assert result["lot_id"] == "lot1"
        
        # Verify mocks were called
        mock_validation_service['validate_token'].assert_called_once_with(token)
        mock_validation_service['check_admin'].assert_called_once()
    
    def test_admin_can_access_any_reservation(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations
    ):
        """Test that an admin can retrieve any user's reservation"""
        res_id = "1"
        token = "admin_token"
        admin_id = "admin123"
        
        # Setup mocks - admin user
        mock_validation_service['validate_token'].return_value = {
            "id": admin_id,
            "username": "admin"
        }
        mock_validation_service['check_admin'].return_value = True
        mock_validation_service['check_employee'].return_value = False
        mock_storage_functions['get_item'].return_value = [existing_reservations[0]]
        
        # Execute
        result = ReservationService.get_reservation(res_id, token)
        
        # Assertions
        assert result["id"] == res_id
        assert result["user_id"] == "user456"
        
        # Admin check should return True, so no further validation needed
        mock_validation_service['check_admin'].assert_called_once()
    
    def test_user_cannot_access_other_users_reservation(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations
    ):
        """Test that a regular user cannot access another user's reservation"""
        res_id = "1"  # This belongs to user456
        token = "valid_token"
        user_id = "user123"  # Different user
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_validation_service['check_employee'].return_value = False
        mock_storage_functions['get_item'].return_value = [existing_reservations[0]]
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in exc_info.value.detail
    
    def test_reservation_not_found_raises_404(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations
    ):
        """Test that requesting a non-existent reservation raises 404"""
        res_id = "nonexistent_res"
        token = "valid_token"
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_validation_service['check_employee'].return_value = False
        mock_storage_functions['get_item'].return_value = []
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Reservation not found" in exc_info.value.detail

    def test_invalid_token_raises_exception(
        self,
        mock_validation_service,
        mock_storage_functions
    ):
        """Test that an invalid token raises an exception"""
        res_id = "1"
        token = "invalid_token"
        
        # Mock ValidationService to raise exception
        mock_validation_service['validate_token'].side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token" in exc_info.value.detail

    def test_empty_reservations_list_raises_404(
        self,
        mock_validation_service,
        mock_storage_functions
    ):
        """Test that requesting a reservation when list is empty raises 404"""
        res_id = "1"
        token = "valid_token"
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_validation_service['check_employee'].return_value = False
        mock_storage_functions['get_item'].return_value = []
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

class TestDeleteReservation:
    """Tests for ReservationService.delete_reservation"""
    
    def test_user_deletes_own_reservation(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that a user can delete their own reservation"""
        token = "valid_token"
        user_id = "user456"
        res_id = "1"
        
        # Setup parking lot with reserved count
        parking_lots = mock_parking_lots.copy()
        parking_lots["lot1"]["reserved"] = 5
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return parking_lots
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute
        result = ReservationService.delete_reservation(res_id, token)
        
        # Assertions
        assert result["status"] == "Success"
        assert result["message"] == "Reservation deleted"
        
        # Verify delete_data was called
        mock_storage_functions['delete_data'].assert_called_once_with(res_id)
        
        # Verify parking lot reserved count was decremented
        mock_storage_functions['change_data'].assert_called_once()
        change_args = mock_storage_functions['change_data'].call_args[0]
        assert change_args[0]["reserved"] == 4  # Was 5, now 4

    def test_admin_deletes_any_reservation(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that an admin can delete any user's reservation"""
        token = "admin_token"
        admin_id = "admin123"
        res_id = "1"  # Belongs to user456, not admin
        
        parking_lots = mock_parking_lots.copy()
        parking_lots["lot1"]["reserved"] = 3
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return parking_lots
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": admin_id,
            "username": "admin"
        }
        mock_validation_service['check_admin'].return_value = True
        
        # Execute
        result = ReservationService.delete_reservation(res_id, token)
        
        # Assertions
        assert result["status"] == "Success"
        
        # Verify reservation was deleted
        mock_storage_functions['delete_data'].assert_called_once()

    def test_user_cannot_delete_others_reservation(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that a user cannot delete another user's reservation"""
        token = "valid_token"
        user_id = "user123"
        res_id = "1"  # Belongs to user456, not user123
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return mock_parking_lots.copy()
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "otheruser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_validation_service['check_employee'].return_value = False
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.delete_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in exc_info.value.detail
        
        # Verify nothing was deleted
        mock_storage_functions['delete_data'].assert_not_called()
        mock_storage_functions['change_data'].assert_not_called()

    def test_nonexistent_reservation_raises_404(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations
    ):
        """Test that deleting a non-existent reservation raises 404"""
        token = "valid_token"
        res_id = "999"  # Does not exist
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load_data'].return_value = existing_reservations.copy()
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.delete_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Reservation not found" in exc_info.value.detail
        
        # Verify nothing was deleted
        mock_storage_functions['delete_data'].assert_not_called()

    def test_invalid_token_raises_401(
        self,
        mock_validation_service
    ):
        """Test that an invalid token raises 401"""
        token = "invalid_token"
        res_id = "1"
        
        # Mock ValidationService to raise exception
        mock_validation_service['validate_token'].side_effect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.delete_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_parking_lot_reserved_decrements_correctly(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that parking lot reserved count decrements after deletion"""
        token = "valid_token"
        user_id = "user456"
        res_id = "1"
        
        # Setup parking lot with specific reserved count
        parking_lots = mock_parking_lots.copy()
        parking_lots["lot1"]["reserved"] = 7
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return parking_lots
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute
        result = ReservationService.delete_reservation(res_id, token)
        
        # Verify parking lot reserved count decremented
        change_args = mock_storage_functions['change_data'].call_args[0]
        assert change_args[0]["reserved"] == 6  # Was 7, now 6

    def test_parking_lot_not_found_still_deletes_reservation(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations
    ):
        """Test that reservation is deleted even if parking lot doesn't exist"""
        token = "valid_token"
        user_id = "user456"
        res_id = "1"
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return {}  # Empty
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks with empty parking lots
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute - should not raise exception
        result = ReservationService.delete_reservation(res_id, token)
        
        # Assertions
        assert result["status"] == "Success"
        
        # Verify reservation was still deleted
        mock_storage_functions['delete_data'].assert_called_once()

    def test_parking_lot_reserved_zero_does_not_go_negative(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations,
        mock_parking_lots
    ):
        """Test that parking lot reserved count doesn't go below zero"""
        token = "valid_token"
        user_id = "user456"
        res_id = "1"
        
        # Setup parking lot with zero reserved
        parking_lots = mock_parking_lots.copy()
        parking_lots["lot1"]["reserved"] = 0
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return existing_reservations.copy()
            elif table_name == "parking_lots":
                return parking_lots
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute
        result = ReservationService.delete_reservation(res_id, token)
        
        # Verify parking lot save was not called (reserved was already 0)
        mock_storage_functions['change_data'].assert_not_called()
        
        # But reservation should still be deleted
        mock_storage_functions['delete_data'].assert_called_once()

    def test_deleting_last_reservation_empties_list(
        self,
        mock_validation_service,
        mock_storage_functions,
        mock_parking_lots
    ):
        """Test that deleting the last reservation works correctly"""
        token = "valid_token"
        user_id = "user123"
        res_id = "1"
        
        # Only one reservation
        single_reservation = [
            {
                "id": "1",
                "user_id": "user123",
                "lot_id": "lot1",
                "vehicle_id": "vehicle1",
                "start_time": "2024-12-01T10:00:00",
                "end_time": "2024-12-01T12:00:00"
            }
        ]
        
        parking_lots = mock_parking_lots.copy()
        parking_lots["lot1"]["reserved"] = 1
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return single_reservation.copy()
            elif table_name == "parking_lots":
                return parking_lots
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute
        result = ReservationService.delete_reservation(res_id, token)
        
        # Verify deletion was called
        mock_storage_functions['delete_data'].assert_called_once()
        
        # Verify parking lot reserved count is now 0
        change_args = mock_storage_functions['change_data'].call_args[0]
        assert change_args[0]["reserved"] == 0

    def test_correct_reservation_removed_from_multiple(
        self,
        mock_validation_service,
        mock_storage_functions,
        mock_parking_lots
    ):
        """Test that the correct reservation is removed when multiple exist"""
        token = "valid_token"
        user_id = "user123"
        res_id = "2"  # Delete the middle one
        
        # Three reservations
        three_reservations = [
            {
                "id": "1",
                "user_id": "user123",
                "lot_id": "lot1",
                "vehicle_id": "vehicle1",
                "start_time": "2024-12-01T10:00:00",
                "end_time": "2024-12-01T12:00:00"
            },
            {
                "id": "2",
                "user_id": "user123",
                "lot_id": "lot1",
                "vehicle_id": "vehicle2",
                "start_time": "2024-12-02T10:00:00",
                "end_time": "2024-12-02T12:00:00"
            },
            {
                "id": "3",
                "user_id": "user123",
                "lot_id": "lot2",
                "vehicle_id": "vehicle3",
                "start_time": "2024-12-03T10:00:00",
                "end_time": "2024-12-03T12:00:00"
            }
        ]
        
        parking_lots = mock_parking_lots.copy()
        parking_lots["lot1"]["reserved"] = 2
        parking_lots["lot2"] = {
            "id": "lot2",
            "name": "Lot 2",
            "capacity": 10,
            "reserved": 1
        }
        
        def load_data_side_effect(table_name):
            if table_name == "reservations":
                return three_reservations.copy()
            elif table_name == "parking_lots":
                return parking_lots
            return {}
        
        mock_storage_functions['load_data'].side_effect = load_data_side_effect
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Execute
        result = ReservationService.delete_reservation(res_id, token)
        
        # Verify correct reservation was deleted
        mock_storage_functions['delete_data'].assert_called_once_with("2")
        
        # Verify correct parking lot was updated
        change_args = mock_storage_functions['change_data'].call_args[0]
        assert change_args[0]["reserved"] == 1