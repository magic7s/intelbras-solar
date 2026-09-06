"""Fixtures for Intelbras Solar tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.intelbras_solar.const import DOMAIN
from custom_components.intelbras_solar.intelbras import (
    IntelbrasSolarData,
    Inverter,
    Plant,
)

MOCK_USERNAME = "test_user"
MOCK_PASSWORD = "test_password"

MOCK_PLANT_DATA = {
    "plantName": "My Solar Plant",
    "nominalPower": "5000",
    "eTotal": "1234.5",
    "co2": "980",
    "tree": "12",
}

MOCK_INVERTER_DATA = {
    "sn": "INV123456",
    "alias": "Inverter 1",
    "deviceModel": "Ecosol 5K",
    "status": 1,
    "pac": "3500",
    "eToday": "15.4",
    "eMonth": "250.0",
    "eTotal": "4321.0",
    "lastUpdateTime": "2026-09-06 14:30:00",
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None, None, None]:
    """Enable custom integrations in Home Assistant tests."""
    yield


@pytest.fixture
def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Return a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=MOCK_USERNAME,
        data={
            CONF_USERNAME: MOCK_USERNAME,
            CONF_PASSWORD: MOCK_PASSWORD,
        },
        unique_id=MOCK_USERNAME.lower(),
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_intelbras_data() -> IntelbrasSolarData:
    """Return sample IntelbrasSolarData snapshot."""
    data = IntelbrasSolarData()
    data.plants["123"] = Plant(
        identifier="123",
        name="My Solar Plant",
        data=MOCK_PLANT_DATA,
    )
    data.inverters["INV123456"] = Inverter(
        serial_number="INV123456",
        plant_id="123",
        name="Inverter 1",
        model="Ecosol 5K",
        data=MOCK_INVERTER_DATA,
    )
    return data


@pytest.fixture
def mock_api_client(
    mock_intelbras_data: IntelbrasSolarData,
) -> Generator[MagicMock, None, None]:
    """Mock the IntelbrasSolarApiClient."""
    with patch(
        "custom_components.intelbras_solar.IntelbrasSolarApiClient",
        autospec=True,
    ) as mock_client_class:
        client = mock_client_class.return_value
        client.login.return_value = None
        client.plants.return_value = [{"id": 123, "plantName": "My Solar Plant"}]
        client.plant_data.return_value = MOCK_PLANT_DATA
        client.devices.return_value = [MOCK_INVERTER_DATA]
        client.fetch.return_value = mock_intelbras_data
        yield client
