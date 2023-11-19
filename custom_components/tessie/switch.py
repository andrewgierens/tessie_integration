"""Switch for performing actions against Tesla."""

from abc import ABC, abstractmethod
from typing import Any

from aiohttp import ClientSession
from tessie_api import (
    close_charge_port,
    disable_sentry_mode,
    disable_valet_mode,
    enable_sentry_mode,
    enable_valet_mode,
    lock,
    open_unlock_charge_port,
    start_charging,
    start_climate_preconditioning,
    start_steering_wheel_heater,
    stop_charging,
    stop_climate,
    stop_steering_wheel_heater,
    unlock,
)

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ACCESS_TOKEN, DOMAIN, MANUFACTURER, TessieDataUpdateCoordinator


def traverse_nested_dict(data_dict, key_path):
    """Get a value by a dot notation."""

    keys = key_path.split(".")
    value = data_dict
    for key in keys:
        value = value.get(key)
        if value is None:
            return None
    return value


def set_nested_dict_value(data_dict, key_path, value):
    """Set a value in a nested dictionary using a dot notation key path."""

    keys = key_path.split(".")
    for key in keys[:-1]:  # Go until the second last key
        data_dict = data_dict.setdefault(
            key, {}
        )  # Get the dict, or create an empty one if the key doesn't exist
    data_dict[keys[-1]] = value  # Set the value for the last key


def set_vehicle_charging_state(coordinator, vin, key, value):
    """Set the charging state for a vehicle by its VIN."""
    for vehicle in coordinator.data["results"]:
        if vehicle["vin"] == vin:
            set_nested_dict_value(vehicle, key, value)
            break


def getCarByVin(coordinator, vin: str) -> Any:
    """Retrieve the car by VIN."""
    for car in coordinator.data["results"]:
        if car["vin"] == vin:
            return car
    return None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the switches for the Ring devices."""
    coordinator: TessieDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    cars = coordinator.data["results"]
    session = async_get_clientsession(hass)

    switches: list[TessieSwitchBase] = []
    for car in cars:
        switches.append(
            TessieChargerSwitch(
                coordinator,
                session,
                "last_state.charge_state.charging_state",
                "charging_state_switch",
                car["last_state"]["display_name"],
                car["last_state"]["vehicle_config"]["car_type"],
                config_entry.data[ACCESS_TOKEN],
                "Charging",
                "Stopped",
                car["vin"],
            )
        )

        switches.append(
            TessieChargePortSwitch(
                coordinator,
                session,
                "last_state.charge_state.charge_port_door_open",
                "charge_port_door_open_switch",
                car["last_state"]["display_name"],
                car["last_state"]["vehicle_config"]["car_type"],
                config_entry.data[ACCESS_TOKEN],
                True,
                False,
                car["vin"],
            )
        )
        switches.append(
            TessieClimateSwitch(
                coordinator,
                session,
                "last_state.climate_state.is_climate_on",
                "is_climate_on_switch",
                car["last_state"]["display_name"],
                car["last_state"]["vehicle_config"]["car_type"],
                config_entry.data[ACCESS_TOKEN],
                True,
                False,
                car["vin"],
            )
        )
        switches.append(
            TessieSteeringWheelHeatSwitch(
                coordinator,
                session,
                "last_state.climate_state.steering_wheel_heater",
                "steering_wheel_heater_switch",
                car["last_state"]["display_name"],
                car["last_state"]["vehicle_config"]["car_type"],
                config_entry.data[ACCESS_TOKEN],
                True,
                False,
                car["vin"],
            )
        )
        switches.append(
            TessieLockSwitch(
                coordinator,
                session,
                "last_state.vehicle_state.locked",
                "locked_switch",
                car["last_state"]["display_name"],
                car["last_state"]["vehicle_config"]["car_type"],
                config_entry.data[ACCESS_TOKEN],
                True,
                False,
                car["vin"],
            )
        )
        switches.append(
            TessieSentryModeSwitch(
                coordinator,
                session,
                "last_state.vehicle_state.sentry_mode",
                "sentry_mode_switch",
                car["last_state"]["display_name"],
                car["last_state"]["vehicle_config"]["car_type"],
                config_entry.data[ACCESS_TOKEN],
                True,
                False,
                car["vin"],
            )
        )
        switches.append(
            TessieValetModeSwitch(
                coordinator,
                session,
                "last_state.vehicle_state.valet_mode",
                "valet_mode_switch",
                car["last_state"]["display_name"],
                car["last_state"]["vehicle_config"]["car_type"],
                config_entry.data[ACCESS_TOKEN],
                True,
                False,
                car["vin"],
            )
        )

    async_add_entities(switches)


class TessieSwitchBase(CoordinatorEntity, SwitchEntity, ABC):
    """Base class for Tessie switches."""

    has_entity_name = True

    def __init__(
        self,
        coordinator,
        session: ClientSession,
        key: str,
        translation_key: str,
        name: str,
        model: str,
        apiKey: str,
        on_value: str | bool,
        off_value: str | bool,
        vin: str,
    ) -> None:
        """Initialize the Tessie switch."""
        super().__init__(coordinator)
        self._session = session
        self._apiKey = apiKey
        self._key = key
        self._name = name
        self._translation_key = translation_key
        self._model = model
        self._vin = vin
        self._on_value = on_value
        self._off_value = off_value

    @property
    def translation_key(self) -> str:
        """Return the translation key of the switch."""
        return self._translation_key

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info for the switch."""
        return DeviceInfo(
            identifiers={(DOMAIN, MANUFACTURER)},
            name=self._name,
            manufacturer=MANUFACTURER,
            model=self._model,
        )

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the switch."""
        return f"{self._key}.switch"

    @property
    def is_on(self) -> bool:
        """Return whether the switch is on."""
        value = traverse_nested_dict(
            getCarByVin(self.coordinator, self._vin), self._key
        )
        return value == self._on_value

    @abstractmethod
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""

    @abstractmethod
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""


class TessieChargerSwitch(TessieSwitchBase):
    """A class for the actual switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await start_charging(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._on_value
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await stop_charging(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._off_value
        )
        self.async_write_ha_state()


class TessieChargePortSwitch(TessieSwitchBase):
    """A class for the actual switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await open_unlock_charge_port(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._on_value
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await close_charge_port(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._off_value
        )
        self.async_write_ha_state()


class TessieClimateSwitch(TessieSwitchBase):
    """A class for the actual switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await start_climate_preconditioning(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._on_value
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await stop_climate(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._off_value
        )
        self.async_write_ha_state()


class TessieSteeringWheelHeatSwitch(TessieSwitchBase):
    """A class for the actual switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await start_steering_wheel_heater(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._on_value
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await stop_steering_wheel_heater(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._off_value
        )
        self.async_write_ha_state()


class TessieLockSwitch(TessieSwitchBase):
    """A class for the actual switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await lock(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._on_value
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await unlock(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._off_value
        )
        self.async_write_ha_state()


class TessieSentryModeSwitch(TessieSwitchBase):
    """A class for the actual switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await enable_sentry_mode(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._on_value
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await disable_sentry_mode(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._off_value
        )
        self.async_write_ha_state()


class TessieValetModeSwitch(TessieSwitchBase):
    """A class for the actual switch."""

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await enable_valet_mode(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._on_value
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await disable_valet_mode(self._session, self._vin, self._apiKey)
        set_vehicle_charging_state(
            self.coordinator, self._vin, self._key, self._off_value
        )
        self.async_write_ha_state()
