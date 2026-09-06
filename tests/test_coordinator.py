"""Test the Intelbras Solar data coordinator."""

from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.intelbras_solar.coordinator import (
    IntelbrasSolarDataUpdateCoordinator,
)
from custom_components.intelbras_solar.intelbras import (
    IntelbrasSolarApiClientError,
    IntelbrasSolarAuthError,
    IntelbrasSolarData,
)


async def test_coordinator_fetch_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_intelbras_data: IntelbrasSolarData,
) -> None:
    """Test successful data update through coordinator."""
    mock_client = MagicMock()
    mock_client.fetch.return_value = mock_intelbras_data

    coordinator = IntelbrasSolarDataUpdateCoordinator(
        hass, mock_config_entry, mock_client
    )

    data = await coordinator._async_update_data()
    assert data == mock_intelbras_data
    assert "123" in data.plants
    assert "INV123456" in data.inverters


async def test_coordinator_auth_error(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test coordinator handles auth error."""
    mock_client = MagicMock()
    mock_client.fetch.side_effect = IntelbrasSolarAuthError("Auth error")

    coordinator = IntelbrasSolarDataUpdateCoordinator(
        hass, mock_config_entry, mock_client
    )

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


async def test_coordinator_api_error(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test coordinator handles API connection error."""
    mock_client = MagicMock()
    mock_client.fetch.side_effect = IntelbrasSolarApiClientError("Connection error")

    coordinator = IntelbrasSolarDataUpdateCoordinator(
        hass, mock_config_entry, mock_client
    )

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
