import unittest
import uuid
from datetime import date, datetime, timedelta # Using date for model, datetime for order deadline

from derzi_master_book.gallery.models import PortfolioItem
from derzi_master_book.gallery import gallery_manager

# For linked dummy data
from derzi_master_book.clients.models import Client
from derzi_master_book.clients import client_manager
from derzi_master_book.orders.models import Order
from derzi_master_book.orders import order_manager

class TestGalleryManager(unittest.TestCase):

    def setUp(self):
        """Clear databases and set up dummy data before each test."""
        gallery_manager.portfolio_items_db = []
        client_manager.clients_db = []
        order_manager.orders_db = []

        # Create dummy client and order for use in PortfolioItem tests
        self.test_client = client_manager.add_client(name="Test Client G", phone_number="555666777")
        self.test_client_id = self.test_client.client_id

        self.another_client = client_manager.add_client(name="Another Client G", phone_number="888999000")
        self.another_client_id = self.another_client.client_id
        
        self.test_order = order_manager.add_order(
            client_id=self.test_client_id,
            deadline=datetime.now() + timedelta(days=20), # Using datetime for order
            measurements={"sample_gallery": "data"},
            style_details="Test Order for Gallery Item"
        )
        self.test_order_id = self.test_order.order_id

        self.another_order = order_manager.add_order(
            client_id=self.another_client_id,
            deadline=datetime.now() + timedelta(days=22), # Using datetime for order
            measurements={},
            style_details="Another Test Order for Gallery"
        )
        self.another_order_id = self.another_order.order_id

    def _create_sample_item_data(self, **kwargs):
        """Helper to create sample portfolio item data with defaults."""
        data = {
            "image_path": "path/to/default_image.jpg",
            "title": "Default Title",
            "description": "Default description.",
            "client_id": self.test_client_id,
            "order_id": self.test_order_id,
            "style_tags": ["default", "sample"],
            "is_public": False,
        }
        data.update(kwargs)
        return data

    def test_add_portfolio_item(self):
        """Test adding a new portfolio item."""
        sample_data = self._create_sample_item_data()
        
        item = gallery_manager.add_portfolio_item(**sample_data)
        
        self.assertIsInstance(item, PortfolioItem)
        self.assertEqual(item.image_path, sample_data["image_path"])
        self.assertEqual(item.title, sample_data["title"])
        self.assertEqual(item.description, sample_data["description"])
        self.assertEqual(item.client_id, sample_data["client_id"])
        self.assertEqual(item.order_id, sample_data["order_id"])
        self.assertEqual(item.style_tags, sample_data["style_tags"])
        self.assertEqual(item.is_public, sample_data["is_public"])
        self.assertIsInstance(item.item_id, uuid.UUID)
        self.assertIsInstance(item.upload_date, date) # Model uses date
        self.assertEqual(item.upload_date, date.today())
        
        self.assertIn(item, gallery_manager.portfolio_items_db)
        self.assertEqual(len(gallery_manager.portfolio_items_db), 1)

        # Test adding with minimal required field (image_path)
        minimal_item = gallery_manager.add_portfolio_item(image_path="minimal/image.png")
        self.assertEqual(len(gallery_manager.portfolio_items_db), 2)
        self.assertEqual(minimal_item.image_path, "minimal/image.png")
        self.assertIsNone(minimal_item.title) # Default for model
        self.assertEqual(minimal_item.style_tags, []) # Default for model
        self.assertFalse(minimal_item.is_public) # Default for model

        # Test for ValueError if image_path is missing or invalid (model validation)
        with self.assertRaises(ValueError):
            gallery_manager.add_portfolio_item(image_path="") # Empty path
        with self.assertRaises(TypeError): # Missing image_path
            gallery_manager.add_portfolio_item(title="No Image Item")

    def test_get_portfolio_item_by_id(self):
        """Test retrieving a portfolio item by its ID."""
        item1_data = self._create_sample_item_data(image_path="item1.jpg")
        item1 = gallery_manager.add_portfolio_item(**item1_data)
        
        retrieved_item = gallery_manager.get_portfolio_item_by_id(item1.item_id)
        self.assertEqual(retrieved_item, item1)
        
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(gallery_manager.get_portfolio_item_by_id(non_existent_uuid))
        self.assertIsNone(gallery_manager.get_portfolio_item_by_id("not-a-uuid-string"))

    def test_get_portfolio_items_for_client(self):
        """Test retrieving portfolio items for a specific client_id."""
        item1 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(client_id=self.test_client_id, image_path="c1_item1.jpg"))
        item2 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(client_id=self.another_client_id, image_path="c2_item1.jpg"))
        item3 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(client_id=self.test_client_id, image_path="c1_item2.jpg"))

        client1_items = gallery_manager.get_portfolio_items_for_client(self.test_client_id)
        self.assertEqual(len(client1_items), 2)
        self.assertIn(item1, client1_items)
        self.assertIn(item3, client1_items)
        self.assertNotIn(item2, client1_items)
        
        # Test with a client_id that has no items
        yet_another_client_id = uuid.uuid4() 
        self.assertEqual(gallery_manager.get_portfolio_items_for_client(yet_another_client_id), [])

    def test_get_portfolio_items_for_order(self):
        """Test retrieving portfolio items for a specific order_id."""
        item1 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(order_id=self.test_order_id, image_path="o1_item1.jpg"))
        item2 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(order_id=self.another_order_id, image_path="o2_item1.jpg"))
        item3 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(order_id=self.test_order_id, image_path="o1_item2.jpg"))

        order1_items = gallery_manager.get_portfolio_items_for_order(self.test_order_id)
        self.assertEqual(len(order1_items), 2)
        self.assertIn(item1, order1_items)
        self.assertIn(item3, order1_items)
        self.assertNotIn(item2, order1_items)

        # Test with an order_id that has no items
        yet_another_order_id = uuid.uuid4()
        self.assertEqual(gallery_manager.get_portfolio_items_for_order(yet_another_order_id), [])

    def test_get_portfolio_items_by_tag(self):
        """Test retrieving portfolio items by a specific style_tag."""
        item1 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(style_tags=["casual", "shirt"], image_path="tag_item1.jpg"))
        item2 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(style_tags=["formal", "suit"], image_path="tag_item2.jpg"))
        item3 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(style_tags=["casual", "dress"], image_path="tag_item3.jpg"))
        item4 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(style_tags=[], image_path="no_tags.jpg")) # No tags
        item5 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(style_tags=None, image_path="none_tags.jpg")) # Tags is None

        # Test tag "casual"
        casual_items = gallery_manager.get_portfolio_items_by_tag("casual")
        self.assertEqual(len(casual_items), 2)
        self.assertIn(item1, casual_items)
        self.assertIn(item3, casual_items)
        self.assertNotIn(item2, casual_items)

        # Test tag "suit"
        suit_items = gallery_manager.get_portfolio_items_by_tag("suit")
        self.assertEqual(len(suit_items), 1)
        self.assertIn(item2, suit_items)

        # Test tag that matches no items
        non_existent_tag_items = gallery_manager.get_portfolio_items_by_tag("nonexistenttag")
        self.assertEqual(len(non_existent_tag_items), 0)
        
        # Test with non-string tag (should return empty list as per manager implementation)
        self.assertEqual(gallery_manager.get_portfolio_items_by_tag(123), [])

    def test_list_all_portfolio_items(self):
        """Test listing all portfolio items."""
        self.assertEqual(gallery_manager.list_all_portfolio_items(), []) # Empty DB
        
        item1 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(image_path="all1.jpg"))
        item2 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(image_path="all2.jpg"))
        
        all_items = gallery_manager.list_all_portfolio_items()
        self.assertEqual(len(all_items), 2)
        self.assertIn(item1, all_items)
        self.assertIn(item2, all_items)

    def test_list_public_portfolio_items(self):
        """Test listing only public portfolio items."""
        item1 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(is_public=True, image_path="public1.jpg"))
        item2 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(is_public=False, image_path="private1.jpg"))
        item3 = gallery_manager.add_portfolio_item(**self._create_sample_item_data(is_public=True, image_path="public2.jpg"))
        
        public_items = gallery_manager.list_public_portfolio_items()
        self.assertEqual(len(public_items), 2)
        self.assertIn(item1, public_items)
        self.assertIn(item3, public_items)
        self.assertNotIn(item2, public_items)

        # Test with no public items
        gallery_manager.portfolio_items_db = [] # Clear
        gallery_manager.add_portfolio_item(**self._create_sample_item_data(is_public=False, image_path="private_only.jpg"))
        self.assertEqual(gallery_manager.list_public_portfolio_items(), [])

    def test_update_portfolio_item(self):
        """Test updating a portfolio item's information."""
        item_data = self._create_sample_item_data(title="Original Title", style_tags=["old_tag"])
        item = gallery_manager.add_portfolio_item(**item_data)
        original_id = item.item_id
        original_upload_date = item.upload_date # Should not change

        new_image_path = "updated/image.png"
        new_title = "Updated Title"
        new_desc = "Updated item description."
        new_tags = ["new_tag", "updated_tag"]
        new_is_public = True

        updated_item = gallery_manager.update_portfolio_item(
            item_id=original_id,
            image_path=new_image_path,
            title=new_title,
            description=new_desc,
            style_tags=new_tags,
            is_public=new_is_public
            # client_id and order_id can also be updated if needed
        )
        self.assertIsNotNone(updated_item)
        self.assertEqual(updated_item.image_path, new_image_path)
        self.assertEqual(updated_item.title, new_title)
        self.assertEqual(updated_item.description, new_desc)
        self.assertEqual(updated_item.style_tags, new_tags)
        self.assertEqual(updated_item.is_public, new_is_public)
        self.assertEqual(updated_item.item_id, original_id)
        self.assertEqual(updated_item.upload_date, original_upload_date)

        # Test updating a non-existent item
        non_existent_uuid = uuid.uuid4()
        self.assertIsNone(gallery_manager.update_portfolio_item(non_existent_uuid, title="Ghost Item"))

        # Test for ValueError if image_path is updated to an invalid value
        with self.assertRaises(ValueError):
            gallery_manager.update_portfolio_item(original_id, image_path="")
            
        # Test for ValueError if style_tags is not a list of strings
        with self.assertRaises(ValueError):
            gallery_manager.update_portfolio_item(original_id, style_tags=["valid", 123])
            
        # Test for ValueError if is_public is not boolean
        with self.assertRaises(ValueError):
            gallery_manager.update_portfolio_item(original_id, is_public="not-a-bool")


    def test_delete_portfolio_item(self):
        """Test deleting a portfolio item."""
        item_data = self._create_sample_item_data(image_path="to_delete.jpg")
        item = gallery_manager.add_portfolio_item(**item_data)
        item_id_to_delete = item.item_id
        
        self.assertIn(item, gallery_manager.portfolio_items_db)
        
        delete_result = gallery_manager.delete_portfolio_item(item_id_to_delete)
        self.assertTrue(delete_result)
        
        self.assertNotIn(item, gallery_manager.portfolio_items_db)
        self.assertIsNone(gallery_manager.get_portfolio_item_by_id(item_id_to_delete))
        
        # Test deleting a non-existent item
        non_existent_uuid = uuid.uuid4()
        delete_non_existent_result = gallery_manager.delete_portfolio_item(non_existent_uuid)
        self.assertFalse(delete_non_existent_result)

    def tearDown(self):
        """Clean up databases after each test."""
        gallery_manager.portfolio_items_db = []
        client_manager.clients_db = []
        order_manager.orders_db = []

if __name__ == '__main__':
    unittest.main()
