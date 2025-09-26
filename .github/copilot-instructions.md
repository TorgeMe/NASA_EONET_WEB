# Copilot Instructions for NASA_EONET_WEB

## Project Overview
This is a Python-based web application for interacting with NASA's EONET (Earth Observatory Natural Event Tracker) API. The project fetches, processes, and displays natural event data using Flask and Jinja2 templates.

## Architecture & Key Components
- `NASA_EONET.py`: Main application logic. Handles API requests, data processing, and serves web routes.
- `templates/`: Contains HTML templates for rendering data and user interfaces (`index.html`, `data.html`, `preferences.html`, `shutdown.html`).
- `config.ini`: Stores configuration settings (API keys, preferences, etc.).
- `nasa_events.json`: Cached or processed event data from NASA EONET API.

## Developer Workflows
- **Run the app:**
	```powershell
	python NASA_EONET.py
	```
- **Debugging:**
	Use print statements or logging in `NASA_EONET.py`. Flask's built-in debugger is available when running in development mode.
- **Configuration:**
	Update `config.ini` for API keys or user preferences. The app reads this file at startup.
- **Templates:**
	Edit HTML files in `templates/` to change UI or data presentation. Data is passed via Flask's `render_template`.
- **Data updates:**
	Event data is fetched from NASA EONET API and may be cached in `nasa_events.json` for performance.

## Patterns & Conventions
- All routes and logic are centralized in `NASA_EONET.py`.
- Jinja2 is used for template rendering; pass context variables from route handlers.
- Cached data is stored in JSON format (`nasa_events.json`).
- Configuration is managed via `config.ini` (use `configparser` in Python).
- No custom build or test scripts detected; manual testing via browser recommended.

## Integration Points
- **External API:** NASA EONET API (see `NASA_EONET.py` for endpoint usage).
- **Templates:** Flask/Jinja2 integration for dynamic HTML rendering.
- **Config:** Reads from `config.ini` for runtime settings.

## Example: Adding a New Event Type
1. Update API logic in `NASA_EONET.py` to fetch/process the new event type.
2. Modify `data.html` or other templates to display the new data.
3. Adjust `config.ini` if new settings are required.

## Key Files
- `NASA_EONET.py`: Main logic, API integration, route definitions.
- `templates/`: UI templates.
- `config.ini`: Configuration.
- `nasa_events.json`: Cached event data.

---
For questions or unclear patterns, review `NASA_EONET.py` and template files for implementation details. If conventions or workflows are missing, ask the user for clarification.
