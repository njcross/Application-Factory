import unittest
from tests.conftest import get_test_client

class TestMechanics(unittest.TestCase):
    def setUp(self):
        self.client = get_test_client()

    def test_list_mechanics(self):
        res = self.client.get('/mechanics')
        self.assertEqual(res.status_code, 200)

    def test_get_mechanic_not_found(self):
        res = self.client.get('/mechanics/9999')
        self.assertEqual(res.status_code, 404)

    def test_add_mechanic_success(self):
        data = {
            "name": "Jane Wrench",
            "email": "jane@wrench.com",
            "phone": "5551112233",
            "salary": 55000
        }
        res = self.client.post('/mechanics', json=data)
        self.assertEqual(res.status_code, 201)

    def test_add_mechanic_duplicate_email(self):
        data = {
            "name": "Jane Wrench",
            "email": "jane@wrench.com",
            "phone": "5551112233",
            "salary": 55000
        }
        res = self.client.post('/mechanics', json=data)
        self.assertEqual(res.status_code, 201)
        data = {
            "name": "Copy",
            "email": "jane@wrench.com",
            "phone": "0000000000",
            "salary": 40000
        }
        res = self.client.post('/mechanics', json=data)
        self.assertEqual(res.status_code, 400)

    def test_update_mechanic_success(self):
        update = {
            "name": "Jane Wrench",
            "email": "jane@wrench.com",
            "phone": "5550001111",
            "salary": 55000
        }
        res = self.client.put('/mechanics/1', json=update)
        self.assertEqual(res.status_code, 200)

    def test_update_mechanic_not_found(self):
        update = {
            "phone": "5559999999"
        }
        res = self.client.put('/mechanics/9999', json=update)
        self.assertEqual(res.status_code, 404)

    def test_get_mechanic_success(self):
        res = self.client.get(f'/mechanics/1')
        self.assertEqual(res.status_code, 200)

    def test_delete_mechanic_success(self):
        res = self.client.delete(f'/mechanics/1')
        self.assertEqual(res.status_code, 200)
        self.assertIn("Mechanic deleted", res.get_json()["message"])

    def test_delete_mechanic_not_found(self):
        res = self.client.delete('/mechanics/9999')
        self.assertEqual(res.status_code, 404)

    def test_most_active_mechanics(self):
        res = self.client.get('/mechanics/most-active?page=1&per_page=5')
        self.assertEqual(res.status_code, 200)
        self.assertIn("mechanics", res.get_json())