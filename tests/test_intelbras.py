"""Test IntelbrasSolarApiClient HTTP requests and response parsing."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from custom_components.intelbras_solar.intelbras import (
    IntelbrasSolarApiClient,
    IntelbrasSolarApiClientError,
    IntelbrasSolarAuthError,
)
from tests.conftest import (
    MOCK_INVERTER_DATA,
    MOCK_PASSWORD,
    MOCK_PLANT_DATA,
    MOCK_USERNAME,
)


def test_login_success() -> None:
    """Test successful login."""
    client = IntelbrasSolarApiClient(MOCK_USERNAME, MOCK_PASSWORD)
    with patch.object(client._session, "post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"result": 1}
        mock_post.return_value = mock_response

        client.login()
        assert client._logged_in is True
        mock_post.assert_called_once()


def test_login_invalid_credentials() -> None:
    """Test login failure raises IntelbrasSolarAuthError."""
    client = IntelbrasSolarApiClient(MOCK_USERNAME, MOCK_PASSWORD)
    with patch.object(client._session, "post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"result": 0}
        mock_post.return_value = mock_response

        with pytest.raises(IntelbrasSolarAuthError):
            client.login()
        assert client._logged_in is False


def test_post_network_error() -> None:
    """Test network error during POST raises IntelbrasSolarApiClientError."""
    client = IntelbrasSolarApiClient(MOCK_USERNAME, MOCK_PASSWORD)
    with patch.object(
        client._session, "post", side_effect=requests.RequestException("Timeout")
    ):
        with pytest.raises(IntelbrasSolarApiClientError):
            client._post("login")


def test_post_invalid_json() -> None:
    """Test non-JSON response raises IntelbrasSolarApiClientError."""
    client = IntelbrasSolarApiClient(MOCK_USERNAME, MOCK_PASSWORD)
    with patch.object(client._session, "post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("No JSON")
        mock_post.return_value = mock_response

        with pytest.raises(IntelbrasSolarApiClientError):
            client._post("login")


def test_fetch_snapshot_success() -> None:
    """Test fetch creates complete plant and inverter snapshot."""
    client = IntelbrasSolarApiClient(MOCK_USERNAME, MOCK_PASSWORD)
    client._logged_in = True

    with (
        patch.object(
            client, "plants", return_value=[{"id": "123", "plantName": "Plant 1"}]
        ),
        patch.object(client, "plant_data", return_value=MOCK_PLANT_DATA),
        patch.object(client, "devices", return_value=[MOCK_INVERTER_DATA]),
    ):
        snapshot = client.fetch()
        assert "123" in snapshot.plants
        assert snapshot.plants["123"].name == "My Solar Plant"
        assert "INV123456" in snapshot.inverters
        assert snapshot.inverters["INV123456"].model == "Ecosol 5K"


def test_fetch_retry_on_api_error() -> None:
    """Test fetch retries after resetting login on client error."""
    client = IntelbrasSolarApiClient(MOCK_USERNAME, MOCK_PASSWORD)
    client._logged_in = True

    calls = 0

    def mock_fetch_internal():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise IntelbrasSolarApiClientError("Session expired")
        client._logged_in = True
        snapshot = MagicMock()
        return snapshot

    with patch.object(client, "_fetch", side_effect=mock_fetch_internal):
        snapshot = client.fetch()
        assert snapshot is not None
        assert calls == 2
