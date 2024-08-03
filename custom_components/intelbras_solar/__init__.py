"""Intelbras Solar Dashboard HASS Integration"""

from __future__ import annotations
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
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
        "temperature": 23,
        CONF_USERNAME: config[DOMAIN][CONF_USERNAME],
        CONF_PASSWORD: config[DOMAIN][CONF_PASSWORD],
    }
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)

    return True
