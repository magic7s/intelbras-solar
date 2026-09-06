"""Constants for the Intelbras Solar integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "intelbras_solar"
NAME: Final = "Intelbras Solar"
MANUFACTURER: Final = "Intelbras"
ISSUE_URL: Final = "https://github.com/magic7s/intelbras-solar/issues"

BASE_URL: Final = "http://solar-monitoramento.intelbras.com.br/"

PLATFORMS: Final[list[Platform]] = [Platform.SENSOR]

# The portal itself only refreshes inverter data every few minutes, so there is
# nothing to gain from polling faster than this.
SCAN_INTERVAL: Final = timedelta(minutes=5)

LOGGER: Final = logging.getLogger(__package__)
