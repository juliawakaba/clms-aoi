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
    """This class validates Sentinel Hub credentials and manages OAuth2 access token."""

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

