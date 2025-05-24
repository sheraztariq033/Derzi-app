from .models import Invoice, Payment
from derzi_master_book.orders.models import Order # For fetching order details
from derzi_master_book.orders.order_manager import get_order_by_id as get_order_by_id_from_order_manager # To get order price

from datetime import date, datetime
import uuid
from decimal import Decimal

invoices_db = []
payments_db = []

# --- Invoice Functions ---

def create_invoice_for_order(order_id, due_date, notes=None):
    """
    Creates an Invoice for a given order_id.
    Fetches order price to set as total_amount.
    """
    # In a real app, you'd fetch the order from order_manager or a shared data service.
    # For now, we'll assume a function get_order_by_id_from_order_manager exists and can be used.
    order_instance = get_order_by_id_from_order_manager(order_id) 

    if not order_instance:
        raise ValueError(f"Order with ID {order_id} not found.")
    
    if order_instance.price is None:
        raise ValueError(f"Order {order_id} does not have a price set. Cannot create invoice.")

    # Ensure order_instance.price is a Decimal
    order_total_amount = Decimal(str(order_instance.price))

    new_invoice = Invoice(
        order_id=order_id, 
        due_date=due_date, 
        total_amount=order_total_amount, 
        notes=notes,
        status=Invoice.STATUS_DRAFT # Initial status
    )
    invoices_db.append(new_invoice)
    return new_invoice

def get_invoice_by_id(invoice_id):
    """
    Searches for an invoice by its invoice_id.
    """
    try:
        uuid_obj = uuid.UUID(str(invoice_id))
    except ValueError:
        return None
    for invoice in invoices_db:
        if invoice.invoice_id == uuid_obj:
            return invoice
    return None

def get_invoices_for_order(order_id):
    """
    Returns a list of all invoices for a given order_id.
    """
    # Assuming order_id is a UUID or string
    order_invoices = []
    for invoice in invoices_db:
        if str(invoice.order_id) == str(order_id):
            order_invoices.append(invoice)
    return order_invoices

def list_all_invoices():
    """
    Returns the list of all invoices.
    """
    return invoices_db

def update_invoice_status(invoice_id, new_status):
    """
    Updates an invoice's status. Validates new_status.
    """
    invoice_to_update = get_invoice_by_id(invoice_id)
    if not invoice_to_update:
        return None
    
    if new_status not in Invoice.VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status}. Must be one of {Invoice.VALID_STATUSES}")
    
    invoice_to_update.status = new_status
    return invoice_to_update

def update_invoice_details(invoice_id, due_date=None, notes=None):
    """
    Updates an invoice's due_date or notes.
    """
    invoice_to_update = get_invoice_by_id(invoice_id)
    if not invoice_to_update:
        return None

    if due_date is not None:
        if not isinstance(due_date, date):
            raise ValueError("due_date must be a date object.")
        invoice_to_update.due_date = due_date
    if notes is not None: # Allows setting notes to None or a new value
        invoice_to_update.notes = notes
    return invoice_to_update

def delete_invoice(invoice_id):
    """
    Deletes an invoice by its invoice_id.
    Also deletes associated payments.
    """
    invoice_to_delete = get_invoice_by_id(invoice_id)
    if not invoice_to_delete:
        return False
    
    # Also delete associated payments
    payments_for_invoice = get_payments_for_invoice(invoice_id)
    for payment in payments_for_invoice:
        payments_db.remove(payment)
        
    invoices_db.remove(invoice_to_delete)
    return True

# --- Payment Functions ---

def add_payment_to_invoice(invoice_id, amount_paid, payment_method, transaction_id=None, notes=None):
    """
    Adds a payment record to an invoice.
    """
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        raise ValueError(f"Invoice with ID {invoice_id} not found.")

    # amount_paid should be Decimal, model handles this
    new_payment = Payment(
        invoice_id=invoice_id,
        amount_paid=amount_paid,
        payment_method=payment_method,
        transaction_id=transaction_id,
        notes=notes
    )
    payments_db.append(new_payment)
    
    # Placeholder for updating invoice status based on payment
    # calculate_invoice_status_after_payment(invoice_id)
    
    return new_payment

def get_payment_by_id(payment_id):
    """
    Searches for a payment by its payment_id.
    """
    try:
        uuid_obj = uuid.UUID(str(payment_id))
    except ValueError:
        return None
    for payment in payments_db:
        if payment.payment_id == uuid_obj:
            return payment
    return None

