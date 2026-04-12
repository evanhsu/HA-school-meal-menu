"""Sensor exposing normalized school meal menus for Lovelace."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_BUILDING_ID,
    CONF_DEBUG,
    CONF_DISTRICT_ID,
    CONF_DISPLAY_CURRENT_WEEK,
    CONF_HIDE_EMPTY_DAYS,
    CONF_HIDE_EMPTY_MEALS,
    CONF_NAME,
    CONF_NUMBER_OF_DAYS_DISPLAY,
    CONF_RECIPE_CATEGORIES,
    CONF_RETRY_DELAY_SECONDS,
    CONF_SIZE,
    CONF_TODAY_CLASS,
    CONF_UPDATE_INTERVAL_SECONDS,
    CONF_WEEK_STARTS_ON_MONDAY,
    DEFAULT_NAME,
    DOMAIN,
)
from .coordinator import SchoolMealMenuCoordinator, merged_options


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor from a config entry."""
    coordinator: SchoolMealMenuCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SchoolMealMenuSensor(coordinator, entry)])


class SchoolMealMenuSensor(CoordinatorEntity[SchoolMealMenuCoordinator], SensorEntity):
    """Menu data for the thin Lovelace card."""

    _attr_should_poll = False

    def __init__(self, coordinator: SchoolMealMenuCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_meal_menu"
        self._attr_has_entity_name = False
        self._attr_name = (entry.data.get(CONF_NAME) or entry.title or DEFAULT_NAME).strip()
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=self._attr_name,
            manufacturer="LINQ Connect",
            model="FamilyMenu",
        )

    @property
    def native_value(self) -> int:
        """Number of day rows currently exposed."""
        menus = self.coordinator.data.get("menus") if self.coordinator.data else None
        if not menus:
            return 0
        return len(menus)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Payload consumed by the Lovelace card (entity-only config)."""
        data = self.coordinator.data or {}
        menus = data.get("menus") or []
        opt = merged_options(self._entry)
        return {
            "menus": menus,
            "building_id": self._entry.data.get(CONF_BUILDING_ID),
            "district_id": self._entry.data.get(CONF_DISTRICT_ID),
            CONF_NUMBER_OF_DAYS_DISPLAY: opt[CONF_NUMBER_OF_DAYS_DISPLAY],
            CONF_UPDATE_INTERVAL_SECONDS: opt[CONF_UPDATE_INTERVAL_SECONDS],
            CONF_RETRY_DELAY_SECONDS: opt[CONF_RETRY_DELAY_SECONDS],
            CONF_RECIPE_CATEGORIES: opt[CONF_RECIPE_CATEGORIES],
            CONF_DISPLAY_CURRENT_WEEK: opt[CONF_DISPLAY_CURRENT_WEEK],
            CONF_WEEK_STARTS_ON_MONDAY: opt[CONF_WEEK_STARTS_ON_MONDAY],
            CONF_HIDE_EMPTY_DAYS: opt[CONF_HIDE_EMPTY_DAYS],
            CONF_HIDE_EMPTY_MEALS: opt[CONF_HIDE_EMPTY_MEALS],
            CONF_SIZE: opt[CONF_SIZE],
            CONF_TODAY_CLASS: opt[CONF_TODAY_CLASS],
            CONF_DEBUG: opt[CONF_DEBUG],
        }
