"""Intelbras Solar API"""
import requests
import json
from .const import BASE_URL, DOMAIN
from homeassistant.const import ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY
from homeassistant.components.sensor import SensorEntity, SensorStateClass


def list_of_plants(username: str, password: str) -> list:
    """Get List of Plants from a login"""
    plants = []
    # POST /login
    # {"result":1}
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
        # [{"id":"2222","timezone":"-3","plantName":"My Plant Name"}]
        response = session.post(BASE_URL + "index/getPlantListTitle")
        plants = response.json()
        return plants
    else:
        print("ERROR: ", response.text)
        return None


class IntelbrasPowerPlant(SensorEntity):
    """Representation of Power Plant"""

    def __iter__(self):
        pass

    def __init__(self, username: str, password: str, plantId: str) -> None:
        """Initialize the sensor."""
        self.username = username
        self.password = password
        self.plantId = plantId
        self.session = requests.Session()
        self._state = None
        if self._login():
            self.plant = self._get_plant_information()

    def _login(self) -> bool:
        """Login to Intelbras Solar Monitoring Site"""
        # POST /login
        # {"result":1}
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
        else:
            print("ERROR: ", response.text)
            return False

    def _get_plant_information(self) -> dict:
        """Get information about the Plant"""
        # POST panel/getPlantData
        # {"result":1,"obj":{"valleyPeriodPrice":"1.0","formulaTree":"0.055","flatPeriodPrice":"1.1","co2":"1283.5","lng":"-45.702","designCompany":"0","moneyUnit":"REAL","peakPeriodPrice":"1.3","formulaCoal":"0.4","city":"Rio","nominalPower":"5350","id":"2222","timezone":"-3","tree":"71","coal":"515","locationImg":"null","fixedPowerPrice":"1.2","moneyUnitText":"R$","lat":"-22.219","plantImg":"images1645555566.jpg","plantName":"My Plant Name","creatDate":"2022-03-03","eTotal":"1287.4","formulaCo2":"0.997","plantType":"0","country":"Brazil","accountName":"Jane Smith","formulaMoney":"0.0","isShare":"false"}}
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
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return ENERGY_KILO_WATT_HOUR

    @property
    def device_class(self) -> str:
        """Return the class of device."""
        return DEVICE_CLASS_ENERGY

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