"""Config flow for School Meal Menu."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .api import TitanSchoolsClient
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
    RECIPE_CATEGORY_OPTIONS,
    SIZE_OPTIONS,
    TODAY_CLASS_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Validate credentials by performing one menu fetch."""
    client = TitanSchoolsClient(
        building_id=data[CONF_BUILDING_ID],
        district_id=data[CONF_DISTRICT_ID],
        number_of_days_to_display=DEFAULT_NUMBER_OF_DAYS,
        recipe_categories_to_include=list(DEFAULT_RECIPE_CATEGORIES),
        display_current_week=DEFAULT_DISPLAY_CURRENT_WEEK,
        week_starts_on_monday=DEFAULT_WEEK_STARTS_ON_MONDAY,
        debug=False,
    )
    session = async_get_clientsession(hass)
    await client.fetch_menu(session)
    return {"title": data.get(CONF_NAME, DEFAULT_NAME)}


def _options_schema_defaults(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_NUMBER_OF_DAYS_DISPLAY,
                default=defaults.get(CONF_NUMBER_OF_DAYS_DISPLAY, DEFAULT_NUMBER_OF_DAYS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=14, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(
                CONF_UPDATE_INTERVAL_SECONDS,
                default=defaults.get(CONF_UPDATE_INTERVAL_SECONDS, DEFAULT_UPDATE_INTERVAL_SECONDS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=60,
                    max=86400,
                    step=60,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_RETRY_DELAY_SECONDS,
                default=defaults.get(CONF_RETRY_DELAY_SECONDS, DEFAULT_RETRY_DELAY_SECONDS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=5,
                    max=600,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_RECIPE_CATEGORIES,
                default=defaults.get(CONF_RECIPE_CATEGORIES, DEFAULT_RECIPE_CATEGORIES),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": c, "label": c} for c in RECIPE_CATEGORY_OPTIONS
                    ],
                    multiple=True,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_DISPLAY_CURRENT_WEEK,
                default=defaults.get(CONF_DISPLAY_CURRENT_WEEK, DEFAULT_DISPLAY_CURRENT_WEEK),
            ): bool,
            vol.Required(
                CONF_WEEK_STARTS_ON_MONDAY,
                default=defaults.get(CONF_WEEK_STARTS_ON_MONDAY, DEFAULT_WEEK_STARTS_ON_MONDAY),
            ): bool,
            vol.Required(
                CONF_HIDE_EMPTY_DAYS,
                default=defaults.get(CONF_HIDE_EMPTY_DAYS, DEFAULT_HIDE_EMPTY_DAYS),
            ): bool,
            vol.Required(
                CONF_HIDE_EMPTY_MEALS,
                default=defaults.get(CONF_HIDE_EMPTY_MEALS, DEFAULT_HIDE_EMPTY_MEALS),
            ): bool,
            vol.Required(
                CONF_SIZE,
                default=defaults.get(CONF_SIZE, DEFAULT_SIZE),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[{"value": s, "label": s} for s in SIZE_OPTIONS],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_TODAY_CLASS,
                default=defaults.get(CONF_TODAY_CLASS, DEFAULT_TODAY_CLASS),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[{"value": s, "label": s} for s in TODAY_CLASS_OPTIONS],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_DEBUG,
                default=defaults.get(CONF_DEBUG, DEFAULT_DEBUG),
            ): bool,
        }
    )


class SchoolMealMenuOptionsFlow(config_entries.OptionsFlow):
    """Options flow."""

    def _defaults(self) -> dict[str, Any]:
        opt = dict(self.config_entry.options)
        return {
            CONF_NUMBER_OF_DAYS_DISPLAY: int(
                opt.get(CONF_NUMBER_OF_DAYS_DISPLAY, DEFAULT_NUMBER_OF_DAYS)
            ),
            CONF_UPDATE_INTERVAL_SECONDS: int(
                opt.get(CONF_UPDATE_INTERVAL_SECONDS, DEFAULT_UPDATE_INTERVAL_SECONDS)
            ),
            CONF_RETRY_DELAY_SECONDS: int(
                opt.get(CONF_RETRY_DELAY_SECONDS, DEFAULT_RETRY_DELAY_SECONDS)
            ),
            CONF_RECIPE_CATEGORIES: list(
                opt.get(CONF_RECIPE_CATEGORIES, DEFAULT_RECIPE_CATEGORIES)
            ),
            CONF_DISPLAY_CURRENT_WEEK: bool(
                opt.get(CONF_DISPLAY_CURRENT_WEEK, DEFAULT_DISPLAY_CURRENT_WEEK)
            ),
            CONF_WEEK_STARTS_ON_MONDAY: bool(
                opt.get(CONF_WEEK_STARTS_ON_MONDAY, DEFAULT_WEEK_STARTS_ON_MONDAY)
            ),
            CONF_HIDE_EMPTY_DAYS: bool(opt.get(CONF_HIDE_EMPTY_DAYS, DEFAULT_HIDE_EMPTY_DAYS)),
            CONF_HIDE_EMPTY_MEALS: bool(
                opt.get(CONF_HIDE_EMPTY_MEALS, DEFAULT_HIDE_EMPTY_MEALS)
            ),
            CONF_SIZE: opt.get(CONF_SIZE, DEFAULT_SIZE),
            CONF_TODAY_CLASS: opt.get(CONF_TODAY_CLASS, DEFAULT_TODAY_CLASS),
            CONF_DEBUG: bool(opt.get(CONF_DEBUG, DEFAULT_DEBUG)),
        }

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        defaults = self._defaults()
        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema_defaults(defaults),
        )


class SchoolMealMenuConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SchoolMealMenuOptionsFlow:
        """Options flow."""
        return SchoolMealMenuOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except aiohttp.ClientError:
                _LOGGER.exception("Connection error")
                errors["base"] = "cannot_connect"
            except TimeoutError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                uid = (
                    f"{user_input[CONF_BUILDING_ID].strip()}_{user_input[CONF_DISTRICT_ID].strip()}"
                )
                await self.async_set_unique_id(uid)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_BUILDING_ID: user_input[CONF_BUILDING_ID].strip(),
                        CONF_DISTRICT_ID: user_input[CONF_DISTRICT_ID].strip(),
                        CONF_NAME: user_input.get(CONF_NAME, DEFAULT_NAME).strip()
                        or DEFAULT_NAME,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_BUILDING_ID): str,
                vol.Required(CONF_DISTRICT_ID): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

