# ☁️ ❄️ ⚡ Weather Chat AI ⛅ 🌡️ ☂️

## ☀️ Conversational Weather 💦

There are dozens of weather APIs out there. But most of them aren't well suited to chat over. They are made for computers 🖥️ to consume, not LLMs 🧠. Then I realized the old-school  🏫 🇺🇸 [National Weather Service](https://www.weather.gov/) text based forecast would be perfect.

Live Demo: https://weather-chat-ai.fly.dev/

## ⚙️ How it works

1. Ask a weather related question.

    `Should I wear a jacket tonight in Denver?`

1. An LLMChain coerces the location of the request into City, ST format. If no location was provided in the question, it defaults to Denver, CO.
1. Call SerpApi for the location to get the lat/lon.
1. Call NWS `points` endpoint to find the NWS grid and timezone.
1. Call NWS `gridpoints` endpoint to get the forecast.
1. The labels for each day in the forecast are normalized to remove holiday names and dates are also added for additional context.
1. A conversational LLM makes a reply based on the
    * question
    * forecast
    * current day of the week
    * local time using the timezone retrieved from the call above
```
Answer a question about the weather. Below is the forecast you should use to answer the question. It includes the current day and time for reference. You may include the location in your answer, but you should not include the current day or time. If you don't know the answer, don't make anything up. Just say you don't know.

The current day and local time in Denver, CO is Friday, June 30, 04:45 PM

Forecast:
This Afternoon: Showers and thunderstorms likely. Mostly cloudy. High near 73, with temperatures falling to around 70 in the afternoon. North northeast wind around 10 mph, with gusts as high as 16 mph. Chance of precipitation is 60%. New rainfall amounts between a tenth and quarter of an inch possible.
Tonight: A chance of showers and thunderstorms before 9pm. Partly cloudy, with a low around 53. West northwest wind 3 to 9 mph. Chance of precipitation is 30%.
Saturday, July 01: Sunny, with a high near 79. North wind 3 to 13 mph, with gusts as high as 21 mph.
Saturday Night, July 01: Mostly clear, with a low around 58. South wind 5 to 9 mph.
Sunday, July 02: Mostly sunny, with a high near 88. North northeast wind 5 to 12 mph, with gusts as high as 18 mph.
Sunday Night, July 02: Mostly clear, with a low around 59.
Monday, July 03: Sunny, with a high near 92.
Monday Night, July 03: Partly cloudy, with a low around 61.
Tuesday, July 04: A chance of showers and thunderstorms after noon. Mostly sunny, with a high near 88.
Tuesday Night, July 04: A chance of showers and thunderstorms before midnight. Partly cloudy, with a low around 59.
Wednesday, July 05: A chance of showers and thunderstorms after noon. Partly sunny, with a high near 76.
Wednesday Night, July 05: A chance of showers and thunderstorms. Mostly cloudy, with a low around 58.
Thursday, July 06: A chance of showers and thunderstorms after noon. Partly sunny, with a high near 80.
Thursday Night, July 06: A chance of showers and thunderstorms before midnight. Partly cloudy, with a low around 58.

Never answer with the entire forecast. If the question doesn't contain any specifics, just answer with the current weather for today or tonight. If it's a yes or no question, provide supporting details from the forecast for your answer.

Location: Denver, CO
Question: Should I wear a jacket tonight in Denver?
Yes, you should wear a jacket tonight in Denver. The forecast indicates a low around 53 degrees with a west northwest wind of 3 to 9 mph.
```

## 📝 Other Examples

> User: Is tomorrow a good day to mow the yard in Boston?

> Weather Chat AI: Based on the forecast for tomorrow in Boston, it is not the best day to mow the yard. There is a chance of rain showers and thunderstorms throughout the day, with a 60% chance of precipitation. Additionally, there is a chance of showers and thunderstorms likely in the afternoon. It would be better to choose a day with more favorable weather conditions for mowing the yard.

> User: Is today a good day for a walk in Dallas?

> Weather Chat AI: Today in Dallas, there is a chance of showers and thunderstorms, with temperatures reaching a high of around 95 degrees. The heat index values could be as high as 104. It may not be the most ideal day for a walk due to the potential for rain and the high temperatures.

> User: I'm traveling to Seattle on July 5. Should I bring an umbrella?

> Weather Chat AI: No, you should not bring an umbrella when traveling to Seattle on July 5. The forecast for that day is sunny with a high near 82 degrees.

## ✔️ Prerequisites

* python3 - tested with 3.10
* [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
* [OpenAI](https://openai.com/) API key
* [SerpApi](https://serpapi.com/) API key

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

Add your open api and serpapi keys to `.env`. See [.env.example](.env.example)

```
make chainlit
```
