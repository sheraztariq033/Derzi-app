import uuid

class AppSettings:
    # Theme constants
    THEME_LIGHT = "light"
    THEME_DARK = "dark"
    THEME_SYSTEM_DEFAULT = "system_default"
    VALID_THEMES = [THEME_LIGHT, THEME_DARK, THEME_SYSTEM_DEFAULT]

    # Language constants (examples)
    LANG_ENGLISH = "en"
    LANG_TURKISH = "tr"
    LANG_FRENCH = "fr"
    VALID_LANGUAGES = [LANG_ENGLISH, LANG_TURKISH, LANG_FRENCH]

    DEFAULT_SETTINGS_ID = "global_app_settings"

    def __init__(self, settings_id=DEFAULT_SETTINGS_ID, theme=THEME_SYSTEM_DEFAULT, 
                 language=LANG_ENGLISH, backup_enabled=False, backup_location=None, 
                 sync_frequency_hours=None):
        
        if theme not in self.VALID_THEMES:
            # Fallback to default if an invalid theme is somehow passed during init
            # Or raise ValueError, but for settings, a graceful fallback might be better
            theme = self.THEME_SYSTEM_DEFAULT
        if language not in self.VALID_LANGUAGES:
            # Fallback to default for language
            language = self.LANG_ENGLISH

        self.settings_id = settings_id
        self.theme = theme
        self.language = language
        self.backup_enabled = backup_enabled
        self.backup_location = backup_location
        self.sync_frequency_hours = sync_frequency_hours

    def to_dict(self):
        """Converts the settings object to a dictionary for JSON serialization."""
        return {
            "settings_id": self.settings_id,
            "theme": self.theme,
            "language": self.language,
            "backup_enabled": self.backup_enabled,
            "backup_location": self.backup_location,
            "sync_frequency_hours": self.sync_frequency_hours,
        }

    @classmethod
    def from_dict(cls, data_dict):
        """Creates an AppSettings instance from a dictionary (e.g., loaded from JSON)."""
        return cls(
            settings_id=data_dict.get("settings_id", cls.DEFAULT_SETTINGS_ID),
            theme=data_dict.get("theme", cls.THEME_SYSTEM_DEFAULT),
            language=data_dict.get("language", cls.LANG_ENGLISH),
            backup_enabled=data_dict.get("backup_enabled", False),
            backup_location=data_dict.get("backup_location"),
            sync_frequency_hours=data_dict.get("sync_frequency_hours")
        )

    def __repr__(self):
        return f"<AppSettings {self.settings_id} - Theme: {self.theme}, Lang: {self.language}>"
