"""Config flow for tessie integration."""
from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientSession
from tessie_api import get_state_of_all_vehicles
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import ACCESS_TOKEN, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(ACCESS_TOKEN): str})


async def validate_input(
    session: ClientSession, data: dict[str, Any]
) -> dict[str, Any]:
    """Validate the incoming inputs."""
    accessToken = data[ACCESS_TOKEN]

    active_vehicles = await get_state_of_all_vehicles(session, accessToken, True)
    if "results" not in active_vehicles or not active_vehicles["results"]:
        raise InvalidAuth("No active vehicles found")

    return accessToken


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SEMS Portal."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        websession = async_get_clientsession(self.hass)

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_input(websession, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title="Tessie",
                    data={
                        ACCESS_TOKEN: user_input[ACCESS_TOKEN],
                    },
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
