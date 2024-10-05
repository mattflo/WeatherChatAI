import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import pytz
import requests
import structlog
from langchain.tools import tool

from weather_chat_ai.nominatim import get_lat_lon

logger = structlog.get_logger(__name__)


def get_tz_and_forecast_url(lat: str, lon: str) -> Tuple[str, str]:
    resp = requests.get(f"https://api.weather.gov/points/{lat},{lon}")
    gridpoints = json.loads(resp.content)
    tz = gridpoints["properties"]["timeZone"]
    forecast_url = gridpoints["properties"]["forecast"]
    return tz, forecast_url


def fetch_nws_forecast(
    forecast_url: str,
) -> Dict[str, Any]:
    """Get the weather forecast from the NWS API."""
    res = requests.get(forecast_url)
    return json.loads(res.content)


DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def normalize_forecast_days(
    forecast: List[str],
    ts: datetime,
) -> List[str]:
    """Normalize the labels for the days and nights of the forecast to eliminate holiday names and add dates."""
    current_day_of_week_index = ts.weekday()
    for index, row in enumerate(forecast[2::2]):
        ts += timedelta(days=1)
        date = ts.strftime("%B %d")
        day_label = DAYS[(current_day_of_week_index + 1 + index) % 7]
        forecast[index * 2 + 2] = f"{day_label}, {date}: {row.split(': ', 1)[1]}"
        next_row = forecast[index * 2 + 3]
        forecast[index * 2 + 3] = (
            f"{day_label} Night, {date}: {next_row.split(': ', 1)[1]}"
        )
    return forecast


def get_current_day_and_time(
    ts: datetime,
    location: str,
) -> str:
    """Build the string to present the llm with the current day of week, date, and time in the given location."""
    day = DAYS[ts.weekday()]
    prefix = "The current day and local time in"
    return f"{prefix} {location} is {day}, {ts.strftime('%B %d, %I:%M %p')}"


def extract_forecast_lines(
    forecast: Dict[str, Any],
) -> List[str]:
    """Extract the forecast lines from the NWS API response."""
    periods = forecast["properties"]["periods"]
    logger.info(f"Found {len(periods)} forecast periods.")
    return [f"{p['name']}: {p['detailedForecast']}" for p in periods]


def get_formatted_forecast(
    tz_name: str,
    location: str,
    forecast_lines: List[str],
) -> str:
    """Finalize the format of the forecast."""
    ts = datetime.now(tz=pytz.timezone(tz_name))
    forecasts = normalize_forecast_days(forecast_lines, ts)
    prefix = get_current_day_and_time(ts, location)
    logger.info(f"Prepared {len(forecasts)} forecast rows.")
    return "\n".join([prefix, "", "Forecast:"] + forecasts)


def get_weather(location: str, lat: str, lon: str) -> str:
    tz, forecast_url = get_tz_and_forecast_url(lat, lon)
    forecast = fetch_nws_forecast(forecast_url)
    forecast_lines = extract_forecast_lines(forecast)
    formatted_forecast = get_formatted_forecast(tz, location, forecast_lines)
    return formatted_forecast


@tool
def get_weather_forecast(search: str):
    """Get the weather forecast for a city"""
    lat, lon = get_lat_lon(search)
    return get_weather(search, lat, lon)
