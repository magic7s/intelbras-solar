"""Test Intelbras Solar sensor entities."""

from datetime import UTC
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.intelbras_solar.intelbras import IntelbrasSolarData
from custom_components.intelbras_solar.sensor import _as_float, _as_timestamp


def test_as_float_helpers() -> None:
    """Test float parsing helper."""
    assert _as_float("123.45") == 123.45
    assert _as_float(50) == 50.0
    assert _as_float("invalid") is None
    assert _as_float(None) is None


def test_as_timestamp_helpers() -> None:
    """Test timestamp parsing helper."""
    data = {"last": "2026-09-06 12:00:00", "timezone": "-3"}
    ts = _as_timestamp(data, "last")
    assert ts is not None
    assert ts.year == 2026
    assert ts.month == 9
    assert ts.day == 6
    assert ts.hour == 12

    # Test invalid timestamp string
    assert _as_timestamp({"last": "invalid"}, "last") is None
    # Test missing timestamp key
    assert _as_timestamp({}, "last") is None
    # Test fallback UTC on invalid timezone
    ts_no_tz = _as_timestamp(
        {"last": "2026-09-06 12:00:00", "timezone": "invalid"}, "last"
    )
    assert ts_no_tz is not None
    assert ts_no_tz.tzinfo == UTC


async def test_sensor_entities_created(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_intelbras_data: IntelbrasSolarData,
) -> None:
    """Test sensor entities are created and report states."""
    with patch(
        "custom_components.intelbras_solar.IntelbrasSolarApiClient.fetch",
        return_value=mock_intelbras_data,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Plant sensor
    state_plant = hass.states.get("sensor.my_solar_plant_total_energy")
    assert state_plant is not None
    assert state_plant.state == "1234.5"
    assert state_plant.attributes.get("unit_of_measurement") == "kWh"

    # Inverter instant power
    state_power = hass.states.get("sensor.inverter_1_instant_power")
    assert state_power is not None
    assert state_power.state == "3500.0"
    assert state_power.attributes.get("unit_of_measurement") == "W"

    # Inverter energy today
    state_today = hass.states.get("sensor.inverter_1_energy_today")
    assert state_today is not None
    assert state_today.state == "15.4"

    # Inverter energy this month
    state_month = hass.states.get("sensor.inverter_1_energy_this_month")
    assert state_month is not None
    assert state_month.state == "250.0"

    # Inverter total energy
    state_inv_total = hass.states.get("sensor.inverter_1_total_energy")
    assert state_inv_total is not None
    assert state_inv_total.state == "4321.0"
