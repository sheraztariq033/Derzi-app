from .models import MeasurementTemplate, CustomMeasurement
from datetime import datetime
import uuid # Required for type checking if an ID is a valid UUID

measurement_templates_db = []
custom_measurements_db = []

# --- Measurement Template Management ---

def add_measurement_template(name, fields, diagram_image_path=None):
    """
    Creates a new MeasurementTemplate instance and adds it to the in-memory database.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Template name must be a non-empty string.")
    if not isinstance(fields, list) or not all(isinstance(f, str) for f in fields) or not fields:
        raise ValueError("Fields must be a non-empty list of strings.")
        
    new_template = MeasurementTemplate(name=name, fields=fields, diagram_image_path=diagram_image_path)
    measurement_templates_db.append(new_template)
    return new_template

def get_measurement_template_by_id(template_id):
    """
    Searches for a measurement template by its template_id in the in-memory database.
    """
    try:
        uuid_obj = uuid.UUID(str(template_id)) # Validate if template_id is a valid UUID
    except ValueError:
        return None # Not a valid UUID format
        
    for template in measurement_templates_db:
        if template.template_id == uuid_obj:
            return template
    return None

def list_all_measurement_templates():
    """
    Returns the list of all measurement templates in the in-memory database.
    """
    return measurement_templates_db

def update_measurement_template(template_id, name=None, fields=None, diagram_image_path=None):
    """
    Updates a measurement template's information in the in-memory database.
    Only updates attributes for which a new value is provided.
    """
    try:
        uuid_obj = uuid.UUID(str(template_id))
    except ValueError:
        return None
        
    template_to_update = get_measurement_template_by_id(uuid_obj)
    
    if template_to_update:
        if name is not None:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Template name must be a non-empty string.")
            template_to_update.name = name
        if fields is not None:
            if not isinstance(fields, list) or not all(isinstance(f, str) for f in fields) or not fields:
                raise ValueError("Fields must be a non-empty list of strings.")
            template_to_update.fields = fields
        if diagram_image_path is not None: # Allow setting to None or a new path
            template_to_update.diagram_image_path = diagram_image_path
        return template_to_update
    return None

def delete_measurement_template(template_id):
    """
    Deletes a measurement template from the in-memory database by its template_id.
    """
    try:
        uuid_obj = uuid.UUID(str(template_id))
    except ValueError:
        return False # Invalid UUID format, so cannot be deleted
        
    template_to_delete = get_measurement_template_by_id(uuid_obj)
            
    if template_to_delete:
        measurement_templates_db.remove(template_to_delete)
        return True
    return False

# --- Custom Measurement Management ---

def add_custom_measurement(order_id, client_id, measurements, notes=None):
    """
    Creates a new CustomMeasurement instance and adds it to the in-memory database.
    """
    if not measurements or not isinstance(measurements, dict):
        raise ValueError("Measurements must be a non-empty dictionary.")
    # Further validation for order_id and client_id can be added if they are expected to be UUIDs
    # For now, they are treated as strings as per the problem description (can link to Order/Client)

    new_measurement = CustomMeasurement(
        order_id=order_id,
        client_id=client_id,
        measurements=measurements,
        notes=notes
    )
    custom_measurements_db.append(new_measurement)
    return new_measurement

def get_custom_measurement_by_id(measurement_id):
    """
    Searches for custom measurements by its measurement_id in the in-memory database.
    """
    try:
        uuid_obj = uuid.UUID(str(measurement_id))
    except ValueError:
        return None
        
    for measurement in custom_measurements_db:
        if measurement.measurement_id == uuid_obj:
            return measurement
    return None

def get_custom_measurements_for_order(order_id):
    """
    Retrieves all custom measurements for a specific order_id.
    """
    # Assuming order_id is a UUID or a string that can be directly compared
    order_measurements = []
    for measurement in custom_measurements_db:
        if str(measurement.order_id) == str(order_id): # Compare as strings to be safe
            order_measurements.append(measurement)
    return order_measurements

def get_custom_measurements_for_client(client_id):
    """
    Retrieves all custom measurements for a specific client_id.
    """
    # Assuming client_id is a UUID or a string that can be directly compared
    client_measurements = []
    for measurement in custom_measurements_db:
        if str(measurement.client_id) == str(client_id): # Compare as strings
            client_measurements.append(measurement)
    return client_measurements

def update_custom_measurement(measurement_id, measurements=None, notes=None):
    """
    Updates specific custom measurement entries in the in-memory database.
    """
    try:
        uuid_obj = uuid.UUID(str(measurement_id))
    except ValueError:
        return None

    measurement_to_update = get_custom_measurement_by_id(uuid_obj)
    
    if measurement_to_update:
        if measurements is not None:
            if not measurements or not isinstance(measurements, dict):
                raise ValueError("Measurements must be a non-empty dictionary.")
            measurement_to_update.measurements = measurements
        if notes is not None: # Allow setting notes to None or a new string
            measurement_to_update.notes = notes
        # date_taken is not updated as per requirements
        return measurement_to_update
    return None

def delete_custom_measurement(measurement_id):
    """
    Deletes a custom measurement entry from the in-memory database by its measurement_id.
    """
    try:
        uuid_obj = uuid.UUID(str(measurement_id))
    except ValueError:
        return False
        
    measurement_to_delete = get_custom_measurement_by_id(uuid_obj)
            
    if measurement_to_delete:
        custom_measurements_db.remove(measurement_to_delete)
        return True
    return False
