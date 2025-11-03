import pytest
from fastapi import HTTPException, status

from services.reservation_service import ReservationService

class TestGetReservationsList:
    """Tests for ReservationService.get_reservations_list"""
    
    def test_regular_user_can_access_own_reservations(self, mocker):
        """Test that a regular user can retrieve their own reservations"""
        user_id = "user123"
        token = "valid_token"
        
        # Mock ValidationService methods
        mock_validate = mocker.patch('services.validation_service.ValidationService.validate_session_token')
        mock_check_admin = mocker.patch('services.validation_service.ValidationService.check_valid_admin')
        mock_load_data = mocker.patch('services.reservation_service.load_reservation_data')
        
        # Setup mock returns
        mock_validate.return_value = {"id": user_id, "username": "testuser"}
        mock_check_admin.return_value = False
        mock_load_data.return_value = [
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
        mock_validate.assert_called_once_with(token)
        mock_load_data.assert_called_once()
    
    
#     def test_admin_can_access_any_user_reservations(self, mocker):
#         """Test that an admin can retrieve any user's reservations"""
#         admin_id = "admin123"
#         target_user_id = "user456"
#         token = "admin_token"
        
#         # Mock ValidationService methods
#         mock_validate = mocker.patch('ValidationService.validate_session_token')
#         mock_check_admin = mocker.patch('ValidationService.check_valid_admin')
#         mock_load_data = mocker.patch('load_reservation_data')
        
#         # Setup - admin user
#         mock_validate.return_value = {"id": admin_id, "username": "admin"}
#         mock_check_admin.return_value = True
#         mock_load_data.return_value = [
#             {"id": "res1", "user_id": target_user_id, "table": "T1"},
#             {"id": "res2", "user_id": "other_user", "table": "T2"}
#         ]
        
#         # Execute
#         result = ReservationService.get_reservations_list(target_user_id, token)
        
#         # Assertions
#         assert len(result["reservations"]) == 1
#         assert result["reservations"][0]["user_id"] == target_user_id
        
#         # Admin check should only be called once in first condition
#         mock_check_admin.assert_called_once()
    
#     def test_regular_user_cannot_access_other_users_reservations(self, mocker):
#         """Test that a regular user cannot access another user's reservations"""
#         user_id = "user123"
#         other_user_id = "user456"
#         token = "valid_token"
        
#         # Mock ValidationService methods
#         mock_validate = mocker.patch('ValidationService.validate_session_token')
#         mock_check_admin = mocker.patch('ValidationService.check_valid_admin')
        
#         # Setup - regular user trying to access other user's data
#         mock_validate.return_value = {"id": user_id, "username": "testuser"}
#         mock_check_admin.return_value = False
        
#         # Execute & Assert
#         with pytest.raises(HTTPException) as exc_info:
#             ReservationService.get_reservations_list(other_user_id, token)
        
#         assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
#         assert "Cannot access other user's reservations" in exc_info.value.detail
    
#     def test_invalid_token_raises_exception(self, mocker):
#         """Test that an invalid token raises an exception"""
#         user_id = "user123"
#         token = "invalid_token"
        
#         # Mock ValidationService to raise exception
#         mock_validate = mocker.patch('ValidationService.validate_session_token')
#         mock_validate.side_effect = HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token"
#         )
        
#         # Execute & Assert
#         with pytest.raises(HTTPException) as exc_info:
#             ReservationService.get_reservations_list(user_id, token)
        
#         assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
#     def test_user_with_no_reservations_returns_empty_list(self, mocker):
#         """Test that a user with no reservations gets an empty list"""
#         user_id = "user123"
#         token = "valid_token"
        
#         # Mock ValidationService methods
#         mock_validate = mocker.patch('ValidationService.validate_session_token')
#         mock_check_admin = mocker.patch('ValidationService.check_valid_admin')
#         mock_load_data = mocker.patch('load_reservation_data')
        
#         # Setup
#         mock_validate.return_value = {"id": user_id, "username": "testuser"}
#         mock_check_admin.return_value = False
#         mock_load_data.return_value = [
#             {"id": "res1", "user_id": "other_user", "table": "T1"}
#         ]
        
#         # Execute
#         result = ReservationService.get_reservations_list(user_id, token)
        
#         # Assertions
#         assert result["reservations"] == []
    
#     def test_token_user_mismatch_first_check(self, mocker):
#         """Test the first authorization check catches token/user mismatch for non-admins"""
#         requesting_user_id = "user123"
#         target_user_id = "user456"
#         token = "valid_token"
        
#         # Mock ValidationService methods
#         mock_validate = mocker.patch('ValidationService.validate_session_token')
#         mock_check_admin = mocker.patch('ValidationService.check_valid_admin')
        
#         # Setup - token belongs to different user, not admin
#         mock_validate.return_value = {"id": requesting_user_id, "username": "testuser"}
#         mock_check_admin.return_value = False
        
#         # Execute & Assert
#         with pytest.raises(HTTPException) as exc_info:
#             ReservationService.get_reservations_list(target_user_id, token)
        
#         assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
#         assert "Cannot access other user's reservations" in exc_info.value.detail


# # Example of how to use fixtures for common setup
# @pytest.fixture
# def mock_validation_service(mocker):
#     """Fixture to provide mocked ValidationService"""
#     return {
#         'validate_token': mocker.patch('ValidationService.validate_session_token'),
#         'check_admin': mocker.patch('ValidationService.check_valid_admin')
#     }

# @pytest.fixture
# def mock_load_reservation_data(mocker):
#     """Fixture to provide mocked load_reservation_data"""
#     return mocker.patch('load_reservation_data')


# # Alternative test using fixtures
# def test_with_fixtures(mock_validation_service, mock_load_reservation_data):
#     """Example test using fixtures for cleaner setup"""
#     user_id = "user123"
#     token = "valid_token"
    
#     mock_validation_service['validate_token'].return_value = {"id": user_id}
#     mock_validation_service['check_admin'].return_value = False
#     mock_load_reservation_data.return_value = [
#         {"id": "res1", "user_id": user_id, "table": "T1"}
#     ]
    
#     result = ReservationService.get_reservations_list(user_id, token)
    
#     assert len(result["reservations"]) == 1