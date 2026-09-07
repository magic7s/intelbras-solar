"""Base entities that attach the portal objects to device registry entries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BASE_URL, DOMAIN, MANUFACTURER, NAME
from .coordinator import IntelbrasSolarDataUpdateCoordinator

if TYPE_CHECKING:
    from .intelbras import Inverter, Plant


def plant_identifier(plant_id: str) -> tuple[str, str]:
    """Return the device registry identifier of a plant."""
    return (DOMAIN, f"plant_{plant_id}")


def plant_device_info(plant: Plant) -> DeviceInfo:
    """Return the device registry entry describing a plant."""
    return DeviceInfo(
        identifiers={plant_identifier(plant.identifier)},
        manufacturer=MANUFACTURER,
        model="Solar plant",
        name=plant.name,
        configuration_url=BASE_URL,
    )


class IntelbrasSolarPlantEntity(CoordinatorEntity[IntelbrasSolarDataUpdateCoordinator]):
    """An entity describing a whole power plant."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IntelbrasSolarDataUpdateCoordinator,
        plant_id: str,
    ) -> None:
        """Initialize the entity and its device."""
        super().__init__(coordinator)
        self._plant_id = plant_id
        self._attr_device_info = plant_device_info(self.plant)

    @property
    def plant(self) -> Plant:
        """Return the plant this entity belongs to."""
        return self.coordinator.data.plants[self._plant_id]

    @property
    def available(self) -> bool:
        """Return whether the last poll still knows about this plant."""
        return super().available and self._plant_id in self.coordinator.data.plants


class IntelbrasSolarInverterEntity(
    CoordinatorEntity[IntelbrasSolarDataUpdateCoordinator]
):
    """An entity describing a single inverter."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IntelbrasSolarDataUpdateCoordinator,
        serial_number: str,
    ) -> None:
        """Initialize the entity and its device."""
        super().__init__(coordinator)
        self._serial_number = serial_number
        inverter = self.inverter
        device_info = DeviceInfo(
            identifiers={(DOMAIN, serial_number)},
            manufacturer=MANUFACTURER,
            model=inverter.model or NAME,
            name=inverter.name,
            serial_number=serial_number,
            configuration_url=BASE_URL,
        )
        # The plant device is registered during config entry setup, so its
        # registry id is available here and can be linked directly. `via_device`
        # (the identifier tuple form) is deprecated and removed in HA 2027.8.0.
        plant_device = dr.async_get(coordinator.hass).async_get_device_by_identifier(
            plant_identifier(inverter.plant_id),
            coordinator.config_entry.entry_id,
        )
        if plant_device is not None:
            device_info["via_device_id"] = plant_device.id
        self._attr_device_info = device_info

    @property
    def inverter(self) -> Inverter:
        """Return the inverter this entity belongs to."""
        return self.coordinator.data.inverters[self._serial_number]

    @property
    def available(self) -> bool:
        """Return whether the last poll still knows about this inverter."""
        return (
            super().available and self._serial_number in self.coordinator.data.inverters
        )
