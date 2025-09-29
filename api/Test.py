import unittest
from unittest import TestCase
import requests

class MobyParkTesting(unittest.TestCase):
    def test_login(self):
        result = requests.post(
            "http://localhost:8000/login",
            json={
                "username": "cindy.leenders42",
                "password": "password",
            },
        )
        assert result.status_code == 200


if __name__ == '__main__':
    unittest.main()
