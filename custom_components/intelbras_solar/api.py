"""Sample API Client."""
import logging
import asyncio
import socket
import json
from typing import Optional
import aiohttp
import async_timeout
from numpy import array

from .const import BASE_URL

TIMEOUT = 10


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class ApiClient:
    """Get Intelbrs Solar Monitoring Data"""

    def __init__(
        self, username: str, password: str, session: aiohttp.ClientSession
    ) -> None:
        """API Client."""
        self._username = username
        self._password = password
        self._session = session

    async def async_login(self) -> bool:
        """POST Login to Web Portal"""
        url = BASE_URL + "login"
        response = await self.api_wrapper(
            "post",
            url,
            data={
                "account": self._username,
                "password": self._password,
                "validateCode": "",
                "lang": "en",
            },
        )
        if response["result"] == 1:
            return True
        else:
            _LOGGER.error("Login Failed - %s", response["msg"])
            return False

    async def async_plant_list(self) -> list:
        """GET List of Power Plants"""
        url = BASE_URL + "index/getPlantListTitle"
        response = await self.api_wrapper("get", url)
        if len(response) < 1:
            _LOGGER.error("No plants returned after login - %s", response)
            return False
        return response

    async def async_get_data(self, plant_id) -> dict:
        """Get data from the API."""
        solar_stats = {}
        plants =[]
        await self.async_login()
        plants = await self.async_plant_list()
        for plant in plants:
            solar_stats.
        url = BASE_URL + "panel/getDevicesByPlantList"
        return await self.api_wrapper("post", url, data={"plantId": plant_id, "currPage": 1})

    async def async_set_title(self, value: str) -> None:
        """Get data from the API."""
        url = "https://jsonplaceholder.typicode.com/posts/1"
        await self.api_wrapper("patch", url, data={"title": value}, headers=HEADERS)

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                if method == "get":
                    response = await self._session.get(url, headers=headers)
                    return await response.json(content_type=None)

                elif method == "put":
                    await self._session.put(url, headers=headers, json=data)

                elif method == "patch":
                    await self._session.patch(url, headers=headers, json=data)

                elif method == "post":
                    response = await self._session.post(url, headers=headers, data=data)
                    return await response.json(content_type=None)

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
