"""Load YAML config and obtain a Sentinel Hub OAuth2 access token."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import requests
import yaml


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


def build_token_cache(config: dict[str, Any]) -> TokenCache:
    """Construct a TokenCache from the loaded config dict."""
    sh = config["sentinel_hub"]
    return TokenCache(
        client_id=sh["client_id"],
        client_secret=sh["client_secret"],
        token_url=sh.get(
            "token_url", "https://services.sentinel-hub.com/oauth/token"
        ),
    )
