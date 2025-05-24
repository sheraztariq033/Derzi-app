import uuid
from datetime import datetime

class Client:
    def __init__(self, name, phone_number, email=None, address=None, client_id=None, creation_date=None):
        self.client_id = client_id if client_id is not None else uuid.uuid4()
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.address = address
        self.creation_date = creation_date if creation_date is not None else datetime.now()

    def __repr__(self):
        return f"<Client {self.client_id} - {self.name}>"
