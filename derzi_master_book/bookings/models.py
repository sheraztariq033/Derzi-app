import uuid
from datetime import datetime

class Appointment:
    # Appointment type constants
    TYPE_CONSULTATION = "Consultation"
    TYPE_MEASUREMENT = "Measurement"
    TYPE_FITTING = "Fitting"
    TYPE_PICKUP = "Pickup"
    TYPE_GENERAL_TASK = "General Task"
    
    VALID_APPOINTMENT_TYPES = [
        TYPE_CONSULTATION, TYPE_MEASUREMENT, TYPE_FITTING, 
        TYPE_PICKUP, TYPE_GENERAL_TASK
    ]

    def __init__(self, start_time, end_time, title, client_id=None, order_id=None, 
                 description=None, location=None, appointment_type=TYPE_GENERAL_TASK, 
                 appointment_id=None, created_at=None):
        
        if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
            raise ValueError("start_time and end_time must be datetime objects.")
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time.")
        if appointment_type not in self.VALID_APPOINTMENT_TYPES:
            raise ValueError(f"Invalid appointment_type: {appointment_type}. Must be one of {self.VALID_APPOINTMENT_TYPES}")

        self.appointment_id = appointment_id if appointment_id is not None else uuid.uuid4()
        self.client_id = client_id
        self.order_id = order_id
        self.start_time = start_time
        self.end_time = end_time
        self.title = title
        self.description = description
        self.location = location
        self.created_at = created_at if created_at is not None else datetime.now()
        self.appointment_type = appointment_type

    def __repr__(self):
        return f"<Appointment {self.appointment_id} - {self.title} ({self.start_time} to {self.end_time})>"
