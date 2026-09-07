"""The Intelbras Solar integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN, ISSUE_URL, NAME, PLATFORMS
from .coordinator import IntelbrasSolarDataUpdateCoordinator
from .entity import plant_device_info
from .intelbras import IntelbrasSolarApiClient

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

    from .coordinator import IntelbrasSolarConfigEntry

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Import a legacy YAML configuration into a config entry."""
    if DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config[DOMAIN]
        )
    )
    ir.async_create_issue(
        hass,
        DOMAIN,
        "deprecated_yaml",
        breaks_in_ha_version=None,
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key="deprecated_yaml",
        translation_placeholders={"integration": NAME, "issue_url": ISSUE_URL},
    )
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: IntelbrasSolarConfigEntry
) -> bool:
    """Set up Intelbras Solar from a config entry."""
    client = IntelbrasSolarApiClient(
        entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
    )
    coordinator = IntelbrasSolarDataUpdateCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # Register the plant devices up front so that inverter entities can link to
    # them by registry id via `via_device_id` when their platforms are set up.
    device_registry = dr.async_get(hass)
    for plant in coordinator.data.plants.values():
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id, **plant_device_info(plant)
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: IntelbrasSolarConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
