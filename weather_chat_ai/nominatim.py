from functools import lru_cache

import requests
import structlog

logger = structlog.get_logger(__name__)


@lru_cache(maxsize=2048)
def get_lat_lon(query: str) -> tuple[str, str]:
    """
    Get the latitude and longitude of a city using the Nominatim API.
    """
    # Nominatim wants you to limit requests to a maximum of 1 request per second.
    # see: https://operations.osmfoundation.org/policies/nominatim/
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
    headers = {"User-Agent": "github.com/mattflo/WeatherChatAI"}
    logger.info(f"Calling nominatim with query: {query}")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response_json = response.json()[0]
        lat, lon = response_json["lat"], response_json["lon"]
        return lat, lon
    else:
        return None, None
