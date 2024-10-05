# ☁️ ❄️ ⚡ Weather Chat AI ⛅ 🌡️ ☂️

☁️ ❄️ ⚡ Don't just get the weather. Get the answer to your underlying weather-related question. Using retrieval augmented generation with LangGraph, OpenAI, the National Weather Service, and Chainlit. ⛅ 🌡️ ☂️

Live Demo: https://weather-chat-ai.fly.dev/

## 👥 Who is this for?

WeatherChatAI is built for a couple different audiences:

First, it's for anyone who wants to learn how to 🛠️ build LLM applications. It's easier than ever to get started. Both models and tooling have progressed significantly since the initial version of this in July 2023. Simple agents built with [LangGraph](https://www.langchain.com/langgraph) just work out of the box. The forecast is massaged to make it more useful to the LLM, but as models improve, perhaps even this will become unnecessary.

WeatherChatAI is also built to help users learn how to leverage 💪 new AI-based tools. Our world is shifting paradigms from search engine to answer engine. The next phase in this incremental journey is well underway - a shift toward action engines. We will all become more productive as we begin to save time on the small things of everyday life, like getting answers to our weather-related questions.

## 📝 Examples

> User: Is tomorrow a good day to mow the yard in Boston?

> Weather Chat AI: Tomorrow in Boston, the weather is expected to be sunny with a high near 66°F. However, rain showers are likely to start after midnight, which means the ground may be wet in the morning.

Considering these conditions, it might be a good day to mow the yard in the afternoon if the ground is not too wet. Just be cautious of the rain starting later in the night.

> User: Is today a good day for a walk in Dallas?

> Weather Chat AI: Today in Dallas, the weather is sunny with a high near 92°F. The winds are light, which makes it a pleasant day for a walk. Enjoy your time outdoors!

> User: I'm traveling to Seattle on October 7th. Should I bring an umbrella?

> Weather Chat AI: On October 7th in Seattle, there is a 30% chance of rain in the afternoon, increasing to a 60% chance at night. With the likelihood of rain later in the day, it would be a good idea to bring an umbrella.

## ⚙️ How it works

1. Ask a weather related question.

   `Should I wear a jacket tonight in Denver?`

1. Based on the latest message, and the chat history, the agent decides what to search the weather tool for.
1. Deterministic code in the tool calls [Nominatim](https://nominatim.org/release-docs/develop/api/Overview/) to get the lat/lon.
1. Deterministic code in the tool calls NWS `points` endpoint to find the NWS grid and timezone.
1. Deterministic code in the tool calls NWS `gridpoints` endpoint to get the forecast.
1. Deterministic code cleans and normalizes the forecast for better augmentation of the LLM.
1. The LLM makes a reply based on the
   - original question
   - chat history
   - forecast
   - current day of the week
   - local time using the timezone retrieved from the call above

### Example Normalized Forecast

```
The current day and local time in Seattle, WA is Saturday, October 05, 10:12 AM

Forecast:
Today: Patchy fog before 11am. Mostly sunny, with a high near 64. West northwest wind 1 to 7 mph.
Tonight: Partly cloudy. Low around 48, with temperatures rising to around 50 overnight. North northeast wind 2 to 7 mph.
Sunday, October 06: Mostly sunny, with a high near 68. Southeast wind around 3 mph.
Sunday Night, October 06: Mostly clear, with a low around 49. South southeast wind around 3 mph.
Monday, October 07: A chance of rain after 5pm. Mostly sunny, with a high near 71. South wind 2 to 6 mph. Chance of precipitation is 30%.
Monday Night, October 07: Rain likely. Mostly cloudy, with a low around 57. Chance of precipitation is 60%. New rainfall amounts less than a tenth of an inch possible.
Tuesday, October 08: Rain likely. Mostly cloudy, with a high near 67. Chance of precipitation is 60%.
Tuesday Night, October 08: A chance of rain. Mostly cloudy, with a low around 55.
Wednesday, October 09: A chance of rain. Mostly cloudy, with a high near 65.
Wednesday Night, October 09: A chance of rain. Mostly cloudy, with a low around 53.
Thursday, October 10: A chance of rain. Mostly cloudy, with a high near 62.
Thursday Night, October 10: A chance of rain. Mostly cloudy, with a low around 50.
Friday, October 11: A chance of rain. Mostly cloudy, with a high near 61.
Friday Night, October 11: A chance of rain. Mostly cloudy, with a low around 50.
```

## ✔️ Prerequisites

- python3 - tested with 3.11.10
- [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
- [OpenAI](https://openai.com/) API key

## 🚀 Setup

```
git clone git@github.com:mattflo/WeatherChatAI.git
cd WeatherChatAI
```

```
poetry install
```

```
cp .env.example .env
```

Add your open ai api key to `.env`. See [.env.example](.env.example)

```
make chainlit
```

## 🧭 Roadmap

- [x] Use LangGraph agent
- [ ] International Support
- [ ] Experiment with OSS alternatives to OpenAI
