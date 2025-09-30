"""Platform for light integration."""

from __future__ import annotations

from typing import Any

import ayla_iot_unofficial
import ayla_iot_unofficial.device
from homeassistant.components.humidifier import (
    HumidifierEntity,
    HumidifierEntityFeature,
)

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from nomaiq import NomaIQConfigEntry
from nomaiq.const import DOMAIN
from nomaiq.coordinator import NomaIQDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NomaIQConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Noma IQ Switch platform."""
    coordinator: NomaIQDataUpdateCoordinator = entry.runtime_data

    for device in coordinator.data:
        if (
            "humidity" in device.properties_full
        ):
            async_add_entities(
                [NomaIQDehumidifierEntity(coordinator, device)], update_before_add=False
            )


class NomaIQDehumidifierEntity(HumidifierEntity):
    """Representation of a NomaIQ Dehumidifier."""

    def __init__(
        self,
        coordinator: NomaIQDataUpdateCoordinator,
        device: ayla_iot_unofficial.device.Device,
    ) -> None:
        """Initialize a NomaIQ Dehumidifier."""
        self.coordinator = coordinator
        self._device = device
        self._attr_supported_features = HumidifierEntityFeature.MODES
        self._attr_min_humidity = 30
        self._attr_max_humidity = 80
        self._attr_available_modes = ["Manual", "Continuous", "Auto Dry"]
        self._attr_name = device.get_property_value("product_name") or device.name
        self._attr_unique_id = f"nomaiq_dehumidifer_{device.serial_number}"
        self._attr_has_entity_name = device.get_property_value("product_name")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.serial_number)},
            name=device.name,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if dehumidifier is on."""
        data: list[ayla_iot_unofficial.device.Device] = self.coordinator.data
        device: ayla_iot_unofficial.device.Device | None = next(
            (d for d in data if d.serial_number == self._device.serial_number),
            None,
        )
        return device and device.get_property_value("power")

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn device on."""
        await self._device.async_set_property_value("power", 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn device off."""
        await self._device.async_set_property_value("power", 0)

    async def async_update(self) -> None:
        """Update the dehumidifier state."""
        await self.coordinator.async_request_refresh()
