"""Sensor platform for the Intelbras Solar integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfEnergy, UnitOfPower

from .entity import IntelbrasSolarInverterEntity, IntelbrasSolarPlantEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
    from homeassistant.helpers.typing import StateType

    from .coordinator import (
        IntelbrasSolarConfigEntry,
        IntelbrasSolarDataUpdateCoordinator,
    )

# The portal reports every reading as a string, and timestamps in the plant's
# own local time with the offset carried in a separate field.
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def _as_float(value: Any) -> StateType:
    """Return a portal reading as a float, or None when it is not a number."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_timestamp(data: dict[str, Any], key: str) -> datetime | None:
    """Return a portal timestamp anchored to the plant's UTC offset."""
    raw = data.get(key)
    if not raw:
        return None
    try:
        naive = datetime.strptime(str(raw), TIMESTAMP_FORMAT)  # noqa: DTZ007
    except ValueError:
        return None
    try:
        offset = timezone(timedelta(hours=float(data.get("timezone"))))
    except (TypeError, ValueError):
        offset = UTC
    return naive.replace(tzinfo=offset)


@dataclass(frozen=True, kw_only=True)
class IntelbrasSolarSensorEntityDescription(SensorEntityDescription):
    """Describe an Intelbras Solar sensor."""

    value_fn: Callable[[dict[str, Any]], StateType | datetime]
    # Sensors that predate this platform keep the bare plant id or serial
    # number as their unique id, so existing entity ids and history survive.
    legacy_unique_id: bool = False


PLANT_SENSORS: tuple[IntelbrasSolarSensorEntityDescription, ...] = (
    IntelbrasSolarSensorEntityDescription(
        key="eTotal",
        translation_key="energy_total",
        legacy_unique_id=True,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: _as_float(data.get("eTotal")),
    ),
)

INVERTER_SENSORS: tuple[IntelbrasSolarSensorEntityDescription, ...] = (
    IntelbrasSolarSensorEntityDescription(
        key="pac",
        translation_key="instant_power",
        legacy_unique_id=True,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: _as_float(data.get("pac")),
    ),
    IntelbrasSolarSensorEntityDescription(
        key="eToday",
        translation_key="energy_today",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: _as_float(data.get("eToday")),
    ),
    IntelbrasSolarSensorEntityDescription(
        key="eMonth",
        translation_key="energy_month",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: _as_float(data.get("eMonth")),
    ),
    IntelbrasSolarSensorEntityDescription(
        key="eTotal",
        translation_key="energy_total",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: _as_float(data.get("eTotal")),
    ),
    IntelbrasSolarSensorEntityDescription(
        key="lastUpdateTime",
        translation_key="last_update",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _as_timestamp(data, "lastUpdateTime"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: IntelbrasSolarConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensors of every plant and inverter of the account."""
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [
        IntelbrasSolarPlantSensor(coordinator, plant_id, description)
        for plant_id in coordinator.data.plants
        for description in PLANT_SENSORS
    ]
    entities.extend(
        IntelbrasSolarInverterSensor(coordinator, serial_number, description)
        for serial_number in coordinator.data.inverters
        for description in INVERTER_SENSORS
    )
    async_add_entities(entities)


class IntelbrasSolarPlantSensor(IntelbrasSolarPlantEntity, SensorEntity):
    """A sensor reading a field of the plant record."""

    entity_description: IntelbrasSolarSensorEntityDescription

    def __init__(
        self,
        coordinator: IntelbrasSolarDataUpdateCoordinator,
        plant_id: str,
        description: IntelbrasSolarSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, plant_id)
        self.entity_description = description
        self._attr_unique_id = (
            plant_id
            if description.legacy_unique_id
            else f"{plant_id}_{description.key}"
        )

    @property
    def native_value(self) -> StateType | datetime:
        """Return the current reading."""
        return self.entity_description.value_fn(self.plant.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose the raw plant record, as this platform always has."""
        if not self.entity_description.legacy_unique_id:
            return None
        return self.plant.data


class IntelbrasSolarInverterSensor(IntelbrasSolarInverterEntity, SensorEntity):
    """A sensor reading a field of an inverter record."""

    entity_description: IntelbrasSolarSensorEntityDescription

    def __init__(
        self,
        coordinator: IntelbrasSolarDataUpdateCoordinator,
        serial_number: str,
        description: IntelbrasSolarSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, serial_number)
        self.entity_description = description
        self._attr_unique_id = (
            serial_number
            if description.legacy_unique_id
            else f"{serial_number}_{description.key}"
        )

    @property
    def native_value(self) -> StateType | datetime:
        """Return the current reading."""
        return self.entity_description.value_fn(self.inverter.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose the raw inverter record, as this platform always has."""
        if not self.entity_description.legacy_unique_id:
            return None
        return self.inverter.data
