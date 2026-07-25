import time
from unittest.mock import MagicMock, patch
import pytest
import requests

from clms_aoi.auth import CachedToken, SentinelHubAuthenticator
from clms_aoi.config import SentinelHubCredentials
from clms_aoi.exceptions import (
    InvalidCredentialsError,
    MissingCredentialsError,
    TokenRequestError,
)


@pytest.fixture
def valid_credentials():
    """Fixture providing mock valid credentials."""
    return SentinelHubCredentials(
        client_id="test_client_id", client_secret="test_client_secret"
    )


@pytest.fixture
def empty_credentials():
    """Fixture providing empty credentials."""
    return SentinelHubCredentials(client_id="", client_secret="")


@patch("requests.post")
def test_authenticate_success(mock_post, valid_credentials):
    """Tests successful token retrieval from CDSE endpoint."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "mock_access_token_123",
        "expires_in": 3600,
    }
    mock_post.return_value = mock_response

    authenticator = SentinelHubAuthenticator(valid_credentials)
    token = authenticator.authenticate()

    assert token == "mock_access_token_123"
    assert authenticator.cached_token is not None
    assert authenticator.cached_token.access_token == "mock_access_token_123"

    # check request payload & auth
    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    assert kwargs["data"] == {"grant_type": "client_credentials"}
    assert kwargs["auth"] == ("test_client_id", "test_client_secret")


@patch("requests.post")
def test_token_caching(mock_post, valid_credentials):
    """Tests that cached tokens are reused without making redundant HTTP calls."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "cached_token_xyz",
        "expires_in": 3600,
    }
    mock_post.return_value = mock_response

    authenticator = SentinelHubAuthenticator(valid_credentials)

    token1 = authenticator.authenticate()
    token2 = authenticator.authenticate()

    assert token1 == token2 == "cached_token_xyz"
    assert mock_post.call_count == 1  # Only fetched once


# this tests Exception Handling


def test_missing_credentials_raises_error(empty_credentials):
    """Tests that missing client_id/client_secret raises MissingCredentialsError."""
    authenticator = SentinelHubAuthenticator(empty_credentials)
    with pytest.raises(MissingCredentialsError):
        authenticator.authenticate()


@patch("requests.post")
def test_invalid_credentials_raises_error(mock_post, valid_credentials):
    """Tests that HTTP 401 response raises InvalidCredentialsError."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_post.return_value = mock_response

    authenticator = SentinelHubAuthenticator(valid_credentials)
    with pytest.raises(InvalidCredentialsError):
        authenticator.authenticate()


@patch("requests.post")
def test_network_exception_raises_token_request_error(mock_post, valid_credentials):
    """Tests that network failures raise TokenRequestError."""
    mock_post.side_effect = requests.RequestException("Connection timeout")

    authenticator = SentinelHubAuthenticator(valid_credentials)
    with pytest.raises(TokenRequestError):
        authenticator.authenticate()


# to test SHConfig Generation


@patch("requests.post")
def test_get_sh_config(mock_post, valid_credentials):
    """Tests generation of sentinelhub.SHConfig profile."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "mock_token",
        "expires_in": 3600,
    }
    mock_post.return_value = mock_response

    authenticator = SentinelHubAuthenticator(valid_credentials)

    with patch("sentinelhub.SHConfig") as MockSHConfig:
        mock_config_instance = MagicMock()
        MockSHConfig.return_value = mock_config_instance

        config = authenticator.get_sh_config(save_profile=None)

        assert config.sh_client_id == "test_client_id"
        assert config.sh_client_secret == "test_client_secret"
        assert config.sh_base_url == "https://sh.dataspace.copernicus.eu"