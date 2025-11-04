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
def sample_reservations():
    """Fixture providing sample reservation data"""
    return [
        {
            "id": "res1",
            "user_id": "user123",
            "table": "T1",
            "date": "2024-12-01",
            "time": "18:00"
        },
        {
            "id": "res2",
            "user_id": "user456",
            "table": "T2",
            "date": "2024-12-02",
            "time": "19:00"
        },
        {
            "id": "res3",
            "user_id": "user123",
            "table": "T3",
            "date": "2024-12-03",
            "time": "20:00"
        }
    ]

class TestGetReservationsList:
    """Tests for ReservationService.get_reservations_list"""

    def test_regular_user_can_access_own_reservations(self, mock_validation_service, mock_load_reservation_data):
        """Test that a regular user can retrieve their own reservations"""
        user_id = "user123"
        token = "valid_token"
        
        # Mock ValidationService methods
        # mock_validation_service["validate_token"] = mocker.patch('services.validation_service.ValidationService.validate_session_token')
        # mock_validation_service["check_admin"] = mocker.patch('services.validation_service.ValidationService.check_valid_admin')
        # mock_load_data = mocker.patch('services.reservation_service.load_reservation_data')
        
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
        sample_reservations
    ):
        """Test that a user can retrieve their own reservation"""
        res_id = "res1"
        token = "valid_token"
        user_id = "user123"
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id, 
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_load_reservation_data.return_value = sample_reservations
        
        # Execute
        result = ReservationService.get_reservation(res_id, token)
        
        # Assertions
        assert result["reservation"]["id"] == res_id
        assert result["reservation"]["user_id"] == user_id
        assert result["reservation"]["table"] == "T1"
        
        # Verify mocks were called
        mock_validation_service['validate_token'].assert_called_once_with(token)
        mock_validation_service['check_admin'].assert_called_once()
        mock_load_reservation_data.assert_called_once()
    
    def test_admin_can_access_any_reservation(
        self,
        mock_validation_service,
        mock_load_reservation_data,
        sample_reservations
    ):
        """Test that an admin can retrieve any user's reservation"""
        res_id = "res2"
        token = "admin_token"
        admin_id = "admin123"
        
        # Setup mocks - admin user
        mock_validation_service['validate_token'].return_value = {
            "id": admin_id,
            "username": "admin"
        }
        mock_validation_service['check_admin'].return_value = True
        mock_load_reservation_data.return_value = sample_reservations
        
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
        sample_reservations
    ):
        """Test that a regular user cannot access another user's reservation"""
        res_id = "res2"  # This belongs to user456
        token = "valid_token"
        user_id = "user123"  # Different user
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": user_id,
            "username": "testuser"
        }
        mock_validation_service['check_admin'].return_value = False
        mock_load_reservation_data.return_value = sample_reservations
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReservationService.get_reservation(res_id, token)
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in exc_info.value.detail
    
    def test_reservation_not_found_raises_404(
        self,
        mock_validation_service,
        mock_load_reservation_data,
        sample_reservations
    ):
        """Test that requesting a non-existent reservation raises 404"""
        res_id = "nonexistent_res"
        token = "valid_token"
        
        # Setup mocks
        mock_validation_service['validate_token'].return_value = {
            "id": "user123",
            "username": "testuser"
        }
        mock_load_reservation_data.return_value = sample_reservations
        
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
        res_id = "res1"
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
        res_id = "res1"
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