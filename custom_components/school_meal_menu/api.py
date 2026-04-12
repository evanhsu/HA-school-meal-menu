"""LINQ Connect / Titan FamilyMenu API client (logic ported from MMM-TitanSchoolMealMenu)."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

import aiohttp

from .const import MENU_API_URL

_LOGGER = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"
)


def format_date(d: date) -> str:
    """Format as m-d-Y to match the upstream API expectations."""
    return f"{d.month}-{d.day}-{d.year}"


def upcoming_relative_dates(number_of_days: int) -> list[dict[str, str]]:
    """Relative day labels: Today, Tomorrow, then weekday names (JS getDay order)."""
    # Mirrors MMM `upcomingRelativeDates` / Date#getDay() indexing (Sun=0 .. Sat=6).
    dow_labels = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    out: list[dict[str, str]] = []
    today = date.today()
    for day_offset in range(number_of_days):
        adjusted = today + timedelta(days=day_offset)
        if day_offset == 0:
            label = "Today"
        elif day_offset == 1:
            label = "Tomorrow"
        else:
            js_dow = (adjusted.weekday() + 1) % 7
            label = dow_labels[js_dow]
        out.append({"date": format_date(adjusted), "label": label})
    return out


def get_first_day_of_week(today: date, *, week_starts_on_monday: bool) -> date:
    """Match node_helper.getFirstDayOfWeek."""
    wd = today.weekday()  # Monday=0 .. Sunday=6
    if week_starts_on_monday:
        days_back = wd
    else:
        # week starts Sunday: Python Monday=0 -> Sunday is 6
        days_back = (wd + 1) % 7
    return today - timedelta(days=days_back)


def parse_flexible_date(value: str) -> date:
    """Parse API day strings (e.g. 1/18/2023) and our m-d-Y strings."""
    raw = value.strip().replace("-", "/")
    parts = raw.split("/")
    if len(parts) != 3:
        msg = f"Unrecognized date: {value!r}"
        raise ValueError(msg)
    month, day, year = (int(parts[0]), int(parts[1]), int(parts[2]))
    return date(year, month, day)


def dates_equal(a: str, b: str) -> bool:
    """Compare two date strings by calendar day."""
    return parse_flexible_date(a) == parse_flexible_date(b)


class TitanSchoolsClient:
    """Fetch and normalize FamilyMenu payloads."""

    def __init__(
        self,
        *,
        building_id: str,
        district_id: str,
        number_of_days_to_display: int,
        recipe_categories_to_include: list[str],
        display_current_week: bool,
        week_starts_on_monday: bool,
        debug: bool = False,
    ) -> None:
        self._building_id = building_id
        self._district_id = district_id
        self._number_of_days = number_of_days_to_display
        self._recipe_categories = recipe_categories_to_include
        self._display_current_week = display_current_week
        self._week_starts_on_monday = week_starts_on_monday
        self._debug = debug

    def extract_menus_by_date(self, api_response: dict[str, Any]) -> list[list[dict[str, Any]]]:
        if "FamilyMenuSessions" not in api_response:
            return []

        menus: list[list[dict[str, Any]]] = []
        for menu_session in api_response["FamilyMenuSessions"]:
            serving = str(menu_session.get("ServingSession", ""))
            breakfast_or_lunch = "breakfast" if "breakfast" in serving.lower() else "lunch"

            menu_plans = menu_session.get("MenuPlans") or []
            if not menu_plans:
                continue
            days = (menu_plans[0] or {}).get("Days") or []
            if not days:
                continue

            menus_by_date: list[dict[str, Any]] = []
            for menu_for_this_date in days:
                menu_meals = menu_for_this_date.get("MenuMeals") or []
                first_meal = menu_meals[0] if menu_meals else {}
                first_rc = (first_meal.get("RecipeCategories") or [])
                first_rc0 = first_rc[0] if first_rc else {}
                first_recipes = first_rc0.get("Recipes") or []
                if not first_recipes:
                    continue

                recipes_to_log: dict[str, list[str]] = {"all": [], "filtered_out": []}

                recipe_categories_flat: list[dict[str, Any]] = []
                for meal_line in menu_meals:
                    for recipe_category in meal_line.get("RecipeCategories") or []:
                        name = recipe_category.get("CategoryName")
                        if name and name not in recipes_to_log["all"]:
                            recipes_to_log["all"].append(name)

                        include = (
                            len(self._recipe_categories) == 0
                            or name in self._recipe_categories
                        )
                        if include:
                            recipe_categories_flat.append(recipe_category)
                        elif name and name not in recipes_to_log["filtered_out"]:
                            recipes_to_log["filtered_out"].append(name)

                if self._debug:
                    _LOGGER.debug(
                        "Categories for %s %s: all=%s filtered=%s",
                        breakfast_or_lunch,
                        menu_for_this_date.get("Date"),
                        recipes_to_log["all"],
                        recipes_to_log["filtered_out"],
                    )

                menu_text = ", ".join(
                    " or ".join(
                        str(r.get("RecipeName", ""))
                        for r in (cat.get("Recipes") or [])
                        if r.get("RecipeName")
                    )
                    for cat in recipe_categories_flat
                    if cat.get("Recipes")
                )

                menus_by_date.append(
                    {
                        "date": menu_for_this_date.get("Date"),
                        "breakfastOrLunch": breakfast_or_lunch,
                        "menu": menu_text,
                    }
                )

            menus.append(menus_by_date)

        return menus

    def process_data(self, data: dict[str, Any]) -> list[dict[str, Any | None]]:
        menus = self.extract_menus_by_date(data)

        days_out: list[dict[str, Any | None]] = []
        for day in upcoming_relative_dates(self._number_of_days):
            meal_accum: dict[str, str] = {}
            for session_days in menus:
                matching = [
                    m
                    for m in session_days
                    if m.get("date")
                    and isinstance(m["date"], str)
                    and dates_equal(m["date"], day["date"])
                ]
                if not matching:
                    continue
                entry = matching[0]
                key = str(entry.get("breakfastOrLunch", "lunch")).lower()
                meal_accum[key] = str(entry.get("menu", ""))

            days_out.append(
                {
                    "date": day["date"],
                    "label": day["label"],
                    "breakfast": meal_accum.get("breakfast"),
                    "lunch": meal_accum.get("lunch"),
                }
            )
        return days_out

    def compute_date_range(self) -> tuple[date, date]:
        """Start/end dates for the API request (mirrors MMM node_helper.fetchData)."""
        today = date.today()
        if self._display_current_week:
            start = get_first_day_of_week(today, week_starts_on_monday=self._week_starts_on_monday)
        else:
            start = today

        end = date.fromordinal(start.toordinal() + self._number_of_days)
        return start, end

    async def fetch_menu(
        self, session: aiohttp.ClientSession
    ) -> list[dict[str, Any | None]]:
        start_d, end_d = self.compute_date_range()
        params = {
            "buildingId": self._building_id,
            "districtId": self._district_id,
            "startDate": format_date(start_d),
            "endDate": format_date(end_d),
        }

        async with session.get(
            MENU_API_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            response.raise_for_status()
            payload = await response.json()

        return self.process_data(payload)


def filter_hide_empty_days(
    menus: list[dict[str, Any | None]], *, hide_empty_days: bool
) -> list[dict[str, Any | None]]:
    """MMM hideEmptyDays: omit days with no breakfast and no lunch."""
    if not hide_empty_days:
        return list(menus)
    return [d for d in menus if d.get("breakfast") or d.get("lunch")]
