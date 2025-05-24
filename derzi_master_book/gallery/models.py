import uuid
from datetime import date # Using date for upload_date

class PortfolioItem:
    def __init__(self, image_path, title=None, description=None, client_id=None, 
                 order_id=None, style_tags=None, is_public=False, item_id=None, upload_date=None):
        
        if not image_path or not isinstance(image_path, str):
            raise ValueError("image_path must be a non-empty string.")

        self.item_id = item_id if item_id is not None else uuid.uuid4()
        self.image_path = image_path
        self.title = title
        self.description = description
        self.client_id = client_id # Should be UUID in practice
        self.order_id = order_id # Should be UUID in practice
        self.style_tags = style_tags if style_tags is not None else []
        self.upload_date = upload_date if upload_date is not None else date.today()
        self.is_public = is_public

    def __repr__(self):
        return f"<PortfolioItem {self.item_id} - {self.title or 'Untitled'} - Path: {self.image_path}>"
