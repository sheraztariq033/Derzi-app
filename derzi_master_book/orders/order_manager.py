from .models import Order
from datetime import datetime

orders_db = []

def add_order(client_id, deadline, measurements, style_details, attachments=None, price=None, status=Order.STATUS_PENDING):
    """
    Creates a new Order instance and adds it to the in-memory database.
    """
    if not isinstance(deadline, datetime):
        raise ValueError("Deadline must be a datetime object.")
        
    new_order = Order(
        client_id=client_id,
        deadline=deadline,
        measurements=measurements,
        style_details=style_details,
        attachments=attachments,
        price=price,
        status=status
    )
    orders_db.append(new_order)
    return new_order

def get_order_by_id(order_id):
    """
    Searches for an order by its order_id in the in-memory database.
    """
    for order in orders_db:
        if order.order_id == order_id:
            return order
    return None

def list_orders_by_client(client_id):
    """
    Returns a list of all orders for a given client_id.
    """
    client_orders = []
    for order in orders_db:
        if order.client_id == client_id:
            client_orders.append(order)
    return client_orders

def list_all_orders():
    """
    Returns the list of all orders in the in-memory database.
    """
    return orders_db

def update_order_status(order_id, new_status):
    """
    Updates an order's status in the in-memory database.
    Validates if new_status is one of the predefined statuses.
    """
    order_to_update = get_order_by_id(order_id)
    
    if order_to_update:
        if new_status in Order.VALID_STATUSES:
            order_to_update.status = new_status
            return order_to_update
        else:
            # Invalid status
            return None 
    return None # Order not found

def update_order_details(order_id, deadline=None, measurements=None, style_details=None, attachments=None, price=None):
    """
    Updates an order's details in the in-memory database.
    Only updates attributes for which a new value is provided.
    """
    order_to_update = get_order_by_id(order_id)
    
    if order_to_update:
        if deadline is not None:
            if not isinstance(deadline, datetime):
                raise ValueError("Deadline must be a datetime object.")
            order_to_update.deadline = deadline
        if measurements is not None:
            order_to_update.measurements = measurements
        if style_details is not None:
            order_to_update.style_details = style_details
        if attachments is not None:
            order_to_update.attachments = attachments
        if price is not None:
            order_to_update.price = price
        return order_to_update
    return None # Order not found

def delete_order(order_id):
    """
    Deletes an order from the in-memory database by its order_id.
    """
    order_to_delete = get_order_by_id(order_id)
            
    if order_to_delete:
        orders_db.remove(order_to_delete)
        return True
    return False
