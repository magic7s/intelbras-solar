"""Intelbras Solar API."""

import json

import requests
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.components.sensor.const import (
    SensorDeviceClass,
)
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
)

from .const import BASE_URL


class IntelbrasSolarApiClientError(Exception):
    """Exception to indicate a general API error."""


def list_of_plants(username: str, password: str) -> list:
    """Get List of Plants from a login."""
    # POST /login
    # {"result":1}  # noqa: ERA001
    session = requests.Session()
    response = session.post(
        BASE_URL + "login",
        data={
            "account": username,
            "password": password,
            "validateCode": "",
            "lang": "en",
        },
    )
    if response.json().get("result") == 1:
        # POST /index/getPlantListTitle
        # [{"id":"2222","timezone":"-3","plantName":"My Plant Name"}] # noqa: ERA001
        response = session.post(BASE_URL + "index/getPlantListTitle")
        return [response.json()]
    raise IntelbrasSolarApiClientError(
        response.text,
    )
    return None


def list_of_devices_in_plant(username: str, password: str, plantId: str) -> list:  # noqa: N803
    """Get List of Plants from a login."""
    # POST /login
    # {"result":1} # noqa: ERA001
    session = requests.Session()
    response = session.post(
        BASE_URL + "login",
        data={
            "account": username,
            "password": password,
            "validateCode": "",
            "lang": "en",
        },
    )
    if response.json().get("result") == 1:
        # POST panel/getDevicesByPlantList
        # {"result":1,"obj":{"currPage":1,"pages":1,"pageSize":4,"count":1,"ind":1,"datas":[{"pac":"0.7","sn":"ASF4K655557066A","plantName":"My Plant Name","location":"","alias":"ASF45555470555A","status":"1","eToday":"27.6","lastUpdateTime":"2022-04-06 18:14:22","datalogSn":"HPEXX333330935","datalogTypeTest":"EPWU 2000","deviceModel":"EGT 4600 PRO","bdcStatus":"0","deviceTypeName":"tlx","eTotal":"699.5","eMonth":"144.7","nominalPower":"4600","accountName":"Jane Smith","timezone":"-3","timeServer":"2022-04-07 05:14:22","plantId":"222224","deviceType":"0"}],"notPager":false}}  # noqa: E501, ERA001
        response = session.post(
            BASE_URL + "panel/getDevicesByPlantList",
            data={"plantId": plantId, "currPage": 1},
        )
        all_devices = json.loads(response.text)
        return all_devices["obj"]["datas"]
    raise IntelbrasSolarApiClientError(
        response.text,
    )
    return None


class IntelbrasPowerPlant(SensorEntity):
    """Representation of Power Plant."""

    def __init__(self, username: str, password: str, plantId: str) -> None:  # noqa: N803
        """Initialize the sensor."""
        self.username = username
        self.password = password
        self.plantId = plantId
        self.session = requests.Session()
        self._state = None
        if self._login():
            self.plant = self._get_plant_information()

    def _login(self) -> bool:
        """Login to Intelbras Solar Monitoring Site."""
        # POST /login
        # {"result":1} # noqa: ERA001
        response = self.session.post(
            BASE_URL + "login",
            data={
                "account": self.username,
                "password": self.password,
                "validateCode": "",
                "lang": "en",
            },
        )
        if response.json().get("result") == 1:
            return True
        raise IntelbrasSolarApiClientError(
            response.text,
        )
        return False

    def _get_plant_information(self) -> dict:
        """Get information about the Plant."""
        # POST panel/getPlantData
        # {"result":1,"obj":{"valleyPeriodPrice":"1.0","formulaTree":"0.055","flatPeriodPrice":"1.1","co2":"1283.5","lng":"-45.702","designCompany":"0","moneyUnit":"REAL","peakPeriodPrice":"1.3","formulaCoal":"0.4","city":"Rio","nominalPower":"5350","id":"2222","timezone":"-3","tree":"71","coal":"515","locationImg":"null","fixedPowerPrice":"1.2","moneyUnitText":"R$","lat":"-22.219","plantImg":"images1645555566.jpg","plantName":"My Plant Name","creatDate":"2022-03-03","eTotal":"1287.4","formulaCo2":"0.997","plantType":"0","country":"Brazil","accountName":"Jane Smith","formulaMoney":"0.0","isShare":"false"}}  # noqa: E501, ERA001
        response = self.session.post(
            BASE_URL + "panel/getPlantData", data={"plantId": self.plantId}
        )
        data = json.loads(response.text)
        return data["obj"]

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.plant["plantName"]

    @property
    def unique_id(self) -> str:
        """Return the plantId as the unique id."""
        return self.plant["id"]

    @property
    def state(self) -> None:
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def device_class(self) -> str:
        """Return the class of device."""
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self) -> str:
        """Return type of value calculation."""
        return SensorStateClass.TOTAL_INCREASING

    @property
    def extra_state_attributes(self) -> dict:
        """Return all the received plant data."""
        return self.plant

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        self._state = self._get_plant_information()["eTotal"]


