import unittest
import uuid
from datetime import datetime

# Assuming the tests will be run from the root of the project (e.g., python -m unittest discover)
# or that derzi_master_book is in PYTHONPATH
from derzi_master_book.clients.models import Client
from derzi_master_book.clients import client_manager

class TestClientManager(unittest.TestCase):

    def setUp(self):
        """Clear the clients_db before each test for isolation."""
        client_manager.clients_db = []

    def test_add_client(self):
        """Test adding a new client."""
        client = client_manager.add_client(
            name="Test User",
            phone_number="1234567890",
            email="test@example.com",
            address="123 Test St"
        )
        self.assertIsInstance(client, Client)
        self.assertEqual(client.name, "Test User")
        self.assertEqual(client.phone_number, "1234567890")
        self.assertEqual(client.email, "test@example.com")
        self.assertEqual(client.address, "123 Test St")
        self.assertIsInstance(client.client_id, uuid.UUID)
        self.assertIsInstance(client.creation_date, datetime)
        
        self.assertEqual(len(client_manager.clients_db), 1)
        self.assertEqual(client_manager.clients_db[0], client)

        # Test adding a client with minimal required fields
        client2 = client_manager.add_client(name="Another User", phone_number="0987654321")
        self.assertEqual(len(client_manager.clients_db), 2)
        self.assertEqual(client2.name, "Another User")
        self.assertIsNone(client2.email) # Email should be None by default

        # Current add_client doesn't have explicit validation for missing name/phone,
        # it would raise TypeError from Client constructor if not provided.
        # Python's default behavior for missing arguments will raise TypeError.
        with self.assertRaises(TypeError):
            client_manager.add_client(phone_number="1112223333") # Missing name
        with self.assertRaises(TypeError):
            client_manager.add_client(name="No Phone User") # Missing phone_number

    def test_get_client_by_id(self):
        """Test retrieving a client by their ID."""
        client1 = client_manager.add_client(name="Client One", phone_number="11111")
        
        retrieved_client = client_manager.get_client_by_id(client1.client_id)
        self.assertEqual(retrieved_client, client1)
        
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(client_manager.get_client_by_id(non_existent_uuid))
        
        # Test with an invalid UUID format (current implementation of get_client_by_id does not validate format,
        # it would just not find it. If it did, this test would be different)
        # For now, it should just return None as it won't match any client's UUID.
        self.assertIsNone(client_manager.get_client_by_id("not-a-uuid"))

    def test_list_all_clients(self):
        """Test listing all clients."""
        self.assertEqual(client_manager.list_all_clients(), []) # Test with empty db
        
        client1 = client_manager.add_client(name="Client Alpha", phone_number="123")
        client2 = client_manager.add_client(name="Client Beta", phone_number="456")
        
        all_clients = client_manager.list_all_clients()
        self.assertEqual(len(all_clients), 2)
        self.assertIn(client1, all_clients)
        self.assertIn(client2, all_clients)

    def test_update_client(self):
        """Test updating a client's information."""
        client = client_manager.add_client(name="Original Name", phone_number="100000", email="original@example.com")
        original_id = client.client_id
        original_creation_date = client.creation_date

        updated_client = client_manager.update_client(
            client_id=original_id,
            name="Updated Name",
            phone_number="200000"
        )
        self.assertIsNotNone(updated_client)
        self.assertEqual(updated_client.name, "Updated Name")
        self.assertEqual(updated_client.phone_number, "200000")
        self.assertEqual(updated_client.email, "original@example.com") # Email should be unchanged
        self.assertEqual(updated_client.client_id, original_id) # ID should not change
        self.assertEqual(updated_client.creation_date, original_creation_date) # Creation date should not change

        # Test updating only one attribute (e.g., email)
        further_updated_client = client_manager.update_client(
            client_id=original_id,
            email="new_email@example.com"
        )
        self.assertIsNotNone(further_updated_client)
        self.assertEqual(further_updated_client.name, "Updated Name") # Name from previous update
        self.assertEqual(further_updated_client.phone_number, "200000") # Phone from previous update
        self.assertEqual(further_updated_client.email, "new_email@example.com") # Email updated

        # Test updating a non-existent client
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(client_manager.update_client(client_id=non_existent_uuid, name="Ghost"))
        
        # Test attempting to update with no actual changes
        no_change_client = client_manager.update_client(client_id=original_id)
        self.assertIsNotNone(no_change_client)
        self.assertEqual(no_change_client.email, "new_email@example.com")


    def test_delete_client(self):
        """Test deleting a client."""
        client = client_manager.add_client(name="To Be Deleted", phone_number="999")
        client_id_to_delete = client.client_id
        
        self.assertEqual(len(client_manager.clients_db), 1)
        
        delete_result = client_manager.delete_client(client_id_to_delete)
        self.assertTrue(delete_result)
        self.assertEqual(len(client_manager.clients_db), 0)
        self.assertIsNone(client_manager.get_client_by_id(client_id_to_delete))
        
        # Test deleting a non-existent client
        non_existent_uuid = uuid.uuid4()
        delete_non_existent_result = client_manager.delete_client(non_existent_uuid)
        self.assertFalse(delete_non_existent_result)

if __name__ == '__main__':
    unittest.main()
