"""Sensor for retrieving data for SEMS portal."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    Platform,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, TessieDataUpdateCoordinator
from .entity import BaseTessieSensor


def traverse_nested_dict(data_dict, key_path):
    """Get a value by a dot notation."""

    keys = key_path.split(".")
    value = data_dict
    for key in keys:
        value = value.get(key)
        if value is None:
            return None
    return value


class TessieCarSensor(BaseTessieSensor):
    """Used to represent a SemsInformationSensor."""

    def getCarByVin(self, coordinator: TessieDataUpdateCoordinator, vin: str) -> Any:
        """Retrieve the inverter by name."""

        for car in coordinator.data["results"]:
            if car["vin"] == vin:
                return car
        return None

    @property
    def native_value(self):
        """Return the state of the sensor."""

        return traverse_nested_dict(
            self.getCarByVin(self.coordinator, self.vin), self.entity_description.key
        )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Get the setup sensor."""

    coordinator: TessieDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    cars = coordinator.data["results"]

    teslaCarInfoEntities = [
        TessieCarSensor(
            car["last_state"]["display_name"],
            car["last_state"]["vehicle_config"]["car_type"],
            car["vin"],
            config_entry,
            description,
            coordinator,
        )
        for description in SENSOR_INFO_TYPES_TESLA
        for car in cars
    ]

    async_add_entities(teslaCarInfoEntities)


SENSOR_INFO_TYPES_TESLA: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        translation_key="display_name",
        key="last_state.display_name",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="vin",
        key="vin",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="battery_heater_on",
        key="last_state.charge_state.battery_heater_on",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="battery_level",
        key="last_state.charge_state.battery_level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
    ),
    SensorEntityDescription(
        translation_key="battery_range",
        key="last_state.charge_state.battery_range",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
    ),
    SensorEntityDescription(
        translation_key="charge_amps",
        key="last_state.charge_state.charge_amps",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
    ),
    SensorEntityDescription(
        translation_key="charge_current_request",
        key="last_state.charge_state.charge_current_request",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
    ),
    SensorEntityDescription(
        translation_key="charge_current_request_max",
        key="last_state.charge_state.charge_current_request_max",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
    ),
    SensorEntityDescription(
        translation_key="charge_enable_request",
        key="last_state.charge_state.charge_enable_request",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="charge_energy_added",
        key="last_state.charge_state.charge_energy_added",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    SensorEntityDescription(
        translation_key="charge_limit_soc",
        key="last_state.charge_state.charge_limit_soc",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
    ),
    SensorEntityDescription(
        translation_key="charge_limit_soc_max",
        key="last_state.charge_state.charge_limit_soc_max",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
    ),
    SensorEntityDescription(
        translation_key="charge_limit_soc_min",
        key="last_state.charge_state.charge_limit_soc_min",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
    ),
    SensorEntityDescription(
        translation_key="charge_limit_soc_std",
        key="last_state.charge_state.charge_limit_soc_std",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
    ),
    SensorEntityDescription(
        translation_key="charge_miles_added_ideal",
        key="last_state.charge_state.charge_miles_added_ideal",
        native_unit_of_measurement=UnitOfLength.MILES,
        device_class=SensorDeviceClass.DISTANCE,
    ),
    SensorEntityDescription(
        translation_key="charge_miles_added_rated",
        key="last_state.charge_state.charge_miles_added_rated",
        native_unit_of_measurement=UnitOfLength.MILES,
        device_class=SensorDeviceClass.DISTANCE,
    ),
    SensorEntityDescription(
        translation_key="charge_port_cold_weather_mode",
        key="last_state.charge_state.charge_port_cold_weather_mode",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="charge_port_color",
        key="last_state.charge_state.charge_port_color",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="charge_port_door_open",
        key="last_state.charge_state.charge_port_door_open",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="charge_port_latch",
        key="last_state.charge_state.charge_port_latch",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="charge_rate",
        key="last_state.charge_state.charge_rate",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
    ),
    SensorEntityDescription(
        translation_key="charger_actual_current",
        key="last_state.charge_state.charger_actual_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
    ),
    SensorEntityDescription(
        translation_key="charger_phases",
        key="last_state.charge_state.charger_phases",
        native_unit_of_measurement=Platform.NUMBER,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="charger_pilot_current",
        key="last_state.charge_state.charger_pilot_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
    ),
    SensorEntityDescription(
        translation_key="charger_power",
        key="last_state.charge_state.charger_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        translation_key="charger_voltage",
        key="last_state.charge_state.charger_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
    ),
    SensorEntityDescription(
        translation_key="charging_state",
        key="last_state.charge_state.charging_state",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="conn_charge_cable",
        key="last_state.charge_state.conn_charge_cable",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="est_battery_range",
        key="last_state.charge_state.est_battery_range",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
    ),
    SensorEntityDescription(
        translation_key="fast_charger_brand",
        key="last_state.charge_state.fast_charger_brand",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="fast_charger_present",
        key="last_state.charge_state.fast_charger_present",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="fast_charger_type",
        key="last_state.charge_state.fast_charger_type",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="ideal_battery_range",
        key="last_state.charge_state.ideal_battery_range",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
    ),
    SensorEntityDescription(
        translation_key="max_range_charge_counter",
        key="last_state.charge_state.max_range_charge_counter",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="minutes_to_full_charge",
        key="last_state.charge_state.minutes_to_full_charge",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
    ),
    SensorEntityDescription(
        translation_key="not_enough_power_to_heat",
        key="last_state.charge_state.not_enough_power_to_heat",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="off_peak_charging_enabled",
        key="last_state.charge_state.off_peak_charging_enabled",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="off_peak_charging_times",
        key="last_state.charge_state.off_peak_charging_times",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="off_peak_hours_end_time",
        key="last_state.charge_state.off_peak_hours_end_time",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="preconditioning_enabled",
        key="last_state.charge_state.preconditioning_enabled",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="preconditioning_times",
        key="last_state.charge_state.preconditioning_times",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="scheduled_charging_mode",
        key="last_state.charge_state.scheduled_charging_mode",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="scheduled_charging_pending",
        key="last_state.charge_state.scheduled_charging_pending",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="scheduled_charging_start_time",
        key="last_state.charge_state.scheduled_charging_start_time",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="scheduled_departure_time",
        key="last_state.charge_state.scheduled_departure_time",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="scheduled_departure_time_minutes",
        key="last_state.charge_state.scheduled_departure_time_minutes",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="supercharger_session_trip_planner",
        key="last_state.charge_state.supercharger_session_trip_planner",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="time_to_full_charge",
        key="last_state.charge_state.time_to_full_charge",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
    ),
    SensorEntityDescription(
        translation_key="timestamp",
        key="last_state.charge_state.timestamp",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="trip_charging",
        key="last_state.charge_state.trip_charging",
        native_unit_of_measurement=None,
        device_class=None,
    ),
    SensorEntityDescription(
        translation_key="usable_battery_level",
        key="last_state.charge_state.usable_battery_level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
    ),
    SensorEntityDescription(
        translation_key="user_charge_enable_request",
        key="last_state.charge_state.user_charge_enable_request",
        native_unit_of_measurement=None,
        device_class=None,
    ),
)