class IntelbrasDataLogger(SensorEntity):
    """Representation of Power Plant."""

    def __init__(
        self,
        username: str,
        password: str,
        plantId: str,  # noqa: N803
        serialnumber: str,
    ) -> None:
        """Initialize the sensor."""
        self.username = username
        self.password = password
        self.plantId = plantId
        self.serialnumber = serialnumber
        self.session = requests.Session()
        self._state = None
        if self._login():
            self.device = self._get_device_information()

    def _login(self) -> bool:
        """Login to Intelbras Solar Monitoring Site."""
        # POST /login
        # {"result":1} # noqa: ERA001
        response = self.session.post(
            BASE_URL + "login",
            data={
                "account": self.username,
                "password": self.password,
                "validateCode": "",
                "lang": "en",
            },
        )
        if response.json().get("result") == 1:
            return True
        raise IntelbrasSolarApiClientError(
            response.text,
        )
        return False

    def _get_device_information(self) -> dict:
        """Get information about device in the Plant."""
        # POST panel/getDevicesByPlantList
        # {"result":1,"obj":{"currPage":1,"pages":1,"pageSize":4,"count":1,"ind":1,"datas":[{"pac":"0.7","sn":"ASF4K555557066A","plantName":"My Plant Name ","location":"","alias":"ASF4K555557066A","status":"1","eToday":"27.6","lastUpdateTime":"2022-04-06 18:14:22","datalogSn":"HPEX66666665","datalogTypeTest":"EPWU 2000","deviceModel":"EGT 4600 PRO","bdcStatus":"0","deviceTypeName":"tlx","eTotal":"699.5","eMonth":"144.7","nominalPower":"4600","accountName":"Jane Smith","timezone":"-3","timeServer":"2022-04-07 05:14:22","plantId":"22222","deviceType":"0"}],"notPager":false}}  # noqa: E501, ERA001
        response = self.session.post(
            BASE_URL + "panel/getDevicesByPlantList",
            data={"plantId": self.plantId, "currPage": 1},
        )
        device = {}
        all_devices = json.loads(response.text)
        for device in all_devices["obj"]["datas"]:
            if device["sn"] == self.serialnumber:
                return device
        return device

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self.device["alias"]

    @property
    def unique_id(self) -> str:
        """Return the plantId as the unique id."""
        return self.device["sn"]

    @property
    def state(self) -> None:
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfPower.WATT

    @property
    def device_class(self) -> str:
        """Return the class of device."""
        return SensorDeviceClass.POWER

    @property
    def state_class(self) -> str:
        """Return type of value calculation."""
        return SensorStateClass.MEASUREMENT

    @property
    def extra_state_attributes(self) -> dict:
        """Return all the received plant data."""
        return self.device

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        self._state = self._get_device_information()["pac"]
