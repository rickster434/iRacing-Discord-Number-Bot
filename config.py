"""
Configuration handler for iRacing Number Bot
Loads settings from .env file
"""

import os
from typing import Optional
from pathlib import Path

class Config:
    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self.config = {}
        self._load_env()

    def _load_env(self):
        """Load environment variables from .env file"""
        env_path = Path(self.env_file)

        if not env_path.exists():
            print(f"Warning: {self.env_file} not found. Using environment variables only.")
            return

        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Parse key=value
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]

                        self.config[key] = value

        except Exception as e:
            print(f"Error loading {self.env_file}: {e}")

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value"""
        # Check environment variable first (higher priority)
        value = os.environ.get(key)
        if value is not None:
            return value

        # Then check loaded config
        value = self.config.get(key)
        if value is not None:
            return value

        # Return default
        return default

    def get_int(self, key: str, default: int = 0) -> int:
        """Get a configuration value as integer"""
        value = self.get(key)
        if value is None:
            return default

        try:
            return int(value)
        except ValueError:
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a configuration value as boolean"""
        value = self.get(key)
        if value is None:
            return default

        return value.lower() in ('true', '1', 'yes', 'on')

    def set(self, key: str, value: str):
        """Set a configuration value (in memory only)"""
        self.config[key] = value

    def save(self):
        """Save configuration to .env file"""
        try:
            with open(self.env_file, 'w') as f:
                f.write("# iRacing Discord Number Bot Configuration\n")
                f.write("# Generated configuration file\n\n")

                for key, value in self.config.items():
                    # Add quotes if value contains spaces
                    if ' ' in str(value):
                        f.write(f'{key}="{value}"\n')
                    else:
                        f.write(f'{key}={value}\n')

        except Exception as e:
            print(f"Error saving {self.env_file}: {e}")

    def validate(self) -> tuple[bool, list[str]]:
        """Validate required configuration"""
        required_keys = [
            'DISCORD_BOT_TOKEN',
        ]

        optional_keys = [
            'IRACING_USERNAME',
            'IRACING_PASSWORD',
        ]

        missing = []
        warnings = []

        # Check required keys
        for key in required_keys:
            if not self.get(key):
                missing.append(key)

        # Check optional keys
        for key in optional_keys:
            if not self.get(key):
                warnings.append(f"{key} not set - iRacing sync features will be disabled")

        is_valid = len(missing) == 0

        return is_valid, missing + warnings
