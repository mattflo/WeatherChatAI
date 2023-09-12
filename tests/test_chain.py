from datetime import datetime
import pytest
import time
from weather_chat_ai.chat import WeatherChat


def dated_tag():
    current_date = datetime.now().strftime("%Y%m%d")
    epoch_timestamp = str(time.time())[-4:]
    return f"{current_date}-{epoch_timestamp}"


@pytest.mark.asyncio
async def test_chain():
    day_of_week = datetime.now().strftime("%A")
    chain = WeatherChat(tags=[dated_tag()])
    queries = [
        "what is the weather in london today?",
        f"what is the weather next {day_of_week}?",
        "What is the weather today in Denver, CO?",
    ]

    results = []

    for query in queries:
        result = await chain.acall({"input": query})
        results.append(result)

    print(results)
