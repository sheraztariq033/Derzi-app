import uuid
from datetime import datetime
from derzi_master_book.clients.models import Client # Assuming Client model is needed for type hinting or future foreign key relations

class Order:
    # Status constants
    STATUS_PENDING = "Pending"
    STATUS_IN_PROGRESS = "In Progress"
    STATUS_READY_FOR_PICKUP = "Ready for Pickup"
    STATUS_DELIVERED = "Delivered"
    STATUS_CANCELLED = "Cancelled"
    
    VALID_STATUSES = [STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_READY_FOR_PICKUP, STATUS_DELIVERED, STATUS_CANCELLED]

    def __init__(self, client_id, deadline, measurements, style_details, attachments=None, price=None, status=STATUS_PENDING, order_id=None, order_date=None):
        self.order_id = order_id if order_id is not None else uuid.uuid4()
        self.client_id = client_id  # This would eventually be a foreign key to a Client instance
        self.order_date = order_date if order_date is not None else datetime.now()
        self.deadline = deadline # This should be a datetime object
        self.status = status
        self.measurements = measurements # Dictionary for now
        self.style_details = style_details
        self.attachments = attachments if attachments is not None else []
        self.price = price

    def __repr__(self):
        return f"<Order {self.order_id} - Client {self.client_id} - Status {self.status}>"
