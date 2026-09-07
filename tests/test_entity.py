"""Test device registry wiring for plant and inverter entities."""

import logging
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.intelbras_solar.const import DOMAIN
from custom_components.intelbras_solar.intelbras import IntelbrasSolarData


async def test_inverter_device_links_to_plant_without_deprecation(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_intelbras_data: IntelbrasSolarData,
    caplog,
) -> None:
    """The inverter device links to its plant without deprecated `via_device`."""
    caplog.set_level(logging.WARNING)
    with patch(
        "custom_components.intelbras_solar.IntelbrasSolarApiClient.fetch",
        return_value=mock_intelbras_data,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    registry = dr.async_get(hass)
    entry_id = mock_config_entry.entry_id
    plant = registry.async_get_device_by_identifier((DOMAIN, "plant_123"), entry_id)
    inverter = registry.async_get_device_by_identifier((DOMAIN, "INV123456"), entry_id)

    assert plant is not None
    assert inverter is not None
    assert inverter.via_device_id == plant.id

    deprecations = [
        r.getMessage() for r in caplog.records if "via_device" in r.getMessage()
    ]
    assert not deprecations, f"deprecated via_device still in use: {deprecations}"


async def test_inverter_without_a_known_plant_is_registered_unlinked(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_intelbras_data: IntelbrasSolarData,
    caplog,
) -> None:
    """An inverter whose plant is missing still registers, just without a parent."""
    mock_intelbras_data.plants.clear()

    with patch(
        "custom_components.intelbras_solar.IntelbrasSolarApiClient.fetch",
        return_value=mock_intelbras_data,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    registry = dr.async_get(hass)
    inverter = registry.async_get_device_by_identifier(
        (DOMAIN, "INV123456"), mock_config_entry.entry_id
    )

    assert inverter is not None
    assert inverter.via_device_id is None
