"""Constants for integration_blueprint."""

# Base component constants
NAME = "Intelbras Solar"
DOMAIN = "intelbras_solar"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.5"
ATTRIBUTION = ""
ISSUE_URL = "https://github.com/magic7s/intelbras-solar/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
BASE_URL = "http://solar-monitoramento.intelbras.com.br/"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This integration is to access Intelbras Solar statistics.
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
