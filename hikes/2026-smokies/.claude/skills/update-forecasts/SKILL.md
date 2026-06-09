---
name: update-forecasts
description: Fetch the latest 7-day NWS weather forecast for each of the 9 shelter/endpoint locations along the 2026 Smokies AT traverse and write weather-data.json. Run when the user wants to refresh the data on the /weather page.
---

# Update forecasts

When the user invokes this skill, run the bundled Python script from the project root and report the result.

## Steps

1. Run the script:
   ```
   python3 .claude/skills/update-forecasts/update.py
   ```
2. The script writes `weather-data.json` to the project root. It contains the `updated` timestamp, the 9 locations, each location's forecast (per-day high/low/short/detailed/precip/wind), and any per-location errors.
3. Report a one-line summary: how many locations got data, how many failed, and the updated timestamp. If any location failed, list its name and the error.
4. Do **not** commit the change automatically — leave the file unstaged so the user can review and commit it themselves.

## Notes

- The script uses the National Weather Service public API (api.weather.gov). No API key, but it requires a User-Agent header (already set in the script).
- NWS sometimes rate-limits or returns transient 5xx errors; the script retries each call up to 3 times with backoff.
- If many locations fail, suggest waiting a minute and re-running — usually a transient NWS issue.
- The script runs entirely from the project root cwd; it does not need any flags.
