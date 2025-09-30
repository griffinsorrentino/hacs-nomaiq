"""Platform for light integration."""

from __future__ import annotations

from typing import Any

import ayla_iot_unofficial
import ayla_iot_unofficial.device
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.humidifier import (
    HumidifierEntity,
    HumidifierEntityFeature,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from custom_components.nomaiq import NomaIQConfigEntry
from custom_components.nomaiq.const import DOMAIN
from custom_components.nomaiq.coordinator import NomaIQDataUpdateCoordinator

MODE_MAP = {
    "Manual": "Normal",
    "Continuous": "Persistent",
    "Auto Dry": "Auto",
}
AYLA_TO_HASS_MODE = {v: k for k, v in MODE_MAP.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NomaIQConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Noma IQ Switch platform."""
    coordinator: NomaIQDataUpdateCoordinator = entry.runtime_data

    for device in coordinator.data:
        if (
            "filter_clean_alarm" in device.properties_full
        ):
            async_add_entities(
                [NomaIQTankFullSensor(coordinator, device), NomaIQFilterAlertSensor(coordinator, device)], update_before_add=False
            )


class NomaIQTankFullSensor(BinarySensorEntity):

    def __init__(
        self,
        coordinator: NomaIQDataUpdateCoordinator,
        device: ayla_iot_unofficial.device.Device,
    ) -> None:
        self.coordinator = coordinator
        self._device = device
        self._attr_name = f"{device.get_property_value("product_name") or device.name} Tank Full"
        self._attr_unique_id = f"nomaiq_dehumidifer_tank_full{device.serial_number}"
        self._attr_has_entity_name = device.get_property_value("product_name")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.serial_number)},
            name=device.name,
        )

    @property
    def is_on(self) -> bool:
        data: list[ayla_iot_unofficial.device.Device] = self.coordinator.data
        device: ayla_iot_unofficial.device.Device | None = next(
            (d for d in data if d.serial_number == self._device.serial_number),
            None,
        )
        return device and device.get_property_value("water_bucket_full")


class NomaIQFilterAlertSensor(BinarySensorEntity):
    def __init__(
        self,
        coordinator: NomaIQDataUpdateCoordinator,
        device: ayla_iot_unofficial.device.Device,
    ) -> None:
        self.coordinator = coordinator
        self._device = device
        self._attr_name = f"{device.get_property_value("product_name") or device.name} Filter Alert"
        self._attr_unique_id = f"nomaiq_dehumidifer_filter_alert{device.serial_number}"
        self._attr_has_entity_name = device.get_property_value("product_name")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.serial_number)},
            name=device.name,
        )

    @property
    def is_on(self) -> bool:
        data: list[ayla_iot_unofficial.device.Device] = self.coordinator.data
        device: ayla_iot_unofficial.device.Device | None = next(
            (d for d in data if d.serial_number == self._device.serial_number),
            None,
        )
        return device and device.get_property_value("filter_clean_alarm")