def get_payments_for_invoice(invoice_id):
    """
    Returns a list of all payments for a given invoice_id.
    """
    # Assuming invoice_id is a UUID or string
    invoice_payments = []
    for payment in payments_db:
        if str(payment.invoice_id) == str(invoice_id):
            invoice_payments.append(payment)
    return invoice_payments

def list_all_payments():
    """
    Returns the list of all payments.
    """
    return payments_db

def update_payment_details(payment_id, amount_paid=None, payment_method=None, transaction_id=None, notes=None):
    """
    Updates a payment's details.
    """
    payment_to_update = get_payment_by_id(payment_id)
    if not payment_to_update:
        return None

    if amount_paid is not None:
        if not isinstance(amount_paid, Decimal):
            raise ValueError("amount_paid must be a Decimal object.")
        if amount_paid <= Decimal('0.00'):
            raise ValueError("amount_paid must be a positive value.")
        payment_to_update.amount_paid = amount_paid
    
    if payment_method is not None:
        if payment_method not in Payment.VALID_PAYMENT_METHODS:
            raise ValueError(f"Invalid payment_method: {payment_method}. Must be one of {Payment.VALID_PAYMENT_METHODS}")
        payment_to_update.payment_method = payment_method
        
    if transaction_id is not None: # Allows setting to None or new value
        payment_to_update.transaction_id = transaction_id
    if notes is not None: # Allows setting to None or new value
        payment_to_update.notes = notes
        
    # If amount_paid was changed, the linked invoice status might need recalculation.
    # calculate_invoice_status_after_payment(payment_to_update.invoice_id)
    
    return payment_to_update

def delete_payment(payment_id):
    """
    Deletes a payment by its payment_id.
    """
    payment_to_delete = get_payment_by_id(payment_id)
    if not payment_to_delete:
        return False
    
    invoice_id_of_deleted_payment = payment_to_delete.invoice_id
    payments_db.remove(payment_to_delete)
    
    # After deleting a payment, the linked invoice status might need recalculation.
    # calculate_invoice_status_after_payment(invoice_id_of_deleted_payment)
    
    return True

# --- Helper for Invoice Status (Conceptual) ---
def calculate_invoice_status_after_payment(invoice_id):
    """
    Calculates and updates the invoice status based on its total amount and sum of payments.
    This is a more advanced feature and is simplified here.
    """
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        return

    if invoice.status == Invoice.STATUS_CANCELLED: # Don't update cancelled invoices
        return

    payments = get_payments_for_invoice(invoice_id)
    total_paid = sum(p.amount_paid for p in payments)

    if total_paid >= invoice.total_amount:
        update_invoice_status(invoice_id, Invoice.STATUS_PAID)
    elif total_paid > Decimal('0.00') and total_paid < invoice.total_amount:
        update_invoice_status(invoice_id, Invoice.STATUS_PARTIAL)
    elif total_paid == Decimal('0.00'):
        # If no payments, check due_date to set to Overdue or keep as Draft/Sent
        if invoice.due_date < date.today() and invoice.status not in [Invoice.STATUS_DRAFT, Invoice.STATUS_SENT]:
             update_invoice_status(invoice_id, Invoice.STATUS_OVERDUE)
        elif invoice.status == Invoice.STATUS_PAID or invoice.status == Invoice.STATUS_PARTIAL : # if it was paid/partial and now 0, it becomes draft or sent
            update_invoice_status(invoice_id, Invoice.STATUS_SENT) # Or Draft, depending on workflow
    # Note: STATUS_OVERDUE logic might need to be triggered by a separate daily task or when viewing an invoice
    # For now, if it's not paid or partial, and no payments, it remains its current status or becomes overdue.
    # A more robust system would handle the DRAFT -> SENT -> OVERDUE transitions more explicitly.
    
    # This is a basic implementation. A full implementation would need more robust logic
    # for status transitions (e.g., handling DRAFT, SENT states before PAID/PARTIAL/OVERDUE).
    print(f"Conceptual: Recalculated status for invoice {invoice_id} based on payments. Total paid: {total_paid}")

# Example of how it might be integrated:
# In add_payment_to_invoice:
#   ...
#   payments_db.append(new_payment)
#   calculate_invoice_status_after_payment(invoice.invoice_id) # Call the helper
#   return new_payment

# In update_payment_details:
#   ...
#   if amount_paid is not None:
#       payment_to_update.amount_paid = amount_paid
#       calculate_invoice_status_after_payment(payment_to_update.invoice_id) # Call helper
#   ...

# In delete_payment:
#   ...
#   payments_db.remove(payment_to_delete)
#   calculate_invoice_status_after_payment(invoice_id_of_deleted_payment) # Call helper
#   return True
