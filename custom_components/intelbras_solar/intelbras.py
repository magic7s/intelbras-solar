"""Client for the Intelbras Solar monitoring portal."""

# The portal is a rebranded ShineServer instance: it authenticates with a form
# POST that sets a session cookie, and every other endpoint is a POST returning
# JSON with a "result" flag.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import requests

from .const import BASE_URL, LOGGER

TIMEOUT = 30


class IntelbrasSolarApiClientError(Exception):
    """Exception to indicate a general API error."""


class IntelbrasSolarAuthError(IntelbrasSolarApiClientError):
    """Exception to indicate invalid credentials."""


@dataclass(slots=True)
class Plant:
    """A power plant as reported by the portal."""

    identifier: str
    name: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Inverter:
    """An inverter belonging to a plant."""

    serial_number: str
    plant_id: str
    name: str
    model: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class IntelbrasSolarData:
    """Snapshot of everything the portal exposes for an account."""

    plants: dict[str, Plant] = field(default_factory=dict)
    inverters: dict[str, Inverter] = field(default_factory=dict)


class IntelbrasSolarApiClient:
    """Talk to the Intelbras Solar monitoring portal."""

    def __init__(self, username: str, password: str) -> None:
        """Store the credentials; no network access happens here."""
        self._username = username
        self._password = password
        self._session = requests.Session()
        self._logged_in = False

    def _post(self, path: str, data: dict[str, Any] | None = None) -> Any:
        """POST to the portal and return the decoded JSON body."""
        try:
            response = self._session.post(
                BASE_URL + path, data=data or {}, timeout=TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            msg = f"Error talking to {path}: {err}"
            raise IntelbrasSolarApiClientError(msg) from err
        except ValueError as err:
            msg = f"Unexpected non-JSON response from {path}"
            raise IntelbrasSolarApiClientError(msg) from err

    def login(self) -> None:
        """Authenticate and keep the session cookie for later calls."""
        payload = self._post(
            "login",
            {
                "account": self._username,
                "password": self._password,
                "validateCode": "",
                "lang": "en",
            },
        )
        if not isinstance(payload, dict) or payload.get("result") != 1:
            msg = "The portal rejected the username or password"
            raise IntelbrasSolarAuthError(msg)
        self._logged_in = True

    def _ensure_login(self) -> None:
        """Log in if the session has not been established yet."""
        if not self._logged_in:
            self.login()

    def plants(self) -> list[dict[str, Any]]:
        """Return every plant visible to the account."""
        self._ensure_login()
        payload = self._post("index/getPlantListTitle")
        if not isinstance(payload, list):
            msg = "The plant list endpoint did not return a list"
            raise IntelbrasSolarApiClientError(msg)
        return payload

    def plant_data(self, plant_id: str) -> dict[str, Any]:
        """Return the detail record of a single plant."""
        self._ensure_login()
        payload = self._post("panel/getPlantData", {"plantId": plant_id})
        return self._unwrap(payload, "panel/getPlantData")

    def devices(self, plant_id: str) -> list[dict[str, Any]]:
        """Return every device (inverter) registered in a plant."""
        self._ensure_login()
        payload = self._post(
            "panel/getDevicesByPlantList", {"plantId": plant_id, "currPage": 1}
        )
        return self._unwrap(payload, "panel/getDevicesByPlantList").get("datas", [])

    @staticmethod
    def _unwrap(payload: Any, path: str) -> dict[str, Any]:
        """Pull the ``obj`` envelope out of a portal response."""
        if not isinstance(payload, dict) or not isinstance(payload.get("obj"), dict):
            msg = f"Unexpected response shape from {path}"
            raise IntelbrasSolarApiClientError(msg)
        return payload["obj"]

    def fetch(self) -> IntelbrasSolarData:
        """Return a full snapshot, retrying once if the session expired."""
        try:
            return self._fetch()
        except IntelbrasSolarAuthError:
            raise
        except IntelbrasSolarApiClientError as err:
            LOGGER.debug("Retrying after a failed poll: %s", err)
            self._logged_in = False
            return self._fetch()

    def _fetch(self) -> IntelbrasSolarData:
        """Walk every plant and its inverters in a single pass."""
        snapshot = IntelbrasSolarData()
        for entry in self.plants():
            plant_id = str(entry["id"])
            detail = self.plant_data(plant_id)
            snapshot.plants[plant_id] = Plant(
                identifier=plant_id,
                name=detail.get("plantName") or entry.get("plantName") or plant_id,
                data=detail,
            )
            for device in self.devices(plant_id):
                serial_number = str(device["sn"])
                snapshot.inverters[serial_number] = Inverter(
                    serial_number=serial_number,
                    plant_id=plant_id,
                    name=device.get("alias") or serial_number,
                    model=device.get("deviceModel") or "",
                    data=device,
                )
        return snapshot
