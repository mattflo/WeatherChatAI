import logging
import json
import os
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytz
import requests
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain
from serpapi import GoogleSearch

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


def create_logger(name):
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    formatter = logging.Formatter(FORMAT)
    ch.setFormatter(formatter)
    return logger


logger = create_logger(__name__)


class NWSChain(Chain):
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        input = inputs["location"].strip()
        inputs["location"] = input
        forecast = self.nws_weather(input)
        return {"forecast": forecast}

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        input = inputs["location"].strip()
        inputs["location"] = input
        forecast = await self.nws_weather(input)
        return {"forecast": forecast}

    @property
    def input_keys(self) -> List[str]:
        return ["location"]

    @property
    def output_keys(self) -> List[str]:
        return ["forecast"]

    async def nws_weather(self, location):
        """Get the weather forecast for a given location."""
        try:
            logger.info(f"Retrieving forecast for: {location}")
            lat, lon = self.get_lat_lon(location)
            (tz_name, forecast_url) = self.get_nws_gridpoints(lat, lon)
            nws_forecasts = self.get_nws_forecast(forecast_url)
            ts = datetime.now(tz=pytz.timezone(tz_name))
            forecasts = self.normalize_forecast_days(nws_forecasts, ts)
            prefix = self.get_current_day_and_time(ts, location)
            logger.info(f"Prepared {len(forecasts)} forecast rows.")
            return "\n".join([prefix, "", "Forecast:"] + forecasts)
        except Exception as e:
            logger.exception("Failed to get weather forecast.")
            return {"forecast": f"Sorry, I'm having trouble finding the weather for {location}."}

    @staticmethod
    def get_nws_forecast(forecast_url):
        """Get the weather forecast from the NWS API."""
        res = requests.get(forecast_url)
        forecast = json.loads(res.content)
        periods = forecast["properties"]["periods"]
        logger.info(f"Found {len(periods)} forecast periods.")
        return [f"{p['name']}: {p['detailedForecast']}" for p in periods]

    @staticmethod
    def get_lat_lon(location):
        """Get the latitude and longitude for a given location from google maps using SerpApi."""
        search = GoogleSearch(
            {
                "engine": "google_maps",
                "q": location,
                "num_hits": 1,
                "api_key": os.environ["SERPAPI_API_KEY"],
            }
        )
        res = search.get_dict()
        gps = res["place_results"]["gps_coordinates"]
        lat = gps["latitude"]
        lon = gps["longitude"]
        logger.info(f"Found lat/lon: {lat}, {lon}")
        return (lat, lon)

    @staticmethod
    def get_nws_gridpoints(lat, lon):
        """Get the timezone and forecast url for a given latitude and longitude from the NWS API."""
        resp = requests.get(f"https://api.weather.gov/points/{lat},{lon}")
        j = json.loads(resp.content)
        tz = j["properties"]["timeZone"]
        forecast_url = j["properties"]["forecast"]
        logger.info(f"Timezone: {tz}, Forecast URL: {forecast_url}")
        return (tz, forecast_url)

    @staticmethod
    def normalize_forecast_days(forecast, ts):
        """Normalize the labels for the days and nights of the forecast to eliminate holiday names and add dates."""
        current_day_of_week_index = ts.weekday()
        for index, row in enumerate(forecast[2::2]):
            ts += timedelta(days=1)
            date = ts.strftime("%B %d")
            day_label = DAYS[(current_day_of_week_index + 1 + index) % 7]
            forecast[index * 2 + 2] = f"{day_label}, {date}: {row.split(': ', 1)[1]}"
            next_row = forecast[index * 2 + 3]
            forecast[
                index * 2 + 3
            ] = f"{day_label} Night, {date}: {next_row.split(': ', 1)[1]}"
        return forecast

    @staticmethod
    def get_current_day_and_time(ts, location):
        """Build the string to present the llm with the current day of week, date, and time in the given location.

        Usage Examples:
        >>> NWSChain.get_current_day_and_time(datetime(2023, 1, 1, 12, 0, 0), "New York City")
        'The current day and local time in New York City is Sunday, January 01, 12:00 PM'
        """
        day = DAYS[ts.weekday()]
        prefix = "The current day and local time in"
        return f"{prefix} {location} is {day}, {ts.strftime('%B %d, %I:%M %p')}"
