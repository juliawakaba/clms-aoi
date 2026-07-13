"""Simple configuration classes for loading YAML files."""

import os
import yaml

from .exceptions import ConfigError, ConfigFileNotFoundError


class SentinelHubCredentials:
    """Stores Sentinel Hub client ID and secret."""

    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.getenv("CLMS_SH_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("CLMS_SH_CLIENT_SECRET")

    def get_client_id(self):
        return self.client_id

    def get_client_secret(self):
        return self.client_secret


class Config:
    """Holds configuration data for CLMS AOI analysis."""

    def __init__(self, sentinelhub, products=None, time_cfg=None, aoi_cfg=None, output_cfg=None):
        self.sentinelhub = sentinelhub
        self.products = products or []
        self.time = time_cfg
        self.aoi = aoi_cfg
        self.output = output_cfg


class ConfigLoader:
    """This class helps load configuration from YAML files."""

    @staticmethod
    def load(file_path):
        """Loads and parses the config YAML configuration file."""
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            raise ConfigFileNotFoundError(file_path)
        except Exception as error:
            raise ConfigError(f"Failed to load YAML file: {error}")

        if not isinstance(data, dict):
            raise ConfigError("Invalid YAML format: expected dictionary.")

        sh_data = data.get("sentinelhub", {})
        credentials = SentinelHubCredentials(
            client_id=sh_data.get("client_id"),
            client_secret=sh_data.get("client_secret")
        )

        return Config(
            sentinelhub=credentials,
            aoi_cfg=data.get("aoi"),
            products=data.get("products", []),
            time_cfg=data.get("time"),
            output_cfg=data.get("output")
        )