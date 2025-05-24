import json
import os
from .models import AppSettings

SETTINGS_FILE_PATH = "derzi_master_book/data/app_settings.json"
current_settings = None

def _ensure_data_directory_exists():
    """Ensures the data directory for settings file exists."""
    os.makedirs(os.path.dirname(SETTINGS_FILE_PATH), exist_ok=True)

def load_settings():
    """
    Loads settings from SETTINGS_FILE_PATH.
    If the file doesn't exist or is invalid, initializes with defaults and saves.
    """
    global current_settings
    _ensure_data_directory_exists()
    try:
        with open(SETTINGS_FILE_PATH, 'r') as f:
            data = json.load(f)
            current_settings = AppSettings.from_dict(data)
    except (FileNotFoundError, json.JSONDecodeError):
        current_settings = AppSettings() # Initialize with defaults
        save_settings() # Create the file with default settings
    return current_settings

def save_settings():
    """
    Saves the current_settings object to SETTINGS_FILE_PATH as JSON.
    """
    global current_settings
    _ensure_data_directory_exists()
    if current_settings:
        with open(SETTINGS_FILE_PATH, 'w') as f:
            json.dump(current_settings.to_dict(), f, indent=4)

def get_settings():
    """
    Returns the current AppSettings instance, loading it if necessary.
    """
    global current_settings
    if current_settings is None:
        load_settings()
    return current_settings

def update_setting(key, value):
    """
    Updates a specific setting by key and value, then saves settings.
    Validates key and value where appropriate.
    """
    global current_settings
    settings = get_settings() # Ensure settings are loaded

    if not hasattr(settings, key):
        # Or raise AttributeError("Invalid settings key")
        return None 

    # Specific validations
    if key == "theme" and value not in AppSettings.VALID_THEMES:
        # Or raise ValueError for invalid theme
        return None 
    if key == "language" and value not in AppSettings.VALID_LANGUAGES:
        # Or raise ValueError for invalid language
        return None
    if key == "backup_enabled" and not isinstance(value, bool):
        return None
    if key == "sync_frequency_hours" and value is not None and not isinstance(value, int):
        return None
    
    setattr(settings, key, value)
    save_settings()
    return settings

# Convenience getter/setter methods

def get_theme():
    """Returns the current theme."""
    return get_settings().theme

def set_theme(theme_name):
    """Sets the application theme."""
    if theme_name not in AppSettings.VALID_THEMES:
        # Consider raising an error or logging a warning
        print(f"Warning: Invalid theme '{theme_name}'. Not set.")
        return get_settings() # Return current settings without change
    return update_setting("theme", theme_name)

def get_language():
    """Returns the current language."""
    return get_settings().language

def set_language(lang_code):
    """Sets the application language."""
    if lang_code not in AppSettings.VALID_LANGUAGES:
        print(f"Warning: Invalid language code '{lang_code}'. Not set.")
        return get_settings()
    return update_setting("language", lang_code)

def is_backup_enabled():
    """Checks if backup is enabled."""
    return get_settings().backup_enabled

def set_backup_enabled(enabled):
    """Enables or disables backup."""
    if not isinstance(enabled, bool):
        print(f"Warning: Invalid value for backup_enabled '{enabled}'. Must be boolean. Not set")
        return get_settings()
    return update_setting("backup_enabled", enabled)

def get_backup_location():
    """Returns the backup location."""
    return get_settings().backup_location

def set_backup_location(location):
    """Sets the backup location."""
    if location is not None and not isinstance(location, str):
        print(f"Warning: Invalid backup location '{location}'. Must be a string or None. Not set.")
        return get_settings()
    return update_setting("backup_location", location)

def get_sync_frequency():
    """Returns the sync frequency in hours."""
    return get_settings().sync_frequency_hours

def set_sync_frequency(hours):
    """Sets the sync frequency in hours."""
    if hours is not None and not isinstance(hours, int):
        print(f"Warning: Invalid sync frequency '{hours}'. Must be an integer or None. Not set.")
        return get_settings()
    return update_setting("sync_frequency_hours", hours)
