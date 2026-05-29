"""Load YAML config and obtain a Sentinel Hub OAuth2 access token."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import requests
import yaml
from sentinelhub import SHConfig


def load_config(path: str | Path) -> dict[str, Any]:
    """Load the YAML configuration file."""
    with open(path) as fh:
        return yaml.safe_load(fh)


class TokenCache:
    """Holds an access token and refreshes it when it expires."""

    def __init__(self, client_id: str, client_secret: str, token_url: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._token: str | None = None
        self._expires_at: float = 0.0

    def get_token(self) -> str:
        if self._token is None or time.monotonic() >= self._expires_at:
            self._refresh()
        return self._token  # type: ignore[return-value]

    def _refresh(self) -> None:
        resp = requests.post(
            self._token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
        self._token = payload["access_token"]
        self._expires_at = time.monotonic() + payload.get("expires_in", 3600) - 60


_CDSE_TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
_CDSE_BASE_URL = "https://sh.dataspace.copernicus.eu"


def build_token_cache(config: dict[str, Any]) -> TokenCache:
    """Construct a TokenCache from the loaded config dict."""
    sh = config["sentinel_hub"]
    return TokenCache(
        client_id=sh["client_id"],
        client_secret=sh["client_secret"],
        token_url=sh.get("token_url", _CDSE_TOKEN_URL),
    )


def token_cache_from_sh_config(sh_config: SHConfig) -> TokenCache:
    """Build a TokenCache from an already-loaded SHConfig profile."""
    return TokenCache(
        client_id=sh_config.sh_client_id,
        client_secret=sh_config.sh_client_secret,
        token_url=sh_config.sh_token_url,
    )


def build_sh_config(config: dict[str, Any]) -> SHConfig:
    """Create, save, and return an SHConfig profile built from the config dict."""
    sh = config["sentinel_hub"]
    profile = sh.get("profile", "cdse")

    sh_config = SHConfig()
    sh_config.sh_client_id = sh["client_id"]
    sh_config.sh_client_secret = sh["client_secret"]
    sh_config.sh_token_url = sh.get("token_url", _CDSE_TOKEN_URL)
    sh_config.sh_base_url = sh.get("base_url", _CDSE_BASE_URL)
    sh_config.save(profile)

    return SHConfig(profile)
