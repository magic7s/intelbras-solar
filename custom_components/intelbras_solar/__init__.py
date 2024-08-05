"""Intelbras Solar Dashboard HASS Integration."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import discovery

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

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

SCAN_INTERVAL = timedelta(minutes=5)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""
    # Data that you want to share with your platforms
    hass.data[DOMAIN] = {
        CONF_USERNAME: config[DOMAIN][CONF_USERNAME],
        CONF_PASSWORD: config[DOMAIN][CONF_PASSWORD],
    }
    discovery.load_platform(
        hass=hass,
        component="sensor",
        platform=DOMAIN,
        discovered={},
        hass_config=config,
    )

    return True
