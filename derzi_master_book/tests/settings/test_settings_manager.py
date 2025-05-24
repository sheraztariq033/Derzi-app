import unittest
import os
import json
import shutil # For cleaning up the data directory if needed, though file deletion should suffice

from derzi_master_book.settings.models import AppSettings
from derzi_master_book.settings import settings_manager

class TestSettingsManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary test settings file and override the manager's path."""
        self.test_data_dir = "derzi_master_book/data" # Ensure this exists from previous steps
        self.test_settings_file = os.path.join(self.test_data_dir, "test_app_settings.json")
        
        # Store original path and current_settings state
        self.original_settings_file_path = settings_manager.SETTINGS_FILE_PATH
        self.original_current_settings = settings_manager.current_settings

        # Override with test path
        settings_manager.SETTINGS_FILE_PATH = self.test_settings_file
        settings_manager.current_settings = None # Reset to ensure it loads from the new path

        # Clean up any existing test file before each test
        if os.path.exists(self.test_settings_file):
            os.remove(self.test_settings_file)

    def tearDown(self):
        """Clean up the test settings file and restore original manager state."""
        if os.path.exists(self.test_settings_file):
            os.remove(self.test_settings_file)
        
        # Restore original path and settings state
        settings_manager.SETTINGS_FILE_PATH = self.original_settings_file_path
        settings_manager.current_settings = self.original_current_settings # Or None, depending on desired global state after tests

    def test_load_settings_new_file(self):
        """Test loading settings when the settings file does not exist."""
        self.assertFalse(os.path.exists(self.test_settings_file))
        
        loaded_settings = settings_manager.load_settings()
        
        self.assertTrue(os.path.exists(self.test_settings_file))
        self.assertIsInstance(loaded_settings, AppSettings)
        
        # Check default values
        default_app_settings = AppSettings()
        self.assertEqual(loaded_settings.theme, default_app_settings.theme)
        self.assertEqual(loaded_settings.language, default_app_settings.language)
        self.assertEqual(loaded_settings.backup_enabled, default_app_settings.backup_enabled)
        self.assertIsNone(loaded_settings.backup_location) # Default is None
        self.assertIsNone(loaded_settings.sync_frequency_hours) # Default is None

        # Verify the file content matches default settings
        with open(self.test_settings_file, 'r') as f:
            data_from_file = json.load(f)
        self.assertEqual(data_from_file["theme"], default_app_settings.theme)

    def test_load_settings_existing_file(self):
        """Test loading settings from an existing, valid settings file."""
        custom_settings_data = {
            "theme": AppSettings.THEME_DARK,
            "language": AppSettings.LANG_TURKISH,
            "backup_enabled": True,
            "backup_location": "/test/backup",
            "sync_frequency_hours": 12
        }
        with open(self.test_settings_file, 'w') as f:
            json.dump(custom_settings_data, f)
            
        loaded_settings = settings_manager.load_settings()
        
        self.assertEqual(loaded_settings.theme, custom_settings_data["theme"])
        self.assertEqual(loaded_settings.language, custom_settings_data["language"])
        self.assertEqual(loaded_settings.backup_enabled, custom_settings_data["backup_enabled"])
        self.assertEqual(loaded_settings.backup_location, custom_settings_data["backup_location"])
        self.assertEqual(loaded_settings.sync_frequency_hours, custom_settings_data["sync_frequency_hours"])

    def test_load_settings_invalid_json_file(self):
        """Test loading settings when the file contains invalid JSON."""
        with open(self.test_settings_file, 'w') as f:
            f.write("this is not valid json")
            
        loaded_settings = settings_manager.load_settings() # Should handle error and use defaults
        
        self.assertTrue(os.path.exists(self.test_settings_file)) # File should be overwritten with defaults
        default_app_settings = AppSettings()
        self.assertEqual(loaded_settings.theme, default_app_settings.theme)
        self.assertEqual(loaded_settings.language, default_app_settings.language)

        # Verify the file content is now default settings
        with open(self.test_settings_file, 'r') as f:
            data_from_file = json.load(f)
        self.assertEqual(data_from_file["theme"], default_app_settings.theme)


    def test_save_settings(self):
        """Test saving settings to the file."""
        settings = settings_manager.load_settings() # Initializes file with defaults
        
        # Modify a setting directly on the current_settings object
        settings_manager.current_settings.theme = AppSettings.THEME_DARK
        settings_manager.current_settings.language = AppSettings.LANG_FRENCH
        
        settings_manager.save_settings()
        
        # Read the file directly and verify content
        with open(self.test_settings_file, 'r') as f:
            saved_data = json.load(f)
            
        self.assertEqual(saved_data["theme"], AppSettings.THEME_DARK)
        self.assertEqual(saved_data["language"], AppSettings.LANG_FRENCH)
        self.assertEqual(saved_data["settings_id"], AppSettings.DEFAULT_SETTINGS_ID) # Ensure ID is saved

    def test_get_settings(self):
        """Test the get_settings function for loading and returning the same instance."""
        settings_instance1 = settings_manager.get_settings()
        self.assertIsInstance(settings_instance1, AppSettings)
        
        # File should exist now (created by first call to get_settings -> load_settings)
        self.assertTrue(os.path.exists(self.test_settings_file))
        
        settings_instance2 = settings_manager.get_settings()
        self.assertIs(settings_instance1, settings_instance2, "get_settings should return the same instance")

    def test_update_setting(self):
        """Test updating a specific setting using update_setting."""
        settings_manager.load_settings() # Ensure settings are loaded and file exists

        updated_settings = settings_manager.update_setting("theme", AppSettings.THEME_LIGHT)
        self.assertIsNotNone(updated_settings)
        self.assertEqual(settings_manager.current_settings.theme, AppSettings.THEME_LIGHT)
        
        # Verify change is saved to file
        with open(self.test_settings_file, 'r') as f:
            data_from_file = json.load(f)
        self.assertEqual(data_from_file["theme"], AppSettings.THEME_LIGHT)

        # Test updating language
        settings_manager.update_setting("language", AppSettings.LANG_TURKISH)
        self.assertEqual(settings_manager.current_settings.language, AppSettings.LANG_TURKISH)
        with open(self.test_settings_file, 'r') as f:
            data_from_file = json.load(f)
        self.assertEqual(data_from_file["language"], AppSettings.LANG_TURKISH)

        # Test updating with an invalid key
        no_change_settings = settings_manager.update_setting("non_existent_key", "some_value")
        self.assertIsNone(no_change_settings, "update_setting should return None for invalid key")
        # Ensure other settings didn't change unexpectedly
        self.assertEqual(settings_manager.current_settings.language, AppSettings.LANG_TURKISH)


        # Test updating with an invalid value for a valid key
        # Manager's update_setting returns None if validation fails (e.g. theme not in VALID_THEMES)
        invalid_update_result = settings_manager.update_setting("theme", "invalid_theme_value")
        self.assertIsNone(invalid_update_result)
        # Theme should remain as it was (LIGHT from earlier update)
        self.assertEqual(settings_manager.current_settings.theme, AppSettings.THEME_LIGHT)
        with open(self.test_settings_file, 'r') as f:
            data_from_file = json.load(f)
        self.assertEqual(data_from_file["theme"], AppSettings.THEME_LIGHT) # Not changed to invalid

    def test_convenience_getters_setters(self):
        """Test all convenience getter and setter methods."""
        settings_manager.load_settings() # Load initial default settings

        # Theme
        settings_manager.set_theme(AppSettings.THEME_DARK)
        self.assertEqual(settings_manager.get_theme(), AppSettings.THEME_DARK)
        self.assertEqual(settings_manager.current_settings.theme, AppSettings.THEME_DARK)
        with open(self.test_settings_file, 'r') as f: data = json.load(f)
        self.assertEqual(data["theme"], AppSettings.THEME_DARK)
        # Invalid theme through setter
        settings_manager.set_theme("invalid_one")
        self.assertEqual(settings_manager.get_theme(), AppSettings.THEME_DARK) # Should not change

        # Language
        settings_manager.set_language(AppSettings.LANG_FRENCH)
        self.assertEqual(settings_manager.get_language(), AppSettings.LANG_FRENCH)
        with open(self.test_settings_file, 'r') as f: data = json.load(f)
        self.assertEqual(data["language"], AppSettings.LANG_FRENCH)
        # Invalid language through setter
        settings_manager.set_language("xx")
        self.assertEqual(settings_manager.get_language(), AppSettings.LANG_FRENCH) # Should not change

        # Backup Enabled
        settings_manager.set_backup_enabled(True)
        self.assertTrue(settings_manager.is_backup_enabled())
        with open(self.test_settings_file, 'r') as f: data = json.load(f)
        self.assertTrue(data["backup_enabled"])
        # Invalid type for backup_enabled
        settings_manager.set_backup_enabled("not-a-bool")
        self.assertTrue(settings_manager.is_backup_enabled()) # Should not change

        # Backup Location
        test_backup_path = "/my/test/backup/path"
        settings_manager.set_backup_location(test_backup_path)
        self.assertEqual(settings_manager.get_backup_location(), test_backup_path)
        with open(self.test_settings_file, 'r') as f: data = json.load(f)
        self.assertEqual(data["backup_location"], test_backup_path)
        # Invalid type for backup_location
        settings_manager.set_backup_location(12345)
        self.assertEqual(settings_manager.get_backup_location(), test_backup_path) # Should not change

        # Sync Frequency
        test_sync_freq = 24
        settings_manager.set_sync_frequency(test_sync_freq)
        self.assertEqual(settings_manager.get_sync_frequency(), test_sync_freq)
        with open(self.test_settings_file, 'r') as f: data = json.load(f)
        self.assertEqual(data["sync_frequency_hours"], test_sync_freq)
        # Invalid type for sync_frequency
        settings_manager.set_sync_frequency("not-an-int")
        self.assertEqual(settings_manager.get_sync_frequency(), test_sync_freq) # Should not change
        
        # Set sync frequency to None
        settings_manager.set_sync_frequency(None)
        self.assertIsNone(settings_manager.get_sync_frequency())
        with open(self.test_settings_file, 'r') as f: data = json.load(f)
        self.assertIsNone(data["sync_frequency_hours"])


if __name__ == '__main__':
    unittest.main()
