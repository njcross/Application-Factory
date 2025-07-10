# tests/conftest.py
from datetime import datetime, timedelta, timezone
from jose import jwt
from app import create_app
from app.extensions import SECRET_KEY
from app.models import Customers, Mechanics, db 


def generate_token(customer_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(customer_id)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def get_test_client():
    app = create_app('TestingConfig')  # Make sure this uses a test DB
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Optional: Add test customer and mechanic
        customer = Customers(name="Test User", email="test@example.com", phone="1234567890")
        customer.set_password("password")
        db.session.add(customer)

        mechanic = Mechanics(name="Test Mechanic", email="mech@example.com", phone="1112223333", salary=50000)
        db.session.add(mechanic)

        db.session.commit()

    return app.test_client()

