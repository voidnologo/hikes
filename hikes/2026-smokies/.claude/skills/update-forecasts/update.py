#!/usr/bin/env python3
"""Fetch NWS forecasts for each shelter on the 2026 Smokies AT traverse.

Writes ./weather-data.json relative to the current working directory.
Expected to be invoked from the repo root.

NWS API: api.weather.gov (free, no API key, requires User-Agent identifying contact).
Two-step lookup per location:
  1. /points/{lat},{lon} -> metadata + forecast URL
  2. forecast URL -> 14 alternating day/night periods (~7 days)
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LOCATIONS = [
    {"day": 0, "name": "Davenport Gap",      "elevation_ft": 2600, "lat": 35.7536, "lon": -83.1086, "trip_date": "2026-05-18"},
    {"day": 1, "name": "Cosby Knob",         "elevation_ft": 4700, "lat": 35.7331, "lon": -83.1933, "trip_date": "2026-05-19"},
    {"day": 2, "name": "Tricorner Knob",     "elevation_ft": 5920, "lat": 35.6664, "lon": -83.2492, "trip_date": "2026-05-20"},
    {"day": 3, "name": "Pecks Corner",       "elevation_ft": 5280, "lat": 35.6411, "lon": -83.3158, "trip_date": "2026-05-21"},
    {"day": 4, "name": "Icewater Spring",    "elevation_ft": 5920, "lat": 35.6336, "lon": -83.3725, "trip_date": "2026-05-22"},
    {"day": 5, "name": "Double Spring",      "elevation_ft": 5505, "lat": 35.5589, "lon": -83.5083, "trip_date": "2026-05-23"},
    {"day": 6, "name": "Derrick Knob",       "elevation_ft": 4880, "lat": 35.5256, "lon": -83.6203, "trip_date": "2026-05-24"},
    {"day": 7, "name": "Russell Field",      "elevation_ft": 4360, "lat": 35.5443, "lon": -83.7042, "trip_date": "2026-05-25"},
    {"day": 8, "name": "Fontana Dam",        "elevation_ft": 1750, "lat": 35.4520, "lon": -83.8081, "trip_date": "2026-05-26"},
]

# NWS requires a User-Agent identifying the app + contact. Format per their docs.
USER_AGENT = "smokies-2026-hike-site (caleb@telegraph.io)"

OUT_PATH = Path("weather-data.json")


def fetch_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/geo+json"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fetch_with_retry(url: str, attempts: int = 3) -> dict:
    last_err = None
    for i in range(attempts):
        try:
            return fetch_json(url)
        except (HTTPError, URLError) as e:
            last_err = e
            time.sleep(1.5 * (i + 1))
    raise last_err  # type: ignore[misc]


def group_into_days(periods: list) -> list:
    """Collapse alternating day/night periods into per-date entries with high+low."""
    by_date: dict[str, dict] = {}
    for p in periods:
        date = p["startTime"][:10]
        is_day = p["isDaytime"]
        precip = (p.get("probabilityOfPrecipitation") or {}).get("value")
        d = by_date.setdefault(date, {
            "date": date,
            "name": p["name"],
            "high_f": None,
            "low_f": None,
            "short": None,
            "detailed": None,
            "precip_pct": None,
            "wind": None,
            "icon": None,
        })
        if is_day:
            d["high_f"] = p["temperature"]
            d["short"] = p["shortForecast"]
            d["detailed"] = p["detailedForecast"]
            d["wind"] = p.get("windSpeed")
            d["icon"] = p.get("icon")
            d["name"] = p["name"]
            if precip is not None:
                d["precip_pct"] = precip
        else:
            d["low_f"] = p["temperature"]
            # If we got the night period first (forecast issued in the evening),
            # use its description until the day period overwrites it.
            if d["short"] is None:
                d["short"] = p["shortForecast"]
                d["detailed"] = p["detailedForecast"]
                d["wind"] = p.get("windSpeed")
                d["icon"] = p.get("icon")
            if d["precip_pct"] is None and precip is not None:
                d["precip_pct"] = precip
    return sorted(by_date.values(), key=lambda d: d["date"])


def fetch_location(loc: dict) -> dict:
    points = fetch_with_retry(f"https://api.weather.gov/points/{loc['lat']},{loc['lon']}")
    forecast_url = points["properties"]["forecast"]
    grid_id = points["properties"].get("gridId")
    grid_x = points["properties"].get("gridX")
    grid_y = points["properties"].get("gridY")
    time.sleep(0.4)
    forecast = fetch_with_retry(forecast_url)
    periods = forecast["properties"]["periods"]
    return {
        **loc,
        "nws_grid": f"{grid_id}/{grid_x},{grid_y}" if grid_id else None,
        "forecast": group_into_days(periods),
    }


def main() -> int:
    out = {
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "api.weather.gov",
        "locations": [],
        "errors": [],
    }

    for loc in LOCATIONS:
        print(f"  fetching {loc['name']} ({loc['lat']}, {loc['lon']})...", file=sys.stderr)
        try:
            out["locations"].append(fetch_location(loc))
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr)
            out["errors"].append({"location": loc["name"], "error": str(e)})
            out["locations"].append({**loc, "forecast": []})
        time.sleep(0.4)

    OUT_PATH.write_text(json.dumps(out, indent=2))
    print(f"Wrote {OUT_PATH.resolve()} ({len(out['locations'])} locations, {len(out['errors'])} errors)", file=sys.stderr)
    return 1 if out["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
