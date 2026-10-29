"""Builds unique, throw-away user data for every test run.

Nothing here is a real credential: emails use the reserved example.com domain
and the password is generated randomly per user, so no secret is committed.
"""
import secrets
import uuid


class UserFactory:
    @staticmethod
    def build(**overrides):
        token = uuid.uuid4().hex[:10]
        user = {
            "title": "Mr",
            "name": f"qa_user_{token}",
            "email": f"qa_{token}@example.com",
            "password": f"Aa1!{secrets.token_hex(5)}",
            "birth_day": "10",
            "birth_month": "5",
            "birth_year": "1990",
            "first_name": "QA",
            "last_name": f"Tester{token[:4]}",
            "company": "QA Labs",
            "address1": "12 Test Street",
            "address2": "Suite 4",
            "country": "India",
            "state": "Tamil Nadu",
            "city": "Chennai",
            "zipcode": "600001",
            "mobile_number": "9876543210",
        }
        user.update(overrides)
        return user
