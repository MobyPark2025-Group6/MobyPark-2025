import pytest
from unittest.mock import patch
from models.vehicle_models import Vehicle
from storage_utils import load_vehicle_data,  save_vehicle_data
from services.vehicle_service import VehicleService
from services.user_service import *
from models.user_models import * 
import json


authorization = None 

if __name__ == '__main__':
    pytest.main()