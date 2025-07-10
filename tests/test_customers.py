import unittest
from tests.conftest import get_test_client, generate_token

class TestCustomers(unittest.TestCase):
    def setUp(self):
        self.client = get_test_client()
        self.token = generate_token(1)
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def test_get_customers_success(self):
        res = self.client.get('/customers')
        self.assertEqual(res.status_code, 200)

    def test_get_customer_unauthorized(self):
        res = self.client.get('/customers/999')  # No token
        self.assertEqual(res.status_code, 401)  # Or 403 if you override

    def test_add_customer_success(self):
        data = {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "phone": "1234567890",
            "password": "securepassword"
        }
        res = self.client.post('/customers', json=data)
        self.assertEqual(res.status_code, 201)

    def test_add_customer_duplicate_email(self):
        data = {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "phone": "1234567890",
            "password": "securepassword"
        }
        res = self.client.post('/customers', json=data)
        self.assertEqual(res.status_code, 201)

        data = {
            "name": "Duplicate",
            "email": "johndoe@example.com",  # Already exists
            "phone": "1234567890",
            "password": "securepassword"
        }
        res = self.client.post('/customers', json=data)
        self.assertEqual(res.status_code, 400)

    def test_update_customer_success(self):
        update = {
            "name": "John Updated"
        }
        res = self.client.put('/customers/1', json=update, headers=self.headers)
        self.assertEqual(res.status_code, 200)

    def test_update_customer_unauthorized(self):
        update = {"name": "Bad Update"}
        res = self.client.put('/customers/2', json=update, headers=self.headers)  # Token for id 1, trying to update id 2
        self.assertIn(res.status_code, [403, 401])

    def test_delete_customer_success(self):
        # Create a new customer first
        new_customer = {
            "name": "Temp User",
            "email": "tempuser@example.com",
            "phone": "1112223333",
            "password": "temp123"
        }
        res = self.client.post('/customers', json=new_customer)
        self.assertEqual(res.status_code, 201)
        customer_id = res.get_json()["id"]

        # Generate token for that customer
        token = generate_token(customer_id)
        headers = {'Authorization': f'Bearer {token}'}

        # Delete the customer
        res = self.client.delete(f'/customers/{customer_id}', headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn("deleted", res.get_json()["message"].lower())

    def test_delete_customer_unauthorized(self):
        # Attempt to delete another customer's account using the wrong token
        res = self.client.delete('/customers/2', headers=self.headers)
        self.assertIn(res.status_code, [403, 401])

    def test_get_single_customer_success(self):
        # Create a customer
        data = {
            "name": "Fetch Me",
            "email": "fetch@example.com",
            "phone": "1231231234",
            "password": "securepass"
        }
        res = self.client.post('/customers', json=data)
        self.assertEqual(res.status_code, 201)
        customer_id = res.get_json()["id"]

        # Generate token for this customer
        token = generate_token(customer_id)
        headers = {'Authorization': f'Bearer {token}'}

        # Fetch single customer using token
        res = self.client.get(f'/customers/{customer_id}', headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["email"], "fetch@example.com")

    def test_get_single_customer_unauthorized(self):
        res = self.client.get('/customers/1')  # No token
        self.assertEqual(res.status_code, 401)

    def test_customer_login_success(self):
        # First create customer
        data = {
            "name": "Login Tester",
            "email": "logintest@example.com",
            "phone": "9999999999",
            "password": "logintest123"
        }
        self.client.post('/customers', json=data)

        login_payload = {
            "email": "logintest@example.com",
            "password": "logintest123"
        }
        res = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.get_json())

    def test_customer_login_invalid(self):
        login_payload = {
            "email": "fake@example.com",
            "password": "wrongpass"
        }
        res = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(res.status_code, 401)
