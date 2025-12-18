"""Configuration management for the test framework."""

import os
import yaml
from pathlib import Path


class Config:
    """Configuration loader for different environments."""

    def __init__(self, environment="dev"):
        self.environment = environment
        self.config_dir = Path(__file__).parent
        self.project_root = self.config_dir.parent
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from YAML file."""
        config_file = self.config_dir / "environments" / f"{self.environment}.yaml"

        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        with open(config_file, "r") as f:
            return yaml.safe_load(f)

    def get(self, key, default=None):
        """Get configuration value by dot notation key."""
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default

        return value

    def get_cert_path(self, cert_type):
        """Get absolute path to certificate file."""
        relative_path = self.get(f"mqtt.{cert_type}")
        if relative_path:
            return str(self.project_root / relative_path)
        return None


# Global config instance
_config = None


def get_config(environment=None):
    """Get or create global configuration instance."""
    global _config

    if environment is None:
        environment = os.getenv("TEST_ENV", "dev")

    if _config is None or _config.environment != environment:
        _config = Config(environment)

    return _config
