import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import pytz
import requests
import structlog
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain

from weather_chat_ai.nominatim import get_lat_lon

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


logger = structlog.get_logger(__name__)


class NWSChain(Chain):
    gridpoints_url: str = "https://api.weather.gov/points/"

    @property
    def input_keys(self) -> List[str]:
        return ["location"]

    @property
    def output_keys(self) -> List[str]:
        return ["forecast"]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        location = inputs["location"].strip("? \n")
        inputs["location"] = location

        try:
            logger.info(f"Retrieving forecast for: {location}")

            lat, lon = get_lat_lon(location)

            gridpoints = self.fetch_nws_gridpoints(lat, lon)
            tz_name, forecast_url = self.extract_tz_and_forecast_url(gridpoints)

            forecast_response = self.fetch_nws_forecast(forecast_url)
            forecast_lines = self.extract_forecast_lines(forecast_response)

            forecast = self.formatted_forecast(tz_name, location, forecast_lines)
            return {"forecast": forecast}
        except Exception as e:
            logger.error("An exception occurred: %s", e, exc_info=True)
            return {
                "forecast": f"Sorry, I'm having trouble finding the weather for {location}."
            }

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        location = inputs["location"].strip("? \n")
        inputs["location"] = location

        try:
            logger.info(f"Retrieving forecast for: {location}")

            lat, lon = get_lat_lon(location)

            gridpoints = await self.afetch_nws_gridpoints(lat, lon)
            tz_name, forecast_url = self.extract_tz_and_forecast_url(gridpoints)

            forecast_response = await self.afetch_nws_forecast(forecast_url)
            forecast_lines = self.extract_forecast_lines(forecast_response)

            forecast = self.formatted_forecast(tz_name, location, forecast_lines)
            return {"forecast": forecast}
        except Exception as e:
            logger.error("An exception occurred: %s", e, exc_info=True)
            return {
                "forecast": f"Sorry, I'm having trouble finding the weather for {location}."
            }

    def formatted_forecast(
        self,
        tz_name: str,
        location: str,
        forecast_lines: List[str],
    ) -> str:
        """Finalize the format of the forecast."""
        ts = datetime.now(tz=pytz.timezone(tz_name))
        forecasts = self.normalize_forecast_days(forecast_lines, ts)
        prefix = self.get_current_day_and_time(ts, location)
        logger.info(f"Prepared {len(forecasts)} forecast rows.")
        return "\n".join([prefix, "", "Forecast:"] + forecasts)

    def fetch_nws_forecast(
        self,
        forecast_url: str,
    ) -> Dict[str, Any]:
        """Get the weather forecast from the NWS API."""
        res = requests.get(forecast_url)
        return json.loads(res.content)

    async def afetch_nws_forecast(
        self,
        forecast_url: str,
    ) -> Dict[str, Any]:
        """Get the weather forecast from the NWS API."""
        async with aiohttp.ClientSession() as session:
            async with session.get(forecast_url) as res:
                return json.loads(await res.text())

    def extract_forecast_lines(
        self,
        forecast: Dict[str, Any],
    ) -> List[str]:
        """Extract the forecast lines from the NWS API response."""
        periods = forecast["properties"]["periods"]
        logger.info(f"Found {len(periods)} forecast periods.")
        return [f"{p['name']}: {p['detailedForecast']}" for p in periods]

    def fetch_nws_gridpoints(
        self,
        lat: str,
        lon: str,
    ) -> Dict[str, Any]:
        """Get the gridpoints from the NWS API for a given latitude and longitude."""
        resp = requests.get(f"{self.gridpoints_url}{lat},{lon}")
        return json.loads(resp.content)

    async def afetch_nws_gridpoints(
        self,
        lat: str,
        lon: str,
    ) -> Dict[str, Any]:
        """Get the gridpoints from the NWS API for a given latitude and longitude."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.gridpoints_url}{lat},{lon}") as resp:
                return json.loads(await resp.text())

    def extract_tz_and_forecast_url(
        self,
        gridpoints: Dict[str, Any],
    ) -> Tuple[str, str]:
        """Get the timezone and forecast url for a given latitude and longitude from the NWS API."""
        tz = gridpoints["properties"]["timeZone"]
        forecast_url = gridpoints["properties"]["forecast"]
        logger.info(f"Timezone: {tz}, Forecast URL: {forecast_url}")
        return (tz, forecast_url)

    def normalize_forecast_days(
        self,
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
        self,
        ts: datetime,
        location: str,
    ) -> str:
        """Build the string to present the llm with the current day of week, date, and time in the given location.

        Usage Examples:
        >>> NWSChain.get_current_day_and_time(datetime(2023, 1, 1, 12, 0, 0), "New York City")
        'The current day and local time in New York City is Sunday, January 01, 12:00 PM'
        """
        day = DAYS[ts.weekday()]
        prefix = "The current day and local time in"
        return f"{prefix} {location} is {day}, {ts.strftime('%B %d, %I:%M %p')}"
