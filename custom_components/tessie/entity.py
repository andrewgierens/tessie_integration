"""Base class for Tessie sensors."""

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN, TessieDataUpdateCoordinator


class BaseTessieSensor(CoordinatorEntity, SensorEntity):
    """Base class for Tessie Sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        name: str,
        model: str,
        vin: str,
        config_entry: ConfigEntry,
        description: SensorEntityDescription,
        coordinator: TessieDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor."""

        super().__init__(coordinator)

        self.deviceName = name
        self.deviceModel = model
        self.vin = vin
        self.coordinator = coordinator
        self._config_entry_id = config_entry.entry_id
        self.entity_description = description
        self._attr_unique_id = f"{name}-{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, name)},
            manufacturer="Tessie",
            model=model,
            name=name,
        )
