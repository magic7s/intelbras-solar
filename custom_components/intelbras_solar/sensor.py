"""Platform for sensor integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


from .const import DOMAIN
from .intelbras import (
    IntelbrasDataLogger,
    IntelbrasPowerPlant,
    list_of_devices_in_plant,
    list_of_plants,
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,  # noqa: ARG001
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    username = hass.data[DOMAIN][CONF_USERNAME]
    password = hass.data[DOMAIN][CONF_PASSWORD]
    all_entities = []
    for plant in list_of_plants(username, password):
        all_entities.append(IntelbrasPowerPlant(username, password, plant["id"]))
        for device in list_of_devices_in_plant(username, password, plant["id"]):
            all_entities.append(  # noqa: PERF401
                IntelbrasDataLogger(username, password, device["plantId"], device["sn"])
            )
    add_entities(all_entities)
