from unittest.mock import Mock
import pytest
from fastapi import HTTPException, status

from services.reservation_service import ReservationService

@pytest.fixture
def mock_validation_service(mocker):
    """Fixture to provide mocked ValidationService"""
    return {
        'validate_token': mocker.patch('services.validation_service.ValidationService.validate_session_token'),
        'check_admin': mocker.patch('services.validation_service.ValidationService.check_valid_admin')
    }

@pytest.fixture
def mock_load_reservation_data(mocker):
    """Fixture to provide mocked load_reservation_data"""
    return mocker.patch('services.reservation_service.load_reservation_data')

@pytest.fixture
def mock_storage_functions(mocker):
    """Fixture to provide mocked storage functions"""
    return {
        'load': mocker.patch('services.reservation_service.load_reservation_data'),
        'save': mocker.patch('services.reservation_service.save_reservation_data')
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
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load_reservation'].return_value = existing_reservations.copy()
        mock_storage_functions['load_parking_lot'].return_value = mock_parking_lots.copy()
        
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
        
        # Verify save was called with updated list
        mock_storage_functions['save_reservation'].assert_called_once()
        saved_data = mock_storage_functions['save_reservation'].call_args[0][0]
        assert len(saved_data) == 3
        assert saved_data[-1]["id"] == "3"
        
        # Verify parking lot reserved count was incremented
        mock_storage_functions['save_parking_lot'].assert_called_once()
        saved_lots = mock_storage_functions['save_parking_lot'].call_args[0][0]
        assert saved_lots["lot1"]["reserved"] == 1  # Was 0, now 1
    
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
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": session_user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load_reservation'].return_value = existing_reservations.copy()
        mock_storage_functions['load_parking_lot'].return_value = mock_parking_lots.copy()
        
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
        
        # Setup mocks - admin user
        mock_validation_service['validate_token'].return_value = {
            "id": admin_id,
            "username": "admin"
        }
        mock_validation_service['check_admin'].return_value = True
        mock_storage_functions['load_reservation'].return_value = existing_reservations.copy()
        mock_storage_functions['load_parking_lot'].return_value = mock_parking_lots.copy()
        
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
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": session_user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load_reservation'].return_value = existing_reservations.copy()
        mock_storage_functions['load_parking_lot'].return_value = mock_parking_lots.copy()
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.create_reservation(reservation_data, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in exc_info.value.detail
        
        # Verify save was NOT called
        mock_storage_functions['save_reservation'].assert_not_called()
        mock_storage_functions['save_parking_lot'].assert_not_called()
    
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
        
        # Setup mocks with empty reservations list
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load_reservation'].return_value = []
        mock_storage_functions['load_parking_lot'].return_value = mock_parking_lots.copy()
        
        # Execute
        result = ReservationService.create_reservation(sample_reservation_data, token)
        
        # Assertions
        assert result["reservation"]["id"] == "1"
        
        # Verify save was called with list containing 1 item
        saved_data = mock_storage_functions['save_reservation'].call_args[0][0]
        assert len(saved_data) == 1
    
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
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load_reservation'].return_value = existing_reservations.copy()
        mock_storage_functions['load_parking_lot'].return_value = mock_parking_lots.copy()
        
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
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load_reservation'].return_value = existing_reservations.copy()
        mock_storage_functions['load_parking_lot'].return_value = mock_parking_lots.copy()
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
        """Test that the new reservation is appended to existing reservations"""
        token = "valid_token"
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        
        # Use a copy to verify original list is modified
        reservations_copy = existing_reservations.copy()
        mock_storage_functions['load_reservation'].return_value = reservations_copy
        mock_storage_functions['load_parking_lot'].return_value = mock_parking_lots.copy()
        
        # Execute
        result = ReservationService.create_reservation(sample_reservation_data, token)
        
        # Verify save was called with the modified list
        saved_data = mock_storage_functions['save_reservation'].call_args[0][0]
        
        # Check that all original reservations are still there
        assert saved_data[0]["id"] == "1"
        assert saved_data[1]["id"] == "2"
        
        # Check that new reservation is appended
        assert saved_data[2]["id"] == "3"
        assert saved_data[2]["user_id"] == "user123"
        assert len(saved_data) == 3
    
    def test_parking_lot_not_found_raises_404(
        self,
        mock_validation_service,
        mock_storage_functions,
        sample_reservation_data
    ):
        """Test that referencing a non-existent parking lot raises 404"""
        token = "valid_token"
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load_parking_lot'].return_value = {}  # Empty parking lots
        
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
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load_parking_lot'].return_value = full_parking_lots
        
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
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load_reservation'].return_value = existing_reservations.copy()
        mock_storage_functions['load_parking_lot'].return_value = parking_lots.copy()
        
        # Execute
        result = ReservationService.create_reservation(sample_reservation_data, token)
        
        # Verify parking lot data was saved with incremented count
        mock_storage_functions['save_parking_lot'].assert_called_once()
        saved_lots = mock_storage_functions['save_parking_lot'].call_args[0][0]
        assert saved_lots["lot1"]["reserved"] == 4  # Was 3, now 4
    
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
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load_reservation'].return_value = existing_reservations.copy()
        mock_storage_functions['load_parking_lot'].return_value = parking_lots.copy()
        
        # Execute
        result = ReservationService.create_reservation(sample_reservation_data, token)
        
        # Assertions - should succeed
        assert result["status"] == "Success"
        
        # Verify parking lot is now full
        saved_lots = mock_storage_functions['save_parking_lot'].call_args[0][0]
        assert saved_lots["lot1"]["reserved"] == 10  # Now full

class TestGetReservationsList:
    """Tests for ReservationService.get_reservations_list"""

    def test_regular_user_can_access_own_reservations(self, mock_validation_service, mock_load_reservation_data):
        """Test that a regular user can retrieve their own reservations"""
        user_id = "user123"
        token = "valid_token"
        
        # Setup mock returns
        mock_validation_service["validate_token"].return_value = {"id": user_id, "username": "testuser"}
        mock_validation_service["check_admin"].return_value = False
        mock_load_reservation_data.return_value = [
            {"id": "1", "user_id": user_id, "table": "T1"},
            {"id": "2", "user_id": "other_user", "table": "T2"},
            {"id": "3", "user_id": user_id, "table": "T3"}
        ]
        
        # Execute
        result = ReservationService.get_reservations_list(user_id, token)
        
        # Assertions
        assert len(result["reservations"]) == 2
        assert all(res["user_id"] == user_id for res in result["reservations"])
        assert result["reservations"][0]["id"] == "1"
        assert result["reservations"][1]["id"] == "3"
        
        # Verify method calls
        mock_validation_service["validate_token"].assert_called_once_with(token)
        mock_load_reservation_data.assert_called_once()
    
    
    def test_admin_can_access_any_user_reservations(self, mock_validation_service, mock_load_reservation_data):
        """Test that an admin can retrieve any user's reservations"""
        admin_id = "admin123"
        target_user_id = "user456"
        token = "admin_token"
                
        # Setup - admin user
        mock_validation_service["validate_token"].return_value = {"id": admin_id, "username": "admin"}
        mock_validation_service["check_admin"].return_value = True
        mock_load_reservation_data.return_value = [
            {"id": "res1", "user_id": target_user_id, "table": "T1"},
            {"id": "res2", "user_id": "other_user", "table": "T2"}
        ]
        
        # Execute
        result = ReservationService.get_reservations_list(target_user_id, token)
        
        # Assertions
        assert len(result["reservations"]) == 1
        assert result["reservations"][0]["user_id"] == target_user_id
    
    def test_regular_user_cannot_access_other_users_reservations(self, mock_validation_service):
        """Test that a regular user cannot access another user's reservations"""
        user_id = "user123"
        other_user_id = "user456"
        token = "valid_token"

        # Setup - regular user trying to access other user's data
        mock_validation_service["validate_token"].return_value = {"id": user_id, "username": "testuser"}
        mock_validation_service["check_admin"].return_value = False
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservations_list(other_user_id, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Cannot access other user's reservations" in exc_info.value.detail
    
    def test_invalid_token_raises_exception(self, mock_validation_service):
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
    
    def test_user_with_no_reservations_returns_empty_list(self, mock_validation_service, mock_load_reservation_data):
        """Test that a user with no reservations gets an empty list"""
        user_id = "user123"
        token = "valid_token"
        
        # Setup
        mock_validation_service["validate_token"].return_value = {"id": user_id, "username": "testuser"}
        mock_validation_service["check_admin"].return_value = False
        mock_load_reservation_data.return_value = [
            {"id": "res1", "user_id": "other_user", "table": "T1"}
        ]
        
        # Execute
        result = ReservationService.get_reservations_list(user_id, token)
        
        # Assertions
        assert result["reservations"] == []
    
    def test_token_user_mismatch_first_check(self, mock_validation_service):
        """Test the first authorization check catches token/user mismatch for non-admins"""
        requesting_user_id = "user123"
        target_user_id = "user456"
        token = "valid_token"

        # Setup - token belongs to different user, not admin
        mock_validation_service["validate_token"].return_value = {"id": requesting_user_id, "username": "testuser"}
        mock_validation_service["check_admin"].return_value = False
        
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
        mock_load_reservation_data, 
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
        mock_load_reservation_data.return_value = existing_reservations
        
        # Execute
        result = ReservationService.get_reservation(res_id, token)
        
        # Assertions
        assert result["reservation"]["id"] == res_id
        assert result["reservation"]["user_id"] == user_id
        assert result["reservation"]["lot_id"] == "lot1"
        
        # Verify mocks were called
        mock_validation_service['validate_token'].assert_called_once_with(token)
        mock_validation_service['check_admin'].assert_called_once()
        mock_load_reservation_data.assert_called_once()
    
    def test_admin_can_access_any_reservation(
        self,
        mock_validation_service,
        mock_load_reservation_data,
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
        mock_load_reservation_data.return_value = existing_reservations
        
        # Execute
        result = ReservationService.get_reservation(res_id, token)
        
        # Assertions
        assert result["reservation"]["id"] == res_id
        assert result["reservation"]["user_id"] == "user456"
        
        # Admin check should return True, so no further validation needed
        mock_validation_service['check_admin'].assert_called_once()
    
    def test_user_cannot_access_other_users_reservation(
        self,
        mock_validation_service,
        mock_load_reservation_data,
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
        mock_load_reservation_data.return_value = existing_reservations
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in exc_info.value.detail
    
    def test_reservation_not_found_raises_404(
        self,
        mock_validation_service,
        mock_load_reservation_data,
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
        mock_load_reservation_data.return_value = existing_reservations
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Reservation not found" in exc_info.value.detail
    
    def test_invalid_token_raises_exception(
        self,
        mock_validation_service,
        mock_load_reservation_data
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
        mock_load_reservation_data
    ):
        """Test that requesting a reservation when list is empty raises 404"""
        res_id = "1"
        token = "valid_token"
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_load_reservation_data.return_value = []
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

class TestDeleteReservation:
    """Tests for ReservationService.delete_reservation"""
    def test_user_can_delete_own_reservation(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations
    ):
        """Test that a user can delete their own reservation"""
        res_id = "1"
        token = "valid_token"
        user_id = "user456"
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load'].return_value = existing_reservations.copy()
        
        # Execute
        result = ReservationService.delete_reservation(res_id, token)
        
        # Assertions
        assert result["status"] == "Success"
        
        # Verify that the reservation was removed
        mock_storage_functions['save'].assert_called_once()
        saved_data = mock_storage_functions['save'].call_args[0][0]
        assert all(res["id"] != res_id for res in saved_data)
        assert len(saved_data) == len(existing_reservations) - 1
    
    def test_admin_can_delete_any_reservation(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations
    ):
        """Test that an admin can delete any user's reservation"""
        res_id = "1"
        token = "admin_token"
        admin_id = "admin123"
        
        # Setup mocks - admin user
        mock_validation_service['validate_token'].return_value = {
            "id": admin_id,
            "username": "admin"
        }
        mock_validation_service['check_admin'].return_value = True
        mock_storage_functions['load'].return_value = existing_reservations.copy()
        
        # Execute
        result = ReservationService.delete_reservation(res_id, token)
        
        # Assertions
        assert result["status"] == "Success"
        
        # Verify that the reservation was removed
        mock_storage_functions['save'].assert_called_once()
        saved_data = mock_storage_functions['save'].call_args[0][0]
        assert all(res["id"] != res_id for res in saved_data)
        assert len(saved_data) == len(existing_reservations) - 1
    
    def test_user_cannot_delete_other_users_reservation(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations
    ):
        """Test that a regular user cannot delete another user's reservation"""
        res_id = "1"  # This belongs to user456
        token = "valid_token"
        user_id = "user123"  # Different user
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_storage_functions['load'].return_value = existing_reservations.copy()
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.delete_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in exc_info.value.detail
        
        # Verify save was NOT called
        mock_storage_functions['save'].assert_not_called()

    def test_reservation_not_found_raises_404(
        self,
        mock_validation_service,
        mock_storage_functions,
        existing_reservations
    ):
        """Test that deleting a non-existent reservation raises 404"""
        res_id = "nonexistent_res"
        token = "valid_token"
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_storage_functions['load'].return_value = existing_reservations.copy()
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.delete_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Reservation not found" in exc_info.value.detail
        
        # Verify save was NOT called
        mock_storage_functions['save'].assert_not_called()

    