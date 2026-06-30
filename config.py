"""Configuration loader — reads a JSON file and returns Server objects."""
import json
import logging
import pathlib

from models import Server

logger = logging.getLogger(__name__)


class ConfigError(ValueError):
    """Raised when configuration loading fails."""
    pass


class ConfigLoader:
    """Loads server configuration from a JSON file."""

    def __init__(self, path: str):
        self.path = pathlib.Path(path)

    def load(self) -> list[Server]:
        """Parse the config file and return a list of Server objects.

        Raises:
            ConfigError: if the file is missing or contains invalid JSON.
        """
        logger.info("Loading config from %s", self.path)
        try:
            raw = json.loads(self.path.read_text())
        except FileNotFoundError:
            logger.error("Config file not found: %s", self.path)
            raise ConfigError(f"File not found: {self.path}")
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in %s: %s", self.path, e)
            raise ConfigError(f"Invalid JSON: {e}") from e

        servers = [
            Server(
                id=i,
                name=entry["name"],
                host=entry["host"],
                port=entry.get("port", 8080),
                tags=entry.get("tags", []),
            )
            for i, entry in enumerate(raw, start=1)
        ]
        logger.info("Loaded %d servers", len(servers))
        return servers
