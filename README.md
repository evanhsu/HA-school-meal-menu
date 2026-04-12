# Home Assistant School Meal Menu

Custom integration for [LINQ Connect](https://api.linqconnect.com/api/FamilyMenu) (`building_id` / `district_id`), with a thin Lovelace card that only reads the sensor entity.

## Install

1. Copy `custom_components/school_meal_menu/` into your Home Assistant `config/custom_components/` folder and restart HA.
2. **Settings → Devices & services → Add integration → School Meal Menu** and enter building ID, district ID, and a name.
3. Open **Configure** on the integration to set options (same ideas as `MMM-TitanSchoolMealMenu`: days shown, recipe categories, update interval, retry delay, week display, hide-empty flags, `size`, `today_class`, debug).
4. Add a **Dashboard resource** (JavaScript module): `/school_meal_menu_card/school-meal-menu-card.js`

   If that URL is unavailable, copy `custom_components/school_meal_menu/www/school-meal-menu-card.js` to `/config/www/` and use `/local/school-meal-menu-card.js` instead.

5. Add a card that only references the sensor:

```yaml
type: custom:school-meal-menu-card
entity: sensor.YOUR_MENU_SENSOR
```
