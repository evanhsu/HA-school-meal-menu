# Home Assistant School Meal Menu

Custom integration for [LINQ Connect](https://api.linqconnect.com/api/FamilyMenu) (`building_id` / `district_id`), with a thin Lovelace card that only reads the sensor entity.

## Install the backend integration with HACS

1. In HACS, click the 3 dots in the upper right and select "Custom Repositories"
2. Paste the Clone link for this repo (`git@github.com:evanhsu/HA-school-meal-menu.git`) and select "Integration" as the **Type**
3. After the Custom Repository is registered, search for "School meal menu" in the HACS search bar and "Download" the integration. You'll be prompted to restart Home Assistant after the integration is downloaded - go ahead and do it now.
4. On the **Integrations** screen, click the "+ Add Integration" button and search for "School Meal Menu". It will prompt you to name the sensor - you'll need to remember this name in step 7 below.
5. You can customize the options by clicking the Gear icon for this integration on the Integrations page

## Install the custom LoveLace card

1. Copy the javascript lovelace card from `/custom_components/school_meal_menu/www/school-meal-menu-card.js` into a new folder: `/www/community/school_meal_menu/school-meal-menu-card.js`
2. Add the custom lovelace card as a **Dashboard Resource** by navigating to the **Settings -> Dashboards**, then click the 3-dot menu in the upper right and select **Resources**
3. Enter the path `/hacsfiles/school-meal-menu/school-meal-menu-card.js`
4. Add a Custom Card to your dashboard that references the name that you assigned to the sensor:

```yaml
type: custom:school-meal-menu-card
entity: sensor.YOUR_MENU_SENSOR
```
