"""Load YAML config and obtain a Sentinel Hub OAuth2 access token."""

import time
import logging
import requests

from .config import SentinelHubCredentials
from .exceptions import InvalidCredentialsError, MissingCredentialsError, TokenRequestError

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"


logger = logging.getLogger(__name__)


class CachedToken:
    """Class to store the token and the time it expires."""

    def __init__(self, access_token: str, expires_at: float):
        self.access_token = access_token
        self.expires_at = expires_at


class SentinelHubAuthenticator:
    """Thi sclass validates Sentinel Hub credentials and manages OAuth2 access token."""

    def __init__(self, credentials: SentinelHubCredentials, token_url: str = TOKEN_URL):
        self.credentials = credentials
        self.token_url = token_url
        self.cached_token = None

    def authenticate(self):
        """Requests/reuses an access token for API requests."""
        if self.cached_token is not None and self.cached_token.expires_at > time.monotonic() + 30:
            logger.info("Using cached valid Sentinel Hub access token.")
            return self.cached_token.access_token

        client_id = self.credentials.client_id
        client_secret = self.credentials.client_secret

        if not client_id or not client_secret:
            logger.error("Missing client_id or client_secret.")
            raise MissingCredentialsError(
                "Sentinel Hub client_id or client_secret is missing. "
                "Set them in the config file or environment variables."
            )

        try:
            logger.info("Requesting new access token from Sentinel Hub...")
            response = requests.post(
                self.token_url,
                data={"grant_type": "client_credentials"},
                auth=(client_id, client_secret),
                timeout=15,
            )
        except requests.RequestException as error:
            logger.error("Network error while requesting token: %s", error)
            raise TokenRequestError(f"Could not reach Sentinel Hub token endpoint: {error}")

        if response.status_code in (400, 401):
            logger.error("Authentication failed with status code %s", response.status_code)
            raise InvalidCredentialsError(
                f"Sentinel Hub rejected the credentials you gave (HTTP {response.status_code})."
            )
        elif response.status_code != 200:
            logger.error("Token endpoint error: HTTP %s", response.status_code)
            raise TokenRequestError(
                f"Unexpected response from token endpoint: HTTP {response.status_code}"
            )

        data = response.json()
        token = data.get("access_token")
        expires_in = float(data.get("expires_in", 3600))

        self.cached_token = CachedToken(
            access_token=token,
            expires_at=time.monotonic() + expires_in
        )

        logger.info("Successfully retrieved and cached access token.")
        return token

    def get_sh_config(self, save_profile="cdse"):
        """Generates and configures the Sentinel Hub profile object."""
        self.authenticate()

        from sentinelhub import SHConfig

        config = SHConfig()
        config.sh_client_id = self.credentials.client_id
        config.sh_client_secret = self.credentials.client_secret
        config.sh_token_url = self.token_url
        config.sh_base_url = "https://sh.dataspace.copernicus.eu"

        if save_profile:
            config.save(save_profile)
            logger.info("Saved Sentinel Hub configuration profile: '%s'", save_profile)

        return config



# from __future__ import annotations

# import time
# from pathlib import Path
# from typing import Any

# import requests
# import yaml
# from sentinelhub import SHConfig


# def load_config(path: str | Path) -> dict[str, Any]:
#     """Load the YAML configuration file."""
#     with open(path) as fh:
#         return yaml.safe_load(fh)


# class TokenCache:
#     """Holds an access token and refreshes it when it expires."""

#     def __init__(self, client_id: str, client_secret: str, token_url: str) -> None:
#         self._client_id = client_id
#         self._client_secret = client_secret
#         self._token_url = token_url
#         self._token: str | None = None
#         self._expires_at: float = 0.0

#     def get_token(self) -> str:
#         if self._token is None or time.monotonic() >= self._expires_at:
#             self._refresh()
#         return self._token  # type: ignore[return-value]

#     def _refresh(self) -> None:
#         resp = requests.post(
#             self._token_url,
#             data={
#                 "grant_type": "client_credentials",
#                 "client_id": self._client_id,
#                 "client_secret": self._client_secret,
#             },
#             timeout=30,
#         )
#         resp.raise_for_status()
#         payload = resp.json()
#         self._token = payload["access_token"]
#         self._expires_at = time.monotonic() + payload.get("expires_in", 3600) - 60


# _CDSE_TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
# _CDSE_BASE_URL = "https://sh.dataspace.copernicus.eu"


# def build_token_cache(config: dict[str, Any]) -> TokenCache:
#     """Construct a TokenCache from the loaded config dict."""
#     sh = config["sentinel_hub"]
#     return TokenCache(
#         client_id=sh["client_id"],
#         client_secret=sh["client_secret"],
#         token_url=sh.get("token_url", _CDSE_TOKEN_URL),
#     )


# def token_cache_from_sh_config(sh_config: SHConfig) -> TokenCache:
#     """Build a TokenCache from an already-loaded SHConfig profile."""
#     return TokenCache(
#         client_id=sh_config.sh_client_id,
#         client_secret=sh_config.sh_client_secret,
#         token_url=sh_config.sh_token_url,
#     )


# def build_sh_config(config: dict[str, Any]) -> SHConfig:
#     """Create, save, and return an SHConfig profile built from the config dict."""
#     sh = config["sentinel_hub"]
#     profile = sh.get("profile", "cdse")

#     sh_config = SHConfig()
#     sh_config.sh_client_id = sh["client_id"]
#     sh_config.sh_client_secret = sh["client_secret"]
#     sh_config.sh_token_url = sh.get("token_url", _CDSE_TOKEN_URL)
#     sh_config.sh_base_url = sh.get("base_url", _CDSE_BASE_URL)
#     sh_config.save(profile)

#     return SHConfig(profile)
