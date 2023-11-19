"""Class to handle service logic."""

from tessie_api import set_charging_amps

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import ACCESS_TOKEN, DOMAIN


def get_vin_from_device_id(hass: HomeAssistant, deviceId: str) -> str | None:
    """Get vin from device."""

    entReg = er.async_get(hass)

    for entity in entReg.entities.values():
        if entity.device_id == deviceId and entity.entity_id.endswith("_vin"):
            state = hass.states.get(entity.entity_id)
            if state is not None:
                return state.state
    return None


@callback
def async_setup_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Set up the asynchronous service."""

    async def handle_set_charging_amps(call: ServiceCall):
        deviceId = call.data.get("vehicle")
        amps = call.data.get("amps")
        entity_amps = call.data.get("entity_amps")

        if deviceId is None:
            return

        if entity_amps is not None:
            if entity_amps:
                state = hass.states.get(entity_amps)
                if state and state.state.isdigit():
                    amps = float(state.state)

        if amps is None and entity_amps is None:
            return

        vin = get_vin_from_device_id(hass, deviceId)
        accessToken: str = entry.data[ACCESS_TOKEN]
        websession = async_get_clientsession(hass)

        await set_charging_amps(websession, vin, accessToken, amps)

    # Register services with home assistant
    hass.services.async_register(DOMAIN, "set_charging_amps", handle_set_charging_amps)
