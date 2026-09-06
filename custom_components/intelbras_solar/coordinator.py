"""Coordinator that keeps one poll of the portal shared by every entity."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, SCAN_INTERVAL
from .intelbras import (
    IntelbrasSolarApiClientError,
    IntelbrasSolarAuthError,
    IntelbrasSolarData,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .intelbras import IntelbrasSolarApiClient


class IntelbrasSolarDataUpdateCoordinator(DataUpdateCoordinator[IntelbrasSolarData]):
    """Fetch every plant and inverter of an account in one go."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: IntelbrasSolarApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> IntelbrasSolarData:
        """Refresh the snapshot in the executor; the client is blocking."""
        try:
            return await self.hass.async_add_executor_job(self.client.fetch)
        except IntelbrasSolarAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except IntelbrasSolarApiClientError as err:
            raise UpdateFailed(str(err)) from err


IntelbrasSolarConfigEntry = ConfigEntry[IntelbrasSolarDataUpdateCoordinator]
