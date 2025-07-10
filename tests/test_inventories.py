import unittest
from tests.conftest import get_test_client

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.client = get_test_client()

    def test_list_inventory(self):
        res = self.client.get('/inventory')
        self.assertEqual(res.status_code, 200)

    def test_get_inventory_not_found(self):
        res = self.client.get('/inventory/9999')
        self.assertEqual(res.status_code, 404)

    def test_add_inventory_success(self):
        item = {
            "name": "Oil Filter",
            "price": 19.99
        }
        res = self.client.post('/inventory', json=item)
        self.assertEqual(res.status_code, 201)

    def test_add_inventory_invalid(self):
        item = {"name": "Missing Price"}
        res = self.client.post('/inventory', json=item)
        self.assertEqual(res.status_code, 400)

    def test_update_inventory_success(self):
        item = {
            "name": "Oil Filter",
            "price": 19.99
        }
        res = self.client.post('/inventory', json=item)
        self.assertEqual(res.status_code, 201)
        update = {
            "price": 24.99
        }
        res = self.client.put('/inventory/1', json=update)
        self.assertEqual(res.status_code, 200)

    def test_update_inventory_not_found(self):
        update = {
            "price": 99.99
        }
        res = self.client.put('/inventory/9999', json=update)
        self.assertEqual(res.status_code, 404)

    def test_delete_inventory_success(self):
        # Create inventory item first
        item = {
            "name": "Air Filter",
            "price": 15.99
        }
        res = self.client.post('/inventory', json=item)
        self.assertEqual(res.status_code, 201)
        item_id = res.get_json()["id"]

        # Delete it
        res = self.client.delete(f'/inventory/{item_id}')
        self.assertEqual(res.status_code, 200)
        self.assertIn("deleted", res.get_json()["message"].lower())

    def test_delete_inventory_not_found(self):
        res = self.client.delete('/inventory/9999')
        self.assertEqual(res.status_code, 404)

    def test_get_inventory_success(self):
        # First create an inventory item
        item = {
            "name": "Brake Pads",
            "price": 29.99
        }
        res = self.client.post('/inventory', json=item)
        self.assertEqual(res.status_code, 201)
        item_id = res.get_json()["id"]

        # Now fetch the same item
        res = self.client.get(f'/inventory/{item_id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["name"], "Brake Pads")
