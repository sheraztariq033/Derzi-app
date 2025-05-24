from .models import Appointment
from datetime import datetime
import uuid

appointments_db = []

def add_appointment(start_time, end_time, title, client_id=None, order_id=None, 
                    description=None, location=None, appointment_type=Appointment.TYPE_GENERAL_TASK):
    """
    Creates a new Appointment instance and adds it to the in-memory database.
    Validates that end_time is after start_time.
    """
    # Model already validates start_time, end_time and appointment_type
    new_appointment = Appointment(
        start_time=start_time,
        end_time=end_time,
        title=title,
        client_id=client_id,
        order_id=order_id,
        description=description,
        location=location,
        appointment_type=appointment_type
    )
    appointments_db.append(new_appointment)
    return new_appointment

def get_appointment_by_id(appointment_id):
    """
    Searches appointments_db for an appointment with the given appointment_id.
    Returns the appointment object if found, otherwise None.
    """
    try:
        uuid_obj = uuid.UUID(str(appointment_id))
    except ValueError:
        return None # Not a valid UUID format
        
    for appointment in appointments_db:
        if appointment.appointment_id == uuid_obj:
            return appointment
    return None

def list_appointments_for_client(client_id):
    """
    Returns a list of all appointments for a given client_id.
    """
    # Assuming client_id is a UUID or a string that can be directly compared
    client_appointments = []
    for appointment in appointments_db:
        if str(appointment.client_id) == str(client_id): # Compare as strings for safety
            client_appointments.append(appointment)
    return client_appointments

def list_appointments_for_order(order_id):
    """
    Returns a list of all appointments related to a given order_id.
    """
    # Assuming order_id is a UUID or a string that can be directly compared
    order_appointments = []
    for appointment in appointments_db:
        if str(appointment.order_id) == str(order_id): # Compare as strings for safety
            order_appointments.append(appointment)
    return order_appointments

def list_appointments_in_range(range_start_time, range_end_time):
    """
    Returns a list of all appointments that fall within or overlap with the given time range.
    An appointment overlaps if its start_time is before range_end_time AND its end_time is after range_start_time.
    """
    if not isinstance(range_start_time, datetime) or not isinstance(range_end_time, datetime):
        raise ValueError("range_start_time and range_end_time must be datetime objects.")
    if range_end_time <= range_start_time:
        raise ValueError("range_end_time must be after range_start_time.")

    overlapping_appointments = []
    for appointment in appointments_db:
        # Check for overlap:
        # (ApptStart < RangeEnd) and (ApptEnd > RangeStart)
        if appointment.start_time < range_end_time and appointment.end_time > range_start_time:
            overlapping_appointments.append(appointment)
    return overlapping_appointments

def list_all_appointments():
    """
    Returns the appointments_db list.
    """
    return appointments_db

def update_appointment(appointment_id, start_time=None, end_time=None, title=None, 
                       client_id=None, order_id=None, description=None, location=None, 
                       appointment_type=None):
    """
    Finds the appointment by appointment_id.
    If found, updates the specified attributes. Ensures end_time remains after start_time if either is updated.
    Return the updated appointment object or None if not found.
    """
    appointment_to_update = get_appointment_by_id(appointment_id)
    if not appointment_to_update:
        return None

    current_start = appointment_to_update.start_time
    current_end = appointment_to_update.end_time

    if start_time is not None:
        if not isinstance(start_time, datetime):
            raise ValueError("start_time must be a datetime object.")
        current_start = start_time
    
    if end_time is not None:
        if not isinstance(end_time, datetime):
            raise ValueError("end_time must be a datetime object.")
        current_end = end_time

    if current_end <= current_start:
        raise ValueError("end_time must be after start_time.")

    if start_time is not None:
        appointment_to_update.start_time = start_time
    if end_time is not None:
        appointment_to_update.end_time = end_time
    if title is not None:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Title must be a non-empty string.")
        appointment_to_update.title = title
    if client_id is not None: # Allows setting client_id to None or a new value
        appointment_to_update.client_id = client_id
    if order_id is not None: # Allows setting order_id to None or a new value
        appointment_to_update.order_id = order_id
    if description is not None: # Allows setting description to None or a new value
        appointment_to_update.description = description
    if location is not None: # Allows setting location to None or a new value
        appointment_to_update.location = location
    if appointment_type is not None:
        if appointment_type not in Appointment.VALID_APPOINTMENT_TYPES:
            raise ValueError(f"Invalid appointment_type: {appointment_type}. Must be one of {Appointment.VALID_APPOINTMENT_TYPES}")
        appointment_to_update.appointment_type = appointment_type
        
    return appointment_to_update

def delete_appointment(appointment_id):
    """
    Finds and removes the appointment by appointment_id from appointments_db.
    Returns True if deletion was successful, False otherwise.
    """
    appointment_to_delete = get_appointment_by_id(appointment_id)
    if appointment_to_delete:
        appointments_db.remove(appointment_to_delete)
        return True
    return False
