/**
 * Thin Lovelace card: renders `menus` (and display hints) from a School Meal Menu sensor.
 * All tunables live in the integration options — this card only needs `entity`.
 *
 * Resource URL (after integration loads): /school_meal_menu_card/school-meal-menu-card.js
 */

function createStyles() {
  const css = `
    :host { display: block; height: 100%; }
    .root {
      background: #000000;
      color: #e8e8e8;
      font-family: ui-sans-serif, system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 14px;
      line-height: 1.45;
      padding: 12px 16px;
      box-sizing: border-box;
      min-height: 120px;
    }
    .root.size-small { font-size: 12px; }
    .root.size-medium { font-size: 14px; }
    .root.size-large { font-size: 16px; }
    .day { margin-bottom: 14px; }
    .day:last-child { margin-bottom: 0; }
    .day-label {
      display: block;
      font-weight: 600;
      font-size: 1.05em;
      margin-bottom: 6px;
      letter-spacing: 0.02em;
    }
    .day.is-today .day-label { font-weight: 700; }
    .meal { margin: 4px 0 0 12px; }
    .meal-title { font-weight: 500; margin-right: 4px; }
    .meal-items {
      display: inline;
      text-transform: uppercase;
      font-weight: 400;
      letter-spacing: 0.03em;
    }
    .muted { opacity: 0.55; }
    .error { color: #ff8a80; padding: 8px 0; line-height: 1.4; }
    .loading { opacity: 0.65; }
  `;
  const sheet = new CSSStyleSheet();
  sheet.replaceSync(css);
  return sheet;
}

function renderMenu(rootEl, { menus, hideEmptyMeals, size, todayClass }) {
  rootEl.textContent = "";
  const sizeKey = ["small", "medium", "large"].includes(size) ? size : "medium";
  rootEl.className = `root size-${sizeKey}`;

  if (!Array.isArray(menus) || menus.length === 0) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.textContent = "No menu data.";
    rootEl.appendChild(empty);
    return;
  }

  const todayExtra =
    todayClass && todayClass !== "none" ? String(todayClass) : "";

  for (const dayMenu of menus) {
    const dayWrap = document.createElement("div");
    const isToday = dayMenu.label === "Today";
    dayWrap.className = ["day", isToday ? "is-today" : "", todayExtra && isToday ? todayExtra : ""]
      .filter(Boolean)
      .join(" ");

    const dayLabel = document.createElement("span");
    dayLabel.className = "day-label";
    dayLabel.textContent = dayMenu.label ?? "";
    dayWrap.appendChild(dayLabel);

    const appendMeal = (title, text) => {
      const has = Boolean(text);
      if (!has && hideEmptyMeals) {
        return;
      }
      const meal = document.createElement("div");
      meal.className = "meal";
      const titleEl = document.createElement("span");
      titleEl.className = "meal-title";
      titleEl.textContent = `${title}:`;
      const itemsEl = document.createElement("span");
      itemsEl.className = "meal-items";
      const display = has ? String(text) : "none";
      itemsEl.textContent = display;
      if (!has) itemsEl.classList.add("muted");
      meal.appendChild(titleEl);
      meal.appendChild(itemsEl);
      dayWrap.appendChild(meal);
    };

    appendMeal("Breakfast", dayMenu.breakfast);
    appendMeal("Lunch", dayMenu.lunch);

    rootEl.appendChild(dayWrap);
  }
}

class SchoolMealMenuCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [createStyles()];
    this._container = document.createElement("div");
    this._container.className = "root size-medium";
    this.shadowRoot.appendChild(this._container);
    this._config = null;
  }

  setConfig(config) {
    if (!config || !config.entity) {
      throw new Error("Specify entity (School Meal Menu sensor)");
    }
    this._config = { entity: config.entity };
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._config) {
      return;
    }
    this._render();
  }

  _render() {
    const entityId = this._config.entity;
    const state = this._hass.states[entityId];
    this._container.innerHTML = "";

    if (!state) {
      const err = document.createElement("div");
      err.className = "error";
      err.textContent = `Entity not found: ${entityId}`;
      this._container.appendChild(err);
      return;
    }

    if (state.state === "unavailable") {
      const err = document.createElement("div");
      err.className = "error";
      err.textContent = "Sensor unavailable.";
      this._container.appendChild(err);
      return;
    }

    const attrs = state.attributes || {};
    const menus = attrs.menus;
    if (!menus) {
      const err = document.createElement("div");
      err.className = "error";
      err.textContent = "Missing attributes.menus on sensor.";
      this._container.appendChild(err);
      return;
    }

    renderMenu(this._container, {
      menus,
      hideEmptyMeals: Boolean(attrs.hide_empty_meals),
      size: attrs.size || "medium",
      todayClass: attrs.today_class || "none",
    });
  }

  getCardSize() {
    return 5;
  }

  static getStubConfig() {
    return { entity: "" };
  }
}

customElements.define("school-meal-menu-card", SchoolMealMenuCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "school-meal-menu-card",
  name: "School Meal Menu",
  description: "School meal menu (reads School Meal Menu sensor)",
  preview: true,
});
