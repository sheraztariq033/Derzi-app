import unittest
import uuid
from datetime import datetime, timedelta

from derzi_master_book.measurements.models import MeasurementTemplate, CustomMeasurement
from derzi_master_book.measurements import measurement_manager

# For linked dummy data
from derzi_master_book.clients.models import Client
from derzi_master_book.clients import client_manager
from derzi_master_book.orders.models import Order
from derzi_master_book.orders import order_manager

class TestMeasurementManager(unittest.TestCase):

    def setUp(self):
        """Clear databases before each test for isolation."""
        measurement_manager.measurement_templates_db = []
        measurement_manager.custom_measurements_db = []
        client_manager.clients_db = []
        order_manager.orders_db = []

        # Create dummy client and order for use in CustomMeasurement tests
        self.test_client = client_manager.add_client(name="Test Client M", phone_number="111222333")
        self.test_client_id = self.test_client.client_id

        self.another_client = client_manager.add_client(name="Another Client M", phone_number="444555666")
        self.another_client_id = self.another_client.client_id
        
        self.test_order = order_manager.add_order(
            client_id=self.test_client_id,
            deadline=datetime.now() + timedelta(days=10),
            measurements={"initial_order_measurement": "value"}, # Can be empty
            style_details="Test Order Style for Measurements"
        )
        self.test_order_id = self.test_order.order_id

        self.another_order = order_manager.add_order(
            client_id=self.another_client_id,
            deadline=datetime.now() + timedelta(days=12),
            measurements={},
            style_details="Another Test Order"
        )
        self.another_order_id = self.another_order.order_id

    # --- MeasurementTemplate Test Cases ---
    def test_add_measurement_template(self):
        """Test adding a new measurement template."""
        template = measurement_manager.add_measurement_template(
            name="Men's Shirt",
            fields=["neck", "chest", "waist", "sleeve_length"],
            diagram_image_path="path/to/shirt_diagram.png"
        )
        self.assertIsInstance(template, MeasurementTemplate)
        self.assertEqual(template.name, "Men's Shirt")
        self.assertEqual(template.fields, ["neck", "chest", "waist", "sleeve_length"])
        self.assertEqual(template.diagram_image_path, "path/to/shirt_diagram.png")
        self.assertIsInstance(template.template_id, uuid.UUID)
        
        self.assertEqual(len(measurement_manager.measurement_templates_db), 1)
        self.assertEqual(measurement_manager.measurement_templates_db[0], template)

        # Test adding with minimal required fields
        template2 = measurement_manager.add_measurement_template(name="Basic Pants", fields=["waist", "inseam"])
        self.assertEqual(len(measurement_manager.measurement_templates_db), 2)
        self.assertIsNone(template2.diagram_image_path)

        # Test for ValueError for missing/invalid name or fields (as per manager's validation)
        with self.assertRaises(ValueError):
            measurement_manager.add_measurement_template(name="", fields=["test"]) # Empty name
        with self.assertRaises(ValueError):
            measurement_manager.add_measurement_template(name="Test", fields=[]) # Empty fields list
        with self.assertRaises(ValueError):
            measurement_manager.add_measurement_template(name="Test", fields=["field1", 123]) # Invalid field type

    def test_get_measurement_template_by_id(self):
        """Test retrieving a measurement template by its ID."""
        template1 = measurement_manager.add_measurement_template(name="Suit Template", fields=["chest", "shoulder"])
        
        retrieved_template = measurement_manager.get_measurement_template_by_id(template1.template_id)
        self.assertEqual(retrieved_template, template1)
        
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(measurement_manager.get_measurement_template_by_id(non_existent_uuid))
        # Test with an invalid UUID format string
        self.assertIsNone(measurement_manager.get_measurement_template_by_id("not-a-valid-uuid"))

    def test_list_all_measurement_templates(self):
        """Test listing all measurement templates."""
        self.assertEqual(measurement_manager.list_all_measurement_templates(), []) # Test with empty db
        
        template1 = measurement_manager.add_measurement_template(name="Template A", fields=["a"])
        template2 = measurement_manager.add_measurement_template(name="Template B", fields=["b"])
        
        all_templates = measurement_manager.list_all_measurement_templates()
        self.assertEqual(len(all_templates), 2)
        self.assertIn(template1, all_templates)
        self.assertIn(template2, all_templates)

    def test_update_measurement_template(self):
        """Test updating a measurement template's information."""
        template = measurement_manager.add_measurement_template(name="Old Name", fields=["old_field"])
        original_id = template.template_id

        updated_template = measurement_manager.update_measurement_template(
            template_id=original_id,
            name="New Name",
            fields=["new_field1", "new_field2"],
            diagram_image_path="new/path.png"
        )
        self.assertIsNotNone(updated_template)
        self.assertEqual(updated_template.name, "New Name")
        self.assertEqual(updated_template.fields, ["new_field1", "new_field2"])
        self.assertEqual(updated_template.diagram_image_path, "new/path.png")
        self.assertEqual(updated_template.template_id, original_id)

        # Test updating non-existent template
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(measurement_manager.update_measurement_template(non_existent_uuid, name="Ghost"))
        
        # Test invalid updates (e.g., empty name)
        with self.assertRaises(ValueError):
            measurement_manager.update_measurement_template(original_id, name="")
        with self.assertRaises(ValueError):
            measurement_manager.update_measurement_template(original_id, fields=[123])


    def test_delete_measurement_template(self):
        """Test deleting a measurement template."""
        template = measurement_manager.add_measurement_template(name="To Delete", fields=["tbd"])
        template_id_to_delete = template.template_id
        
        self.assertEqual(len(measurement_manager.measurement_templates_db), 1)
        
        delete_result = measurement_manager.delete_measurement_template(template_id_to_delete)
        self.assertTrue(delete_result)
        self.assertEqual(len(measurement_manager.measurement_templates_db), 0)
        self.assertIsNone(measurement_manager.get_measurement_template_by_id(template_id_to_delete))
        
        # Test deleting non-existent template
        non_existent_uuid = uuid.uuid4()
        self.assertFalse(measurement_manager.delete_measurement_template(non_existent_uuid))

    # --- CustomMeasurement Test Cases ---
    def test_add_custom_measurement(self):
        """Test adding a new custom measurement."""
        measurements_data = {"chest": "42", "waist": "34", "hips": "40"}
        custom_meas = measurement_manager.add_custom_measurement(
            order_id=self.test_order_id,
            client_id=self.test_client_id,
            measurements=measurements_data,
            notes="Evening wear measurements"
        )
        self.assertIsInstance(custom_meas, CustomMeasurement)
        self.assertEqual(custom_meas.order_id, self.test_order_id)
        self.assertEqual(custom_meas.client_id, self.test_client_id)
        self.assertEqual(custom_meas.measurements, measurements_data)
        self.assertEqual(custom_meas.notes, "Evening wear measurements")
        self.assertIsInstance(custom_meas.measurement_id, uuid.UUID)
        self.assertIsInstance(custom_meas.date_taken, datetime)
        
        self.assertEqual(len(measurement_manager.custom_measurements_db), 1)
        self.assertEqual(measurement_manager.custom_measurements_db[0], custom_meas)

        # Test adding with minimal required fields
        minimal_data = {"neck": "16"}
        custom_meas2 = measurement_manager.add_custom_measurement(
            order_id=self.another_order_id, client_id=self.another_client_id, measurements=minimal_data
        )
        self.assertEqual(len(measurement_manager.custom_measurements_db), 2)
        self.assertIsNone(custom_meas2.notes)

        # Test for ValueError for invalid/empty measurements dict
        with self.assertRaises(ValueError):
            measurement_manager.add_custom_measurement(self.test_order_id, self.test_client_id, measurements={})
        with self.assertRaises(ValueError):
            measurement_manager.add_custom_measurement(self.test_order_id, self.test_client_id, measurements="not-a-dict")
        
        # Python's arg checking handles missing order_id, client_id, measurements
        with self.assertRaises(TypeError):
            measurement_manager.add_custom_measurement(client_id=self.test_client_id, measurements=minimal_data)


    def test_get_custom_measurement_by_id(self):
        """Test retrieving a custom measurement by its ID."""
        meas1 = measurement_manager.add_custom_measurement(self.test_order_id, self.test_client_id, {"chest": "38"})
        
        retrieved_meas = measurement_manager.get_custom_measurement_by_id(meas1.measurement_id)
        self.assertEqual(retrieved_meas, meas1)
        
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(measurement_manager.get_custom_measurement_by_id(non_existent_uuid))
        self.assertIsNone(measurement_manager.get_custom_measurement_by_id("not-a-uuid-string"))

    def test_get_custom_measurements_for_order(self):
        """Test retrieving custom measurements for a specific order_id."""
        meas1 = measurement_manager.add_custom_measurement(self.test_order_id, self.test_client_id, {"m1": "v1"})
        meas2 = measurement_manager.add_custom_measurement(self.another_order_id, self.another_client_id, {"m2": "v2"})
        meas3 = measurement_manager.add_custom_measurement(self.test_order_id, self.test_client_id, {"m3": "v3"})

        order1_measurements = measurement_manager.get_custom_measurements_for_order(self.test_order_id)
        self.assertEqual(len(order1_measurements), 2)
        self.assertIn(meas1, order1_measurements)
        self.assertIn(meas3, order1_measurements)
        self.assertNotIn(meas2, order1_measurements)
        
        # Test with an order_id that has no measurements
        yet_another_order_id = uuid.uuid4()
        self.assertEqual(measurement_manager.get_custom_measurements_for_order(yet_another_order_id), [])

    def test_get_custom_measurements_for_client(self):
        """Test retrieving custom measurements for a specific client_id."""
        meas1 = measurement_manager.add_custom_measurement(self.test_order_id, self.test_client_id, {"c1m1": "v1"})
        meas2 = measurement_manager.add_custom_measurement(self.another_order_id, self.another_client_id, {"c2m1": "v2"})
        # Another measurement for the first client, but different order
        meas3_order = order_manager.add_order(self.test_client_id, datetime.now(), {}, "Order for meas3")
        meas3 = measurement_manager.add_custom_measurement(meas3_order.order_id, self.test_client_id, {"c1m2": "v3"})

        client1_measurements = measurement_manager.get_custom_measurements_for_client(self.test_client_id)
        self.assertEqual(len(client1_measurements), 2)
        self.assertIn(meas1, client1_measurements)
        self.assertIn(meas3, client1_measurements)
        self.assertNotIn(meas2, client1_measurements)

        # Test with a client_id that has no measurements
        yet_another_client_id = uuid.uuid4()
        self.assertEqual(measurement_manager.get_custom_measurements_for_client(yet_another_client_id), [])

    def test_update_custom_measurement(self):
        """Test updating a custom measurement's information."""
        custom_meas = measurement_manager.add_custom_measurement(
            self.test_order_id, self.test_client_id, {"original_meas": "val1"}, "Original note"
        )
        original_id = custom_meas.measurement_id
        original_date_taken = custom_meas.date_taken 
        original_order_id = custom_meas.order_id # Should not change
        original_client_id = custom_meas.client_id # Should not change

        updated_measurements = {"updated_meas": "val2", "new_field": "val3"}
        updated_notes = "Updated note"

        updated_custom_meas = measurement_manager.update_custom_measurement(
            measurement_id=original_id,
            measurements=updated_measurements,
            notes=updated_notes
        )
        self.assertIsNotNone(updated_custom_meas)
        self.assertEqual(updated_custom_meas.measurements, updated_measurements)
        self.assertEqual(updated_custom_meas.notes, updated_notes)
        self.assertEqual(updated_custom_meas.measurement_id, original_id)
        self.assertEqual(updated_custom_meas.date_taken, original_date_taken) # Date taken should not change
        self.assertEqual(updated_custom_meas.order_id, original_order_id)
        self.assertEqual(updated_custom_meas.client_id, original_client_id)

        # Test updating non-existent custom measurement
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(measurement_manager.update_custom_measurement(non_existent_uuid, notes="Ghost notes"))

        # Test ValueError for invalid measurements
        with self.assertRaises(ValueError):
            measurement_manager.update_custom_measurement(original_id, measurements={}) # Empty dict
        with self.assertRaises(ValueError):
            measurement_manager.update_custom_measurement(original_id, measurements="not-a-dict")


    def test_delete_custom_measurement(self):
        """Test deleting a custom measurement."""
        custom_meas = measurement_manager.add_custom_measurement(self.test_order_id, self.test_client_id, {"chest": "40"})
        measurement_id_to_delete = custom_meas.measurement_id
        
        self.assertEqual(len(measurement_manager.custom_measurements_db), 1)
        
        delete_result = measurement_manager.delete_custom_measurement(measurement_id_to_delete)
        self.assertTrue(delete_result)
        self.assertEqual(len(measurement_manager.custom_measurements_db), 0)
        self.assertIsNone(measurement_manager.get_custom_measurement_by_id(measurement_id_to_delete))
        
        # Test deleting non-existent custom measurement
        non_existent_uuid = uuid.uuid4()
        self.assertFalse(measurement_manager.delete_custom_measurement(non_existent_uuid))

    def tearDown(self):
        """Clean up databases after each test."""
        measurement_manager.measurement_templates_db = []
        measurement_manager.custom_measurements_db = []
        client_manager.clients_db = []
        order_manager.orders_db = []

if __name__ == '__main__':
    unittest.main()
