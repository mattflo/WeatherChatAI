import time
from datetime import datetime

import pytest

from weather_chat_ai.weather_chat_chain import WeatherChatChain


def dated_tag():
    current_date = datetime.now().strftime("%Y%m%d")
    epoch_timestamp = str(time.time())[-4:]
    return f"{current_date}-{epoch_timestamp}"


# @pytest.mark.focus
@pytest.mark.asyncio
async def test_chain():
    chain = WeatherChatChain(tags=[dated_tag()])
    result = await chain.acall("What is the weather today in Denver, CO?")

    assert "in Denver" in result["text"]
