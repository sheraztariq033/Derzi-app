import unittest
import uuid
from datetime import datetime, timedelta

from derzi_master_book.bookings.models import Appointment
from derzi_master_book.bookings import booking_manager

# For linked dummy data
from derzi_master_book.clients.models import Client
from derzi_master_book.clients import client_manager
from derzi_master_book.orders.models import Order
from derzi_master_book.orders import order_manager

class TestBookingManager(unittest.TestCase):

    def setUp(self):
        """Clear databases before each test for isolation."""
        booking_manager.appointments_db = []
        client_manager.clients_db = []
        order_manager.orders_db = []

        # Create dummy client and order for use in Appointment tests
        self.test_client = client_manager.add_client(name="Test Client B", phone_number="777888999")
        self.test_client_id = self.test_client.client_id

        self.another_client = client_manager.add_client(name="Another Client B", phone_number="111000222")
        self.another_client_id = self.another_client.client_id
        
        self.test_order = order_manager.add_order(
            client_id=self.test_client_id,
            deadline=datetime.now() + timedelta(days=15),
            measurements={"order_specific_measurement": "value"},
            style_details="Test Order Style for Bookings"
        )
        self.test_order_id = self.test_order.order_id

        self.another_order = order_manager.add_order(
            client_id=self.another_client_id,
            deadline=datetime.now() + timedelta(days=18),
            measurements={},
            style_details="Another Test Order for Bookings"
        )
        self.another_order_id = self.another_order.order_id
        
        # Define some standard times for consistent testing
        self.now = datetime.now()
        self.one_hour = timedelta(hours=1)
        self.two_hours = timedelta(hours=2)


    def _create_sample_appointment_data(self, **kwargs):
        """Helper to create sample appointment data with defaults."""
        data = {
            "start_time": self.now + self.one_hour,
            "end_time": self.now + self.two_hours,
            "title": "Default Test Appointment",
            "client_id": self.test_client_id,
            "order_id": self.test_order_id,
            "description": "Default description",
            "location": "Default location",
            "appointment_type": Appointment.TYPE_GENERAL_TASK,
        }
        data.update(kwargs)
        return data

    def test_add_appointment(self):
        """Test adding a new appointment."""
        sample_data = self._create_sample_appointment_data()
        
        appointment = booking_manager.add_appointment(**sample_data)
        
        self.assertIsInstance(appointment, Appointment)
        self.assertEqual(appointment.start_time, sample_data["start_time"])
        self.assertEqual(appointment.end_time, sample_data["end_time"])
        self.assertEqual(appointment.title, sample_data["title"])
        self.assertEqual(appointment.client_id, sample_data["client_id"])
        self.assertEqual(appointment.order_id, sample_data["order_id"])
        self.assertEqual(appointment.description, sample_data["description"])
        self.assertEqual(appointment.location, sample_data["location"])
        self.assertEqual(appointment.appointment_type, sample_data["appointment_type"])
        self.assertIsInstance(appointment.appointment_id, uuid.UUID)
        self.assertIsInstance(appointment.created_at, datetime)
        
        self.assertEqual(len(booking_manager.appointments_db), 1)
        self.assertEqual(booking_manager.appointments_db[0], appointment)

        # Test adding with minimal required fields (start_time, end_time, title)
        minimal_data = {
            "start_time": self.now + timedelta(days=1),
            "end_time": self.now + timedelta(days=1, hours=1),
            "title": "Minimal Appointment"
        }
        appointment2 = booking_manager.add_appointment(**minimal_data)
        self.assertEqual(len(booking_manager.appointments_db), 2)
        self.assertIsNone(appointment2.client_id)
        self.assertIsNone(appointment2.order_id)
        self.assertEqual(appointment2.appointment_type, Appointment.TYPE_GENERAL_TASK) # Default type

        # Test for ValueError if end_time is before start_time (model validation)
        with self.assertRaises(ValueError):
            invalid_time_data = self._create_sample_appointment_data(
                start_time=self.now + self.two_hours, 
                end_time=self.now + self.one_hour
            )
            booking_manager.add_appointment(**invalid_time_data)

        # Test for TypeError for missing required fields (Python's arg checking)
        with self.assertRaises(TypeError):
            booking_manager.add_appointment(start_time=self.now, title="Test") # Missing end_time
        with self.assertRaises(TypeError):
            booking_manager.add_appointment(end_time=self.now, title="Test") # Missing start_time
        with self.assertRaises(TypeError):
            booking_manager.add_appointment(start_time=self.now, end_time=self.now + self.one_hour) # Missing title

        # Test adding with an invalid appointment_type (model validation)
        with self.assertRaises(ValueError):
            invalid_type_data = self._create_sample_appointment_data(appointment_type="INVALID_TYPE")
            booking_manager.add_appointment(**invalid_type_data)

    def test_get_appointment_by_id(self):
        """Test retrieving an appointment by its ID."""
        appt1_data = self._create_sample_appointment_data()
        appt1 = booking_manager.add_appointment(**appt1_data)
        
        retrieved_appt = booking_manager.get_appointment_by_id(appt1.appointment_id)
        self.assertEqual(retrieved_appt, appt1)
        
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(booking_manager.get_appointment_by_id(non_existent_uuid))
        self.assertIsNone(booking_manager.get_appointment_by_id("not-a-uuid-string"))

    def test_list_appointments_for_client(self):
        """Test listing appointments for a specific client."""
        appt1 = booking_manager.add_appointment(**self._create_sample_appointment_data(client_id=self.test_client_id, title="Client1 Appt1"))
        appt2 = booking_manager.add_appointment(**self._create_sample_appointment_data(client_id=self.another_client_id, title="Client2 Appt1"))
        appt3 = booking_manager.add_appointment(**self._create_sample_appointment_data(client_id=self.test_client_id, title="Client1 Appt2"))

        client1_appts = booking_manager.list_appointments_for_client(self.test_client_id)
        self.assertEqual(len(client1_appts), 2)
        self.assertIn(appt1, client1_appts)
        self.assertIn(appt3, client1_appts)
        self.assertNotIn(appt2, client1_appts)
        
        # Test with a client_id that has no appointments
        yet_another_client_id = uuid.uuid4() 
        self.assertEqual(booking_manager.list_appointments_for_client(yet_another_client_id), [])

    def test_list_appointments_for_order(self):
        """Test listing appointments for a specific order."""
        appt1 = booking_manager.add_appointment(**self._create_sample_appointment_data(order_id=self.test_order_id, title="Order1 Appt1"))
        appt2 = booking_manager.add_appointment(**self._create_sample_appointment_data(order_id=self.another_order_id, title="Order2 Appt1"))
        appt3 = booking_manager.add_appointment(**self._create_sample_appointment_data(order_id=self.test_order_id, title="Order1 Appt2"))

        order1_appts = booking_manager.list_appointments_for_order(self.test_order_id)
        self.assertEqual(len(order1_appts), 2)
        self.assertIn(appt1, order1_appts)
        self.assertIn(appt3, order1_appts)
        self.assertNotIn(appt2, order1_appts)

        # Test with an order_id that has no appointments
        yet_another_order_id = uuid.uuid4()
        self.assertEqual(booking_manager.list_appointments_for_order(yet_another_order_id), [])

    def test_list_appointments_in_range(self):
        """Test listing appointments within or overlapping a given time range."""
        # Appointments:
        # Appt A: 10:00 - 11:00
        # Appt B: 11:30 - 12:30
        # Appt C: 13:00 - 14:00
        # Appt D: 09:00 - 15:00 (fully encompasses range)
        # Appt E: 10:30 - 11:30 (starts in, ends in)
        # Appt F: 09:30 - 10:30 (starts before, ends in)
        # Appt G: 11:30 - 12:30 (starts in, ends after) -> same as Appt B
        # Appt H: 08:00 - 09:00 (completely before)
        # Appt I: 15:00 - 16:00 (completely after)

        base_time = datetime(2024, 1, 1, 0, 0, 0) # Use a fixed base for predictable times

        appt_a = booking_manager.add_appointment(start_time=base_time.replace(hour=10), end_time=base_time.replace(hour=11), title="Appt A")
        appt_b = booking_manager.add_appointment(start_time=base_time.replace(hour=11, minute=30), end_time=base_time.replace(hour=12, minute=30), title="Appt B")
        appt_c = booking_manager.add_appointment(start_time=base_time.replace(hour=13), end_time=base_time.replace(hour=14), title="Appt C")
        appt_d = booking_manager.add_appointment(start_time=base_time.replace(hour=9), end_time=base_time.replace(hour=15), title="Appt D")
        appt_e = booking_manager.add_appointment(start_time=base_time.replace(hour=10, minute=30), end_time=base_time.replace(hour=11, minute=30), title="Appt E")
        appt_f = booking_manager.add_appointment(start_time=base_time.replace(hour=9, minute=30), end_time=base_time.replace(hour=10, minute=30), title="Appt F")
        # Appt G is identical to Appt B for this test's purpose, so skip explicit G.
        appt_h = booking_manager.add_appointment(start_time=base_time.replace(hour=8), end_time=base_time.replace(hour=9), title="Appt H")
        appt_i = booking_manager.add_appointment(start_time=base_time.replace(hour=15), end_time=base_time.replace(hour=16), title="Appt I")

        # Test Range: 10:00 - 12:00
        range_start = base_time.replace(hour=10)
        range_end = base_time.replace(hour=12)
        
        overlapping_appts = booking_manager.list_appointments_in_range(range_start, range_end)
        
        self.assertIn(appt_a, overlapping_appts) # 10-11, fully within
        self.assertNotIn(appt_b, overlapping_appts) # 11:30-12:30, starts in, ends after range_end (if range is exclusive of end time)
                                                # Actually, (ApptStart < RangeEnd) and (ApptEnd > RangeStart)
                                                # Appt B: 11:30 < 12:00 (True) AND 12:30 > 10:00 (True) => Should be IN
        self.assertIn(appt_b, overlapping_appts) # Re-evaluating: Appt B should be included
        self.assertNotIn(appt_c, overlapping_appts) # 13-14, after range
        self.assertIn(appt_d, overlapping_appts) # 9-15, encompasses range
        self.assertIn(appt_e, overlapping_appts) # 10:30-11:30, fully within
        self.assertIn(appt_f, overlapping_appts) # 9:30-10:30, starts before, ends in
        self.assertNotIn(appt_h, overlapping_appts) # 8-9, before range
        self.assertNotIn(appt_i, overlapping_appts) # 15-16, after range
        
        self.assertEqual(len(overlapping_appts), 5, f"Expected 5, got {len(overlapping_appts)}: {[a.title for a in overlapping_appts]}")

        # Test range where start_time is after end_time
        with self.assertRaises(ValueError):
            booking_manager.list_appointments_in_range(range_end, range_start)
            
        # Test range with no overlapping appointments
        empty_range_start = base_time.replace(hour=17)
        empty_range_end = base_time.replace(hour=18)
        self.assertEqual(booking_manager.list_appointments_in_range(empty_range_start, empty_range_end), [])

    def test_list_all_appointments(self):
        """Test listing all appointments."""
        self.assertEqual(booking_manager.list_all_appointments(), []) # Test with empty db
        
        appt1 = booking_manager.add_appointment(**self._create_sample_appointment_data(title="Appt X"))
        appt2 = booking_manager.add_appointment(**self._create_sample_appointment_data(title="Appt Y"))
        
        all_appts = booking_manager.list_all_appointments()
        self.assertEqual(len(all_appts), 2)
        self.assertIn(appt1, all_appts)
        self.assertIn(appt2, all_appts)

    def test_update_appointment(self):
        """Test updating an appointment's information."""
        appt_data = self._create_sample_appointment_data(title="Original Title")
        appt = booking_manager.add_appointment(**appt_data)
        original_id = appt.appointment_id
        original_created_at = appt.created_at # Should not change

        new_start_time = self.now + timedelta(days=2)
        new_end_time = self.now + timedelta(days=2, hours=2)
        new_title = "Updated Title"
        new_desc = "Updated description"
        new_type = Appointment.TYPE_FITTING

        updated_appt = booking_manager.update_appointment(
            appointment_id=original_id,
            start_time=new_start_time,
            end_time=new_end_time,
            title=new_title,
            description=new_desc,
            appointment_type=new_type
        )
        self.assertIsNotNone(updated_appt)
        self.assertEqual(updated_appt.start_time, new_start_time)
        self.assertEqual(updated_appt.end_time, new_end_time)
        self.assertEqual(updated_appt.title, new_title)
        self.assertEqual(updated_appt.description, new_desc)
        self.assertEqual(updated_appt.appointment_type, new_type)
        self.assertEqual(updated_appt.appointment_id, original_id)
        self.assertEqual(updated_appt.created_at, original_created_at)

        # Test ValueError if end_time updated to be before start_time
        with self.assertRaises(ValueError):
            booking_manager.update_appointment(original_id, end_time=new_start_time - self.one_hour)
        
        # Test updating a non-existent appointment
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(booking_manager.update_appointment(non_existent_uuid, title="Ghost Appt"))

        # Test updating appointment_type to an invalid type
        with self.assertRaises(ValueError):
            booking_manager.update_appointment(original_id, appointment_type="INVALID_TYPE_AGAIN")
            
        # Test updating title to empty string (should raise ValueError in manager)
        with self.assertRaises(ValueError):
            booking_manager.update_appointment(original_id, title="  ")


    def test_delete_appointment(self):
        """Test deleting an appointment."""
        appt_data = self._create_sample_appointment_data()
        appt = booking_manager.add_appointment(**appt_data)
        appointment_id_to_delete = appt.appointment_id
        
        self.assertEqual(len(booking_manager.appointments_db), 1)
        
        delete_result = booking_manager.delete_appointment(appointment_id_to_delete)
        self.assertTrue(delete_result)
        self.assertEqual(len(booking_manager.appointments_db), 0)
        self.assertIsNone(booking_manager.get_appointment_by_id(appointment_id_to_delete))
        
        # Test deleting a non-existent appointment
        non_existent_uuid = uuid.uuid4()
        delete_non_existent_result = booking_manager.delete_appointment(non_existent_uuid)
        self.assertFalse(delete_non_existent_result)

    def tearDown(self):
        """Clean up databases after each test."""
        booking_manager.appointments_db = []
        client_manager.clients_db = []
        order_manager.orders_db = []

if __name__ == '__main__':
    unittest.main()
