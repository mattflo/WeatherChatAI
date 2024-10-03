import pytest
import structlog

from weather_chat_ai.nominatim import get_lat_lon

logger = structlog.get_logger(__name__)


# @pytest.mark.focus
def test_get_lat_lon():
    lat, lon = get_lat_lon("Denver")
    logger.info("Lat and lon", lat=lat, lon=lon)
    assert lat == "39.7392364"
    assert lon == "-104.984862"

    lat2, lon2 = get_lat_lon("Denver")
    logger.info("Lat and lon", lat=lat2, lon=lon2)
    assert lat == "39.7392364"
    assert lon == "-104.984862"


# @pytest.mark.focus
def test_non_existent_location():
    lat, lon = get_lat_lon("City or Attraction, State if needed [")
    logger.info("Lat and lon", lat=lat, lon=lon)
