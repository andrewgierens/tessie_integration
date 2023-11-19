"""The tessie integration."""
from __future__ import annotations

from asyncio import timeout
from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession
from tessie_api import get_state_of_all_vehicles

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import ACCESS_TOKEN, DOMAIN, MANUFACTURER, NAME
from .services import async_setup_services

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SEMS Portal from a config entry."""

    async_setup_services(hass, entry)

    accessToken: str = entry.data[ACCESS_TOKEN]
    websession = async_get_clientsession(hass)

    coordinator = TessieDataUpdateCoordinator(hass, websession, accessToken)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class TessieDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching AccuWeather data API."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        token: str,
    ) -> None:
        """Initialize."""
        self.session = session
        self.token = token
        self.device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, MANUFACTURER)},
            manufacturer=MANUFACTURER,
            name=NAME,
            configuration_url=("https://tessie.com"),
        )

        update_interval = timedelta(minutes=5)
        _LOGGER.debug("Data will be update every %s", update_interval)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            async with timeout(10):
                active_vehicles = await get_state_of_all_vehicles(
                    self.session, self.token, True
                )
        except (
            ClientResponseError,
            ClientError,
            Exception,
        ) as error:
            raise UpdateFailed(error) from error

        return active_vehicles
