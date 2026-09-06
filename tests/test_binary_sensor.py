"""Test Intelbras Solar binary sensor platform."""

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.intelbras_solar.binary_sensor import _connected
from custom_components.intelbras_solar.intelbras import IntelbrasSolarData, Inverter


def test_connected_helper() -> None:
    """Test connection status detection helper."""
    assert _connected({"status": 1}) is True
    assert _connected({"status": "1"}) is True
    assert _connected({"status": 0}) is True
    assert _connected({"status": -1}) is False
    assert _connected({"status": "-1"}) is False
    assert _connected({}) is None
    assert _connected({"status": None}) is None


async def test_binary_sensor_entity_state(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_intelbras_data: IntelbrasSolarData,
) -> None:
    """Test inverter binary sensor is set up and changes state."""
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

    state = hass.states.get("binary_sensor.inverter_1_connection")
    assert state is not None
    assert state.state == "on"
    assert state.attributes.get("device_class") == "connectivity"
