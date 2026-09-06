"""Binary sensor platform for the Intelbras Solar integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .entity import IntelbrasSolarInverterEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .coordinator import (
        IntelbrasSolarConfigEntry,
        IntelbrasSolarDataUpdateCoordinator,
    )

# The portal reports -1 once it stops hearing from the inverter, which is what
# happens every evening when the inverter powers down. Other codes have been
# seen only while it was in contact, so anything else counts as connected
# rather than being mapped to a meaning we cannot confirm.
STATUS_DISCONNECTED = "-1"


def _connected(data: dict[str, Any]) -> bool | None:
    """Return whether the portal is still in contact with the inverter."""
    status = data.get("status")
    if status is None:
        return None
    return str(status) != STATUS_DISCONNECTED


@dataclass(frozen=True, kw_only=True)
class IntelbrasSolarBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe an Intelbras Solar binary sensor."""

    value_fn: Callable[[dict[str, Any]], bool | None]


INVERTER_BINARY_SENSORS: tuple[IntelbrasSolarBinarySensorEntityDescription, ...] = (
    IntelbrasSolarBinarySensorEntityDescription(
        key="status",
        translation_key="connection",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_connected,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: IntelbrasSolarConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the binary sensors of every inverter of the account."""
    coordinator = entry.runtime_data
    async_add_entities(
        IntelbrasSolarInverterBinarySensor(coordinator, serial_number, description)
        for serial_number in coordinator.data.inverters
        for description in INVERTER_BINARY_SENSORS
    )


class IntelbrasSolarInverterBinarySensor(
    IntelbrasSolarInverterEntity, BinarySensorEntity
):
    """A binary sensor reading a field of an inverter record."""

    entity_description: IntelbrasSolarBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: IntelbrasSolarDataUpdateCoordinator,
        serial_number: str,
        description: IntelbrasSolarBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, serial_number)
        self.entity_description = description
        self._attr_unique_id = f"{serial_number}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return whether the portal is in contact with the inverter."""
        return self.entity_description.value_fn(self.inverter.data)
