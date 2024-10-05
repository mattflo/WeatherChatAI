from datetime import datetime

from weather_chat_ai.tool import normalize_forecast_days


def test_day_name_normalization():
    forecast = [
        "Today: A chance of showers and thunderstorms after noon. Partly sunny. High near 73, with temperatures falling to around 71 in the afternoon. North northeast wind around 13 mph, with gusts as high as 21 mph. Chance of precipitation is 40%. New rainfall amounts between a tenth and quarter of an inch possible.",
        "Tonight: A chance of showers and thunderstorms before 11pm. Mostly clear, with a low around 45. West wind 6 to 10 mph, with gusts as high as 16 mph. Chance of precipitation is 40%.",
        "Monday: A slight chance of showers and thunderstorms after noon. Mostly sunny. High near 79, with temperatures falling to around 74 in the afternoon. North wind around 13 mph, with gusts as high as 21 mph.",
        "Monday Night: Partly cloudy, with a low around 47. South southwest wind around 9 mph.",
        "Independence Day: A chance of showers and thunderstorms after noon. Partly sunny, with a high near 74. Southeast wind 7 to 15 mph, with gusts as high as 24 mph. Chance of precipitation is 50%.",
        "Tuesday Night: A chance of showers and thunderstorms. Mostly cloudy, with a low around 44. Chance of precipitation is 40%.",
        "Wednesday: A slight chance of rain showers before noon, then showers and thunderstorms likely. Partly sunny, with a high near 62. Chance of precipitation is 60%.",
        "Wednesday Night: A chance of showers and thunderstorms before midnight. Mostly cloudy, with a low around 44.",
        "Thursday: A chance of showers and thunderstorms after noon. Mostly sunny, with a high near 73.",
        "Thursday Night: A chance of showers and thunderstorms before midnight. Partly cloudy, with a low around 45.",
        "Friday: A chance of showers and thunderstorms after noon. Mostly sunny, with a high near 75.",
        "Friday Night: A chance of showers and thunderstorms before midnight. Partly cloudy, with a low around 48.",
        "Saturday: A chance of showers and thunderstorms after noon. Mostly sunny, with a high near 77.",
        "Saturday Night: A slight chance of showers and thunderstorms before midnight. Partly cloudy, with a low around 48.",
    ]

    normalized_forecast = normalize_forecast_days(forecast, datetime(2023, 7, 2))

    assert (
        "Tuesday, July 04: A chance of showers and thunderstorms after noon. Partly sunny, with a high near 74. Southeast wind 7 to 15 mph, with gusts as high as 24 mph. Chance of precipitation is 50%."
        == normalized_forecast[4]
    ), "It should add the date to the label and replace Independence Day with Tuesday."

    assert (
        "Tuesday Night, July 04: A chance of showers and thunderstorms. Mostly cloudy, with a low around 44. Chance of precipitation is 40%."
        == normalized_forecast[5]
    ), "It should add the date to the label."
