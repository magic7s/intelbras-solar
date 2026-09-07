"""Base entities that attach the portal objects to device registry entries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, NAME
from .coordinator import IntelbrasSolarDataUpdateCoordinator

if TYPE_CHECKING:
    from .intelbras import Inverter, Plant


def plant_identifier(plant_id: str) -> tuple[str, str]:
    """Return the device registry identifier of a plant."""
    return (DOMAIN, f"plant_{plant_id}")


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
        plant = self.plant
        self._attr_device_info = DeviceInfo(
            identifiers={plant_identifier(plant_id)},
            manufacturer=MANUFACTURER,
            model="Solar plant",
            name=plant.name,
            configuration_url="http://solar-monitoramento.intelbras.com.br/",
        )

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
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial_number)},
            manufacturer=MANUFACTURER,
            model=inverter.model or NAME,
            name=inverter.name,
            serial_number=serial_number,
            # `via_device` is deprecated in favour of `via_device_id` and is
            # removed in HA 2027.8.0. Migrating means resolving the plant's
            # device registry id here, which requires the plant device to be
            # registered first; the tuple form defers that resolution for us.
            via_device=plant_identifier(inverter.plant_id),  # type: ignore[typeddict-unknown-key]
            configuration_url="http://solar-monitoramento.intelbras.com.br/",
        )

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
