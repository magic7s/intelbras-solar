"""Test the Intelbras Solar config flow."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.intelbras_solar.const import DOMAIN
from custom_components.intelbras_solar.intelbras import (
    IntelbrasSolarApiClientError,
    IntelbrasSolarAuthError,
)
from tests.conftest import MOCK_PASSWORD, MOCK_USERNAME


async def test_form_user_success(hass: HomeAssistant) -> None:
    """Test successful user step creating a config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "custom_components.intelbras_solar.config_flow.IntelbrasSolarApiClient.plants",
        return_value=[{"id": 1}],
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: MOCK_USERNAME,
                CONF_PASSWORD: MOCK_PASSWORD,
            },
        )

    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["title"] == MOCK_USERNAME
    assert result2["data"] == {
        CONF_USERNAME: MOCK_USERNAME,
        CONF_PASSWORD: MOCK_PASSWORD,
    }
    assert result2["result"].unique_id == MOCK_USERNAME.lower()


async def test_form_user_invalid_auth(hass: HomeAssistant) -> None:
    """Test user step with invalid authentication."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.intelbras_solar.config_flow.IntelbrasSolarApiClient.plants",
        side_effect=IntelbrasSolarAuthError("Auth failed"),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: MOCK_USERNAME,
                CONF_PASSWORD: MOCK_PASSWORD,
            },
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["step_id"] == "user"
    assert result2["errors"] == {"base": "invalid_auth"}


async def test_form_user_cannot_connect(hass: HomeAssistant) -> None:
    """Test user step with connection failure."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.intelbras_solar.config_flow.IntelbrasSolarApiClient.plants",
        side_effect=IntelbrasSolarApiClientError("Connection error"),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: MOCK_USERNAME,
                CONF_PASSWORD: MOCK_PASSWORD,
            },
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["step_id"] == "user"
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_user_already_configured(hass: HomeAssistant) -> None:
    """Test user step when the account is already configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=MOCK_USERNAME.lower(),
        data={
            CONF_USERNAME: MOCK_USERNAME,
            CONF_PASSWORD: MOCK_PASSWORD,
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_USERNAME: MOCK_USERNAME,
            CONF_PASSWORD: MOCK_PASSWORD,
        },
    )

    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


async def test_import_flow_success(hass: HomeAssistant) -> None:
    """Test importing configuration from legacy YAML."""
    with patch(
        "custom_components.intelbras_solar.config_flow.IntelbrasSolarApiClient.plants",
        return_value=[{"id": 1}],
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data={
                CONF_USERNAME: MOCK_USERNAME,
                CONF_PASSWORD: MOCK_PASSWORD,
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == MOCK_USERNAME
    assert result["data"] == {
        CONF_USERNAME: MOCK_USERNAME,
        CONF_PASSWORD: MOCK_PASSWORD,
    }


async def test_import_flow_failure(hass: HomeAssistant) -> None:
    """Test import failure aborts the flow."""
    with patch(
        "custom_components.intelbras_solar.config_flow.IntelbrasSolarApiClient.plants",
        side_effect=IntelbrasSolarAuthError("Bad credentials"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data={
                CONF_USERNAME: MOCK_USERNAME,
                CONF_PASSWORD: MOCK_PASSWORD,
            },
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "invalid_auth"


async def test_reauth_flow_success(hass: HomeAssistant) -> None:
    """Test reauthentication flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=MOCK_USERNAME.lower(),
        data={
            CONF_USERNAME: MOCK_USERNAME,
            CONF_PASSWORD: "old_password",
        },
    )
    entry.add_to_hass(hass)

    result = await entry.start_reauth_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    with (
        patch(
            "custom_components.intelbras_solar.config_flow.IntelbrasSolarApiClient.plants",
            return_value=[{"id": 1}],
        ),
        patch("homeassistant.config_entries.ConfigEntries.async_reload") as mock_reload,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: MOCK_USERNAME,
                CONF_PASSWORD: "new_password",
            },
        )

    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "reauth_successful"
    assert entry.data[CONF_PASSWORD] == "new_password"
    assert len(mock_reload.mock_calls) == 1
