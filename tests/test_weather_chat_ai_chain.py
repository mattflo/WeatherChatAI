import pytest
from langchain.globals import set_debug

from weather_chat_ai.base import WeatherChatAIChain


@pytest.mark.focus
def test_chain_with_memory():
    set_debug(False)

    chain = WeatherChatAIChain()

    assert chain is not None, "chain should have been created"

    answer = chain.invoke("What is the weather today in Breckenridge?")

    print(answer)

    assert isinstance(answer, str), "answer should be a string"
    assert len(answer) > 0, "answer should not be empty"
    assert "breckenridge" in answer.lower(), "answer should mention location"

    answer2 = chain.invoke("what about tomorrow?")

    print(answer2)
    assert "breckenridge" in answer2.lower(), "answer2 should have remembered location"
