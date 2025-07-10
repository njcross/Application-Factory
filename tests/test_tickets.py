import unittest
from tests.conftest import get_test_client, generate_token

class TestTickets(unittest.TestCase):
    def setUp(self):
        self.client = get_test_client()
        self.token = generate_token(1)
        self.headers = {'Authorization': f'Bearer {self.token}'}

        # Create ticket
        ticket_res = self.client.post('/tickets', json={
            "VIN": "ABC123",
            "service_date": "2025-07-09",
            "service_desc": "Brake check",
            "customer_id": 1
        }, headers=self.headers)
        self.ticket = ticket_res.get_json()

        # Create mechanic
        mech_res = self.client.post('/mechanics', json={
            "name": "Mike Wrench",
            "email": "mike@shop.com",
            "phone": "1231231234",
            "salary": 50000
        })
        self.mechanic = mech_res.get_json()

        # Create inventory part
        part_res = self.client.post('/inventory', json={
            "name": "Brake Pad",
            "price": 79.99
        })
        self.part = part_res.get_json()

    def test_get_tickets_success(self):
        res = self.client.get('/tickets', headers=self.headers)
        self.assertEqual(res.status_code, 200)

    def test_get_ticket_unauthenticated(self):
        res = self.client.get('/tickets/1')
        self.assertEqual(res.status_code, 401)  

    def test_add_ticket_invalid_customer(self):
        ticket = {
            "VIN": "2HGCM82633A123456",
            "service_date": "2025-07-09",
            "service_desc": "Oil change",
            "customer_id": 9999
        }
        res = self.client.post('/tickets', json=ticket, headers=self.headers)
        self.assertEqual(res.status_code, 403)

    def test_add_ticket_success(self):
        ticket = {
            "VIN": "2HGCM82633A123456",
            "service_date": "2025-07-09",
            "service_desc": "Oil change",
            "customer_id": 1
        }
        res = self.client.post('/tickets', json=ticket, headers=self.headers)
        self.assertEqual(res.status_code, 201)

    def test_update_ticket_success(self):
        ticket = {
            "VIN": "2HGCM82633A123456",
            "service_date": "2025-07-09",
            "service_desc": "Oil change",
            "customer_id": 1
        }
        res = self.client.post('/tickets', json=ticket, headers=self.headers)
        self.assertEqual(res.status_code, 201)
        ticket_id = res.get_json()["id"]
        update = {
            "VIN": "2HGCM82633A123456",
            "service_date": "2025-07-09",
            "service_desc": "Full diagnostic"
        }
        res = self.client.put(f'/tickets/{ticket_id}', json=update, headers=self.headers)
        self.assertEqual(res.status_code, 200)

    def test_update_ticket_unauthorized(self):
        update = {
            "service_desc": "Unauthorized update"
        }
        res = self.client.put('/tickets/2', json=update, headers=self.headers)  
        self.assertIn(res.status_code, [403, 401])

    def test_delete_ticket_success(self):
        ticket = {
            "VIN": "2HGCM82633A123456",
            "service_date": "2025-07-09",
            "service_desc": "Oil change",
            "customer_id": 1
        }
        res = self.client.post('/tickets', json=ticket, headers=self.headers)
        self.assertEqual(res.status_code, 201)
        ticket_id = res.get_json()["id"]
        res = self.client.delete(f'/tickets/{ticket_id}', headers=self.headers)
        self.assertEqual(res.status_code, 200)
    
    def test_get_my_tickets_success(self):
        res = self.client.get('/tickets/my-tickets', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isinstance(res.get_json(), list))

    def test_edit_ticket_mechanics_success(self):
        res = self.client.put(
            f'/tickets/{self.ticket["id"]}/edit',
            json={"add_ids": [self.mechanic["id"]], "remove_ids": []},
            headers=self.headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("Mechanic assignments updated", res.get_data(as_text=True))

    def test_add_part_to_ticket_success(self):
        res = self.client.put(
            f'/tickets/{self.ticket["id"]}/add-part/{self.part["id"]}',
            headers=self.headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("Part added to ticket", res.get_data(as_text=True))

    def test_assign_mechanic_success(self):
        res = self.client.put(
            f'/tickets/{self.ticket["id"]}/assign-mechanic/{self.mechanic["id"]}',
            headers=self.headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("Mechanic successfully assigned", res.get_data(as_text=True))

    def test_remove_mechanic_success(self):
        # Assign first
        self.client.put(
            f'/tickets/{self.ticket["id"]}/assign-mechanic/{self.mechanic["id"]}',
            headers=self.headers
        )
        # Then remove
        res = self.client.put(
            f'/tickets/{self.ticket["id"]}/remove-mechanic/{self.mechanic["id"]}',
            headers=self.headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("Mechanic successfully removed", res.get_data(as_text=True))