"""Test component initialization and teardown."""

from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.intelbras_solar import async_setup, async_setup_entry, async_unload_entry
from custom_components.intelbras_solar.const import DOMAIN
from custom_components.intelbras_solar.intelbras import IntelbrasSolarData
from tests.conftest import MOCK_PASSWORD, MOCK_USERNAME


async def test_async_setup_no_config(hass: HomeAssistant) -> None:
    """Test async_setup with no configuration."""
    assert await async_setup(hass, {}) is True


async def test_async_setup_with_yaml_config(hass: HomeAssistant) -> None:
    """Test async_setup imports YAML and registers deprecation issue."""
    config = {
        DOMAIN: {
            CONF_USERNAME: MOCK_USERNAME,
            CONF_PASSWORD: MOCK_PASSWORD,
        }
    }
    with patch(
        "custom_components.intelbras_solar.config_flow.IntelbrasSolarApiClient.plants",
        return_value=[{"id": 1}],
    ):
        assert await async_setup(hass, config) is True
        await hass.async_block_till_done()

    issue_registry = ir.async_get(hass)
    issue = issue_registry.async_get_issue(DOMAIN, "deprecated_yaml")
    assert issue is not None


async def test_setup_and_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_intelbras_data: IntelbrasSolarData,
) -> None:
    """Test setup and unloading of config entry."""
    with (
        patch(
            "custom_components.intelbras_solar.IntelbrasSolarApiClient.fetch",
            return_value=mock_intelbras_data,
        ),
        patch(
            "custom_components.intelbras_solar.coordinator.IntelbrasSolarApiClient.fetch",
            return_value=mock_intelbras_data,
        ),
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
