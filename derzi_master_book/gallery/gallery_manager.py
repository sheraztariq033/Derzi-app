from .models import PortfolioItem
from datetime import date # Changed from datetime to date, as model uses date
import uuid

portfolio_items_db = []

def add_portfolio_item(image_path, title=None, description=None, client_id=None, 
                       order_id=None, style_tags=None, is_public=False):
    """
    Creates a new PortfolioItem instance and adds it to the in-memory database.
    """
    # Model's __init__ handles image_path validation and default values.
    new_item = PortfolioItem(
        image_path=image_path,
        title=title,
        description=description,
        client_id=client_id,
        order_id=order_id,
        style_tags=style_tags,
        is_public=is_public
    )
    portfolio_items_db.append(new_item)
    return new_item

def get_portfolio_item_by_id(item_id):
    """
    Searches for a portfolio item by its item_id in the in-memory database.
    """
    try:
        uuid_obj = uuid.UUID(str(item_id))
    except ValueError:
        return None # Not a valid UUID format
        
    for item in portfolio_items_db:
        if item.item_id == uuid_obj:
            return item
    return None

def get_portfolio_items_for_client(client_id):
    """
    Filters items by client_id.
    """
    # Assuming client_id is a UUID or a string that can be directly compared
    client_items = []
    for item in portfolio_items_db:
        if str(item.client_id) == str(client_id): # Compare as strings for safety
            client_items.append(item)
    return client_items

def get_portfolio_items_for_order(order_id):
    """
    Filters items by order_id.
    """
    # Assuming order_id is a UUID or a string that can be directly compared
    order_items = []
    for item in portfolio_items_db:
        if str(item.order_id) == str(order_id): # Compare as strings for safety
            order_items.append(item)
    return order_items

def get_portfolio_items_by_tag(tag):
    """
    Filters items by checking if tag is in style_tags.
    Assumes tag is a single string.
    """
    if not isinstance(tag, str):
        # Or raise ValueError, depending on desired strictness
        return [] 
        
    tagged_items = []
    for item in portfolio_items_db:
        if item.style_tags and tag in item.style_tags:
            tagged_items.append(item)
    return tagged_items

def list_all_portfolio_items():
    """
    Lists all items in the portfolio_items_db.
    """
    return portfolio_items_db

def list_public_portfolio_items():
    """
    Lists items where is_public is True.
    """
    public_items = []
    for item in portfolio_items_db:
        if item.is_public:
            public_items.append(item)
    return public_items

def update_portfolio_item(item_id, image_path=None, title=None, description=None, 
                          client_id=None, order_id=None, style_tags=None, is_public=None):
    """
    Updates item details for the given item_id.
    Only updates attributes for which a new value is provided.
    """
    item_to_update = get_portfolio_item_by_id(item_id)
    if not item_to_update:
        return None

    if image_path is not None:
        if not isinstance(image_path, str) or not image_path.strip():
            raise ValueError("image_path must be a non-empty string.")
        item_to_update.image_path = image_path
    if title is not None: # Allow setting to None (empty string might be better for 'clearing')
        item_to_update.title = title
    if description is not None: # Allow setting to None
        item_to_update.description = description
    if client_id is not None: # Allow setting to None
        item_to_update.client_id = client_id
    if order_id is not None: # Allow setting to None
        item_to_update.order_id = order_id
    if style_tags is not None:
        if not isinstance(style_tags, list) or not all(isinstance(t, str) for t in style_tags):
            raise ValueError("style_tags must be a list of strings.")
        item_to_update.style_tags = style_tags
    if is_public is not None:
        if not isinstance(is_public, bool):
            raise ValueError("is_public must be a boolean.")
        item_to_update.is_public = is_public
        
    # upload_date is not updated as per requirements
    return item_to_update

def delete_portfolio_item(item_id):
    """
    Removes an item from portfolio_items_db by its item_id.
    Returns True if deletion was successful, False otherwise.
    (Note: actual file deletion from storage is not handled here)
    """
    item_to_delete = get_portfolio_item_by_id(item_id)
    if item_to_delete:
        portfolio_items_db.remove(item_to_delete)
        return True
    return False
