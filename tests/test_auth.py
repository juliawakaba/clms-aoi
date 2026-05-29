from unittest.mock import MagicMock, patch

from clms_aoi.auth import build_sh_config

_CONFIG = {
    "sentinel_hub": {
        "client_id": "test-id",
        "client_secret": "test-secret",
    }
}


@patch("clms_aoi.auth.SHConfig")
def test_build_sh_config_sets_fields_and_saves(mock_sh_config_cls):
    instance = MagicMock()
    saved_profile = MagicMock()
    mock_sh_config_cls.side_effect = [instance, saved_profile]

    result = build_sh_config(_CONFIG)

    assert instance.sh_client_id == "test-id"
    assert instance.sh_client_secret == "test-secret"
    assert "identity.dataspace.copernicus.eu" in instance.sh_token_url
    assert "sh.dataspace.copernicus.eu" in instance.sh_base_url
    instance.save.assert_called_once_with("cdse")
    assert result is saved_profile


@patch("clms_aoi.auth.SHConfig")
def test_build_sh_config_respects_overrides(mock_sh_config_cls):
    instance = MagicMock()
    saved_profile = MagicMock()
    mock_sh_config_cls.side_effect = [instance, saved_profile]

    cfg = {
        "sentinel_hub": {
            "client_id": "my-id",
            "client_secret": "my-secret",
            "token_url": "https://custom.token.url",
            "base_url": "https://custom.base.url",
            "profile": "my-profile",
        }
    }
    build_sh_config(cfg)

    assert instance.sh_token_url == "https://custom.token.url"
    assert instance.sh_base_url == "https://custom.base.url"
    instance.save.assert_called_once_with("my-profile")
    mock_sh_config_cls.assert_called_with("my-profile")
