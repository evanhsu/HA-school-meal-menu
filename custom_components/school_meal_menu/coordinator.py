"""Data update coordinator for School Meal Menu."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Callable

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TitanSchoolsClient, filter_hide_empty_days
from .const import (
    CONF_BUILDING_ID,
    CONF_DEBUG,
    CONF_DISPLAY_CURRENT_WEEK,
    CONF_DISTRICT_ID,
    CONF_HIDE_EMPTY_DAYS,
    CONF_HIDE_EMPTY_MEALS,
    CONF_NUMBER_OF_DAYS_DISPLAY,
    CONF_RECIPE_CATEGORIES,
    CONF_RETRY_DELAY_SECONDS,
    CONF_SIZE,
    CONF_TODAY_CLASS,
    CONF_UPDATE_INTERVAL_SECONDS,
    CONF_WEEK_STARTS_ON_MONDAY,
    DEFAULT_DEBUG,
    DEFAULT_DISPLAY_CURRENT_WEEK,
    DEFAULT_HIDE_EMPTY_DAYS,
    DEFAULT_HIDE_EMPTY_MEALS,
    DEFAULT_NAME,
    DEFAULT_NUMBER_OF_DAYS,
    DEFAULT_RECIPE_CATEGORIES,
    DEFAULT_RETRY_DELAY_SECONDS,
    DEFAULT_SIZE,
    DEFAULT_TODAY_CLASS,
    DEFAULT_UPDATE_INTERVAL_SECONDS,
    DEFAULT_WEEK_STARTS_ON_MONDAY,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def build_client(entry: ConfigEntry) -> TitanSchoolsClient:
    """Create API client from config entry data + options."""
    data = entry.data
    opt = entry.options
    recipe = list(opt.get(CONF_RECIPE_CATEGORIES, DEFAULT_RECIPE_CATEGORIES))
    return TitanSchoolsClient(
        building_id=data[CONF_BUILDING_ID],
        district_id=data[CONF_DISTRICT_ID],
        number_of_days_to_display=int(opt.get(CONF_NUMBER_OF_DAYS_DISPLAY, DEFAULT_NUMBER_OF_DAYS)),
        recipe_categories_to_include=recipe,
        display_current_week=bool(opt.get(CONF_DISPLAY_CURRENT_WEEK, DEFAULT_DISPLAY_CURRENT_WEEK)),
        week_starts_on_monday=bool(
            opt.get(CONF_WEEK_STARTS_ON_MONDAY, DEFAULT_WEEK_STARTS_ON_MONDAY)
        ),
        debug=bool(opt.get(CONF_DEBUG, DEFAULT_DEBUG)),
    )


def merged_options(entry: ConfigEntry) -> dict[str, Any]:
    """Defaults + options for sensor attributes."""
    opt = entry.options or {}
    return {
        CONF_NUMBER_OF_DAYS_DISPLAY: int(opt.get(CONF_NUMBER_OF_DAYS_DISPLAY, DEFAULT_NUMBER_OF_DAYS)),
        CONF_UPDATE_INTERVAL_SECONDS: int(
            opt.get(CONF_UPDATE_INTERVAL_SECONDS, DEFAULT_UPDATE_INTERVAL_SECONDS)
        ),
        CONF_RETRY_DELAY_SECONDS: int(opt.get(CONF_RETRY_DELAY_SECONDS, DEFAULT_RETRY_DELAY_SECONDS)),
        CONF_RECIPE_CATEGORIES: list(opt.get(CONF_RECIPE_CATEGORIES, DEFAULT_RECIPE_CATEGORIES)),
        CONF_DISPLAY_CURRENT_WEEK: bool(opt.get(CONF_DISPLAY_CURRENT_WEEK, DEFAULT_DISPLAY_CURRENT_WEEK)),
        CONF_WEEK_STARTS_ON_MONDAY: bool(
            opt.get(CONF_WEEK_STARTS_ON_MONDAY, DEFAULT_WEEK_STARTS_ON_MONDAY)
        ),
        CONF_HIDE_EMPTY_DAYS: bool(opt.get(CONF_HIDE_EMPTY_DAYS, DEFAULT_HIDE_EMPTY_DAYS)),
        CONF_HIDE_EMPTY_MEALS: bool(opt.get(CONF_HIDE_EMPTY_MEALS, DEFAULT_HIDE_EMPTY_MEALS)),
        CONF_DEBUG: bool(opt.get(CONF_DEBUG, DEFAULT_DEBUG)),
        CONF_SIZE: opt.get(CONF_SIZE, DEFAULT_SIZE),
        CONF_TODAY_CLASS: opt.get(CONF_TODAY_CLASS, DEFAULT_TODAY_CLASS),
    }


class SchoolMealMenuCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch normalized menus for the configured school."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.config_entry = entry
        self._client = build_client(entry)
        opt = merged_options(entry)
        self._hide_empty_days = opt[CONF_HIDE_EMPTY_DAYS]
        self._retry_delay = int(opt.get(CONF_RETRY_DELAY_SECONDS, DEFAULT_RETRY_DELAY_SECONDS))
        self._retry_cancel: Callable[[], None] | None = None

        update_interval = timedelta(seconds=opt[CONF_UPDATE_INTERVAL_SECONDS])

        title = entry.title or DEFAULT_NAME
        super().__init__(
            hass,
            _LOGGER,
            name=title,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        if self._retry_cancel is not None:
            cancel = self._retry_cancel
            self._retry_cancel = None
            cancel()

        session = async_get_clientsession(self.hass)
        try:
            menus = await self._client.fetch_menu(session)
        except aiohttp.ClientError as err:
            self._schedule_retry()
            raise UpdateFailed(f"Unable to fetch menu: {err}") from err
        except TimeoutError as err:
            self._schedule_retry()
            raise UpdateFailed("Timeout while fetching menu") from err
        except Exception as err:
            self._schedule_retry()
            raise UpdateFailed(f"Unexpected error: {err}") from err

        menus = filter_hide_empty_days(menus, hide_empty_days=self._hide_empty_days)
        opt = merged_options(self.config_entry)
        return {
            "menus": menus,
            "options": opt,
        }

    def _schedule_retry(self) -> None:
        """Single delayed refresh (mirrors MMM retryDelayMs)."""
        if self._retry_cancel is not None:
            return

        async def _retry(_now: datetime | None) -> None:
            self._retry_cancel = None
            await self.async_request_refresh()

        self._retry_cancel = async_call_later(self.hass, self._retry_delay, _retry)
