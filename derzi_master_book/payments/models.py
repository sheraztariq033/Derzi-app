import uuid
from datetime import date, datetime # Using date for invoice_date, due_date, payment_date
from decimal import Decimal
from derzi_master_book.orders.models import Order # For type hinting or future use

class Invoice:
    # Status constants
    STATUS_DRAFT = "Draft"
    STATUS_SENT = "Sent"
    STATUS_PAID = "Paid"
    STATUS_PARTIAL = "Partial" # Added for clarity
    STATUS_OVERDUE = "Overdue"
    STATUS_CANCELLED = "Cancelled"
    
    VALID_STATUSES = [STATUS_DRAFT, STATUS_SENT, STATUS_PAID, STATUS_PARTIAL, STATUS_OVERDUE, STATUS_CANCELLED]

    def __init__(self, order_id, due_date, total_amount, invoice_id=None, invoice_date=None, status=STATUS_DRAFT, notes=None):
        if not isinstance(due_date, date):
            raise ValueError("due_date must be a date object.")
        if not isinstance(total_amount, Decimal):
            raise ValueError("total_amount must be a Decimal object.")
        if total_amount < Decimal('0.00'):
            raise ValueError("total_amount cannot be negative.")
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}. Must be one of {self.VALID_STATUSES}")

        self.invoice_id = invoice_id if invoice_id is not None else uuid.uuid4()
        self.order_id = order_id # Should be a UUID type in practice
        self.invoice_date = invoice_date if invoice_date is not None else date.today()
        self.due_date = due_date
        self.total_amount = total_amount
        self.status = status
        self.notes = notes

    def __repr__(self):
        return f"<Invoice {self.invoice_id} - Order {self.order_id} - Amount {self.total_amount} - Status {self.status}>"

class Payment:
    # Payment method constants
    METHOD_CASH = "Cash"
    METHOD_CREDIT_CARD = "Credit Card"
    METHOD_BANK_TRANSFER = "Bank Transfer"
    METHOD_OTHER = "Other"
    
    VALID_PAYMENT_METHODS = [METHOD_CASH, METHOD_CREDIT_CARD, METHOD_BANK_TRANSFER, METHOD_OTHER]

    def __init__(self, invoice_id, amount_paid, payment_method, payment_id=None, payment_date=None, transaction_id=None, notes=None):
        if not isinstance(amount_paid, Decimal):
            raise ValueError("amount_paid must be a Decimal object.")
        if amount_paid <= Decimal('0.00'): # Payments should be positive
            raise ValueError("amount_paid must be a positive value.")
        if payment_method not in self.VALID_PAYMENT_METHODS:
            raise ValueError(f"Invalid payment_method: {payment_method}. Must be one of {self.VALID_PAYMENT_METHODS}")

        self.payment_id = payment_id if payment_id is not None else uuid.uuid4()
        self.invoice_id = invoice_id # Should be a UUID type
        self.payment_date = payment_date if payment_date is not None else date.today()
        self.amount_paid = amount_paid
        self.payment_method = payment_method
        self.transaction_id = transaction_id
        self.notes = notes

    def __repr__(self):
        return f"<Payment {self.payment_id} - Invoice {self.invoice_id} - Amount {self.amount_paid} - Method {self.payment_method}>"
