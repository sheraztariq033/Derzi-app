import uuid
from datetime import datetime

class MeasurementTemplate:
    def __init__(self, name, fields, diagram_image_path=None, template_id=None):
        self.template_id = template_id if template_id is not None else uuid.uuid4()
        self.name = name
        self.fields = fields  # List of strings
        self.diagram_image_path = diagram_image_path

    def __repr__(self):
        return f"<MeasurementTemplate {self.template_id} - {self.name}>"

class CustomMeasurement:
    def __init__(self, order_id, client_id, measurements, notes=None, measurement_id=None, date_taken=None):
        self.measurement_id = measurement_id if measurement_id is not None else uuid.uuid4()
        self.order_id = order_id
        self.client_id = client_id
        self.measurements = measurements  # Dictionary
        self.date_taken = date_taken if date_taken is not None else datetime.now()
        self.notes = notes

    def __repr__(self):
        return f"<CustomMeasurement {self.measurement_id} - Order {self.order_id} - Client {self.client_id}>"
