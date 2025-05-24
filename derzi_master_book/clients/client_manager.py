from .models import Client

clients_db = []

def add_client(name, phone_number, email=None, address=None):
    """
    Creates a new Client instance and adds it to the in-memory database.
    """
    new_client = Client(name=name, phone_number=phone_number, email=email, address=address)
    clients_db.append(new_client)
    return new_client

def get_client_by_id(client_id):
    """
    Searches for a client by their client_id in the in-memory database.
    """
    for client in clients_db:
        if client.client_id == client_id:
            return client
    return None

def list_all_clients():
    """
    Returns the list of all clients in the in-memory database.
    """
    return clients_db

def update_client(client_id, name=None, phone_number=None, email=None, address=None):
    """
    Updates a client's information in the in-memory database.
    Only updates attributes for which a new value is provided.
    """
    client_to_update = None
    for client in clients_db:
        if client.client_id == client_id:
            client_to_update = client
            break
    
    if client_to_update:
        if name is not None:
            client_to_update.name = name
        if phone_number is not None:
            client_to_update.phone_number = phone_number
        if email is not None:
            client_to_update.email = email
        if address is not None:
            client_to_update.address = address
        return client_to_update
    return None

def delete_client(client_id):
    """
    Deletes a client from the in-memory database by their client_id.
    """
    client_to_delete = None
    for client in clients_db:
        if client.client_id == client_id:
            client_to_delete = client
            break
            
    if client_to_delete:
        clients_db.remove(client_to_delete)
        return True
    return False
