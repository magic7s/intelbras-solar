"""Platform for sensor integration."""

from __future__ import annotations

from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN

from .intelbras import (
    IntelbrasPowerPlant,
    IntelbrasDataLogger,
    list_of_plants,
    list_of_devices_in_plant,
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
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
            all_entities.append(
                IntelbrasDataLogger(username, password, device["plantId"], device["sn"])
            )
    add_entities(all_entities)
