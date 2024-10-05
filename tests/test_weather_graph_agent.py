import pytest
from langchain_core.messages import AIMessage, HumanMessage

from weather_chat_ai.weather_graph_agent import WeatherGraphAgent


# @pytest.mark.focus
@pytest.mark.asyncio
async def test_astream_with_memory():
    inputs = [
        [
            "What is the weather today in Breckenridge?",
            "answer should mention location",
        ],
        ["what about tomorrow?", "answer2 should have remembered location"],
    ]

    chat_history = []
    for input, location_assertion in inputs:
        chat_history.append(HumanMessage(content=input))
        agent = WeatherGraphAgent(messages=chat_history)

        answer = ""
        async for chunk in agent.astream():
            answer += chunk

        chat_history.append(AIMessage(content=answer))

        assert isinstance(answer, str), "answer should be a string"
        assert len(answer) > 0, "answer should not be empty"
        assert "breckenridge" in answer.lower(), location_assertion
