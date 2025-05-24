import unittest
import uuid
from datetime import datetime, timedelta

from derzi_master_book.orders.models import Order
from derzi_master_book.orders import order_manager
from derzi_master_book.clients.models import Client
from derzi_master_book.clients import client_manager

class TestOrderManager(unittest.TestCase):

    def setUp(self):
        """Clear the orders_db and clients_db before each test for isolation."""
        order_manager.orders_db = []
        client_manager.clients_db = [] # Manage client_db state as well
        
        # Create a dummy client for use in tests
        self.test_client = client_manager.add_client(name="Test Client User", phone_number="1234567890")
        self.test_client_id = self.test_client.client_id

        self.another_client = client_manager.add_client(name="Another Client User", phone_number="0987654321")
        self.another_client_id = self.another_client.client_id


    def _create_sample_order_data(self, client_id=None, **kwargs):
        """Helper to create sample order data with defaults."""
        data = {
            "client_id": client_id if client_id else self.test_client_id,
            "deadline": datetime.now() + timedelta(days=7),
            "measurements": {"chest": "40", "waist": "32"},
            "style_details": "Slim fit shirt",
            "attachments": ["ref1.jpg"],
            "price": 150.00, # Assuming price is float/Decimal compatible
            "status": Order.STATUS_PENDING
        }
        data.update(kwargs)
        return data

    def test_add_order(self):
        """Test adding a new order."""
        sample_data = self._create_sample_order_data()
        
        order = order_manager.add_order(**sample_data)
        
        self.assertIsInstance(order, Order)
        self.assertEqual(order.client_id, sample_data["client_id"])
        self.assertEqual(order.deadline, sample_data["deadline"])
        self.assertEqual(order.measurements, sample_data["measurements"])
        self.assertEqual(order.style_details, sample_data["style_details"])
        self.assertEqual(order.attachments, sample_data["attachments"])
        self.assertEqual(float(order.price), sample_data["price"]) # Compare as float if model stores Decimal
        self.assertEqual(order.status, Order.STATUS_PENDING) # Default status
        self.assertIsInstance(order.order_id, uuid.UUID)
        self.assertIsInstance(order.order_date, datetime)
        
        self.assertEqual(len(order_manager.orders_db), 1)
        self.assertEqual(order_manager.orders_db[0], order)

        # Test adding an order with minimal required fields (assuming model defaults some)
        minimal_data = {
            "client_id": self.test_client_id,
            "deadline": datetime.now() + timedelta(days=3),
            "measurements": {"neck": "15"},
            "style_details": "Basic T-shirt"
        }
        order2 = order_manager.add_order(**minimal_data)
        self.assertEqual(len(order_manager.orders_db), 2)
        self.assertEqual(order2.client_id, minimal_data["client_id"])
        self.assertIsNone(order2.price) # Price should be None by default in model

        # Test for ValueError when deadline is not a datetime object
        with self.assertRaises(ValueError):
            invalid_deadline_data = self._create_sample_order_data(deadline="not-a-datetime")
            order_manager.add_order(**invalid_deadline_data)

        # Test for TypeError for missing required fields (handled by Python's arg checking)
        with self.assertRaises(TypeError):
            order_manager.add_order(client_id=self.test_client_id, measurements={}, style_details="Test") # Missing deadline
        with self.assertRaises(TypeError):
            order_manager.add_order(deadline=datetime.now(), measurements={}, style_details="Test") # Missing client_id

    def test_get_order_by_id(self):
        """Test retrieving an order by its ID."""
        sample_data = self._create_sample_order_data()
        order1 = order_manager.add_order(**sample_data)
        
        retrieved_order = order_manager.get_order_by_id(order1.order_id)
        self.assertEqual(retrieved_order, order1)
        
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(order_manager.get_order_by_id(non_existent_uuid))
        # Assuming get_order_by_id does not strictly validate UUID format, just won't find it
        self.assertIsNone(order_manager.get_order_by_id("not-a-uuid"))

    def test_list_orders_by_client(self):
        """Test listing orders for a specific client."""
        order1_data = self._create_sample_order_data(client_id=self.test_client_id, style_details="Order 1")
        order2_data = self._create_sample_order_data(client_id=self.another_client_id, style_details="Order 2")
        order3_data = self._create_sample_order_data(client_id=self.test_client_id, style_details="Order 3")

        order1 = order_manager.add_order(**order1_data)
        order2 = order_manager.add_order(**order2_data) # Belongs to another_client
        order3 = order_manager.add_order(**order3_data)

        client1_orders = order_manager.list_orders_by_client(self.test_client_id)
        self.assertEqual(len(client1_orders), 2)
        self.assertIn(order1, client1_orders)
        self.assertIn(order3, client1_orders)
        self.assertNotIn(order2, client1_orders)
        
        # Test with a client_id that has no orders
        yet_another_client_id = uuid.uuid4() # Non-existent client for orders
        self.assertEqual(order_manager.list_orders_by_client(yet_another_client_id), [])

    def test_list_all_orders(self):
        """Test listing all orders."""
        self.assertEqual(order_manager.list_all_orders(), []) # Test with empty db
        
        order1_data = self._create_sample_order_data(style_details="Order A")
        order2_data = self._create_sample_order_data(client_id=self.another_client_id, style_details="Order B")

        order1 = order_manager.add_order(**order1_data)
        order2 = order_manager.add_order(**order2_data)
        
        all_orders = order_manager.list_all_orders()
        self.assertEqual(len(all_orders), 2)
        self.assertIn(order1, all_orders)
        self.assertIn(order2, all_orders)

    def test_update_order_status(self):
        """Test updating an order's status."""
        order_data = self._create_sample_order_data()
        order = order_manager.add_order(**order_data)
        original_order_id = order.order_id
        
        updated_order = order_manager.update_order_status(original_order_id, Order.STATUS_IN_PROGRESS)
        self.assertIsNotNone(updated_order)
        self.assertEqual(updated_order.status, Order.STATUS_IN_PROGRESS)
        
        # Test updating to an invalid status string
        no_change_order = order_manager.update_order_status(original_order_id, "INVALID_STATUS_XYZ")
        self.assertIsNone(no_change_order) # order_manager.update_order_status returns None for invalid status
        # Verify status did not change
        current_order = order_manager.get_order_by_id(original_order_id)
        self.assertEqual(current_order.status, Order.STATUS_IN_PROGRESS) 

        # Test updating status for a non-existent order
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(order_manager.update_order_status(non_existent_uuid, Order.STATUS_DELIVERED))

    def test_update_order_details(self):
        """Test updating an order's details."""
        order_data = self._create_sample_order_data()
        order = order_manager.add_order(**order_data)
        original_order_id = order.order_id
        original_order_date = order.order_date # Should not change

        new_deadline = datetime.now() + timedelta(days=10)
        new_measurements = {"shoulder": "18", "sleeve": "25"}
        new_style = "Double-breasted suit"
        new_price = 250.75

        updated_order = order_manager.update_order_details(
            order_id=original_order_id,
            deadline=new_deadline,
            measurements=new_measurements,
            style_details=new_style,
            price=new_price # In manager this is float, model might use Decimal
        )
        self.assertIsNotNone(updated_order)
        self.assertEqual(updated_order.deadline, new_deadline)
        self.assertEqual(updated_order.measurements, new_measurements)
        self.assertEqual(updated_order.style_details, new_style)
        self.assertEqual(float(updated_order.price), new_price)
        self.assertEqual(updated_order.order_date, original_order_date) # Ensure order_date didn't change

        # Test updating only one attribute (e.g., attachments)
        new_attachments = ["ref_updated.jpg", "swatch.png"]
        further_updated_order = order_manager.update_order_details(
            order_id=original_order_id,
            attachments=new_attachments
        )
        self.assertIsNotNone(further_updated_order)
        self.assertEqual(further_updated_order.attachments, new_attachments)
        self.assertEqual(further_updated_order.style_details, new_style) # Check previous update persists

        # Test updating a non-existent order
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(order_manager.update_order_details(non_existent_uuid, style_details="Ghost Order"))
        
        # Test updating deadline to invalid type
        with self.assertRaises(ValueError):
            order_manager.update_order_details(order_id=original_order_id, deadline="not-a-datetime")


    def test_delete_order(self):
        """Test deleting an order."""
        order_data = self._create_sample_order_data()
        order = order_manager.add_order(**order_data)
        order_id_to_delete = order.order_id
        
        self.assertEqual(len(order_manager.orders_db), 1)
        
        delete_result = order_manager.delete_order(order_id_to_delete)
        self.assertTrue(delete_result)
        self.assertEqual(len(order_manager.orders_db), 0)
        self.assertIsNone(order_manager.get_order_by_id(order_id_to_delete))
        
        # Test deleting a non-existent order
        non_existent_uuid = uuid.uuid4()
        delete_non_existent_result = order_manager.delete_order(non_existent_uuid)
        self.assertFalse(delete_non_existent_result)

    def tearDown(self):
        """Clean up databases after each test."""
        order_manager.orders_db = []
        client_manager.clients_db = []

if __name__ == '__main__':
    unittest.main()
