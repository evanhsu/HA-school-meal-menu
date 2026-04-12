"""Constants for the School Meal Menu integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "school_meal_menu"

CONF_BUILDING_ID: Final = "building_id"
CONF_DISTRICT_ID: Final = "district_id"
CONF_NAME: Final = "name"

CONF_NUMBER_OF_DAYS_DISPLAY: Final = "number_of_days_display"
CONF_UPDATE_INTERVAL_SECONDS: Final = "update_interval_seconds"
CONF_RETRY_DELAY_SECONDS: Final = "retry_delay_seconds"
CONF_RECIPE_CATEGORIES: Final = "recipe_categories_to_include"
CONF_DISPLAY_CURRENT_WEEK: Final = "display_current_week"
CONF_WEEK_STARTS_ON_MONDAY: Final = "week_starts_on_monday"
CONF_HIDE_EMPTY_DAYS: Final = "hide_empty_days"
CONF_HIDE_EMPTY_MEALS: Final = "hide_empty_meals"
CONF_DEBUG: Final = "debug"
CONF_SIZE: Final = "size"
CONF_TODAY_CLASS: Final = "today_class"

DEFAULT_NAME: Final = "School meal menu"

# Mirrors MMM-TitanSchoolMealMenu defaults
DEFAULT_NUMBER_OF_DAYS: Final = 3
DEFAULT_UPDATE_INTERVAL_SECONDS: Final = 60 * 60  # updateIntervalMs
DEFAULT_RETRY_DELAY_SECONDS: Final = 20  # retryDelayMs
DEFAULT_DISPLAY_CURRENT_WEEK: Final = False
DEFAULT_WEEK_STARTS_ON_MONDAY: Final = False
DEFAULT_HIDE_EMPTY_DAYS: Final = False
DEFAULT_HIDE_EMPTY_MEALS: Final = False
DEFAULT_DEBUG: Final = False
DEFAULT_SIZE: Final = "medium"
DEFAULT_TODAY_CLASS: Final = "large"

DEFAULT_RECIPE_CATEGORIES: Final[list[str]] = ["Entrees", "Grain"]

RECIPE_CATEGORY_OPTIONS: Final[list[str]] = [
    "Main Entree",
    "Entrees",
    "Grain",
    "Fruit",
    "Vegetable",
    "Milk",
    "Condiment",
    "Extra",
]

SIZE_OPTIONS: Final[list[str]] = ["small", "medium", "large"]
TODAY_CLASS_OPTIONS: Final[list[str]] = ["none", "small", "medium", "large"]

MENU_API_URL: Final = "https://api.linqconnect.com/api/FamilyMenu"
