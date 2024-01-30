import pytest

from weather_chat_ai.location_chain import LocationChain

test_samples = [
    {
        "query": "I'm planning a picnic in Central Park this Saturday. Will the weather be sunny enough?",
        "city": "New York, NY",
    },
    {
        "query": "I have a business meeting in Chicago next Wednesday. Should I expect snow and bring appropriate clothing?",
        "city": "Chicago, IL",
    },
    {
        "query": "I'm attending a wedding in Miami this weekend. Is it going to be hot, or do I need something for cooler evenings?",
        "city": "Miami, FL",
    },
    {
        "query": "I have a hiking trip scheduled in Denver next Tuesday. Will there be any rain or should I prepare for a dry day?",
        "city": "Denver, CO",
    },
    {
        "query": "I'm going to a baseball game in Boston on Friday. Will it be clear or should I bring a poncho?",
        "city": "Boston, MA",
    },
    {
        "query": "I'm visiting family in Dallas this Thursday. Is the weather going to be warm enough for outdoor activities?",
        "city": "Dallas, TX",
    },
    {
        "query": "I'm taking a photography tour in San Francisco next Sunday. Will fog affect visibility?",
        "city": "San Francisco, CA",
    },
    {
        "query": "I'm going to a concert in Nashville next Saturday. Should I prepare for hot weather or bring a light jacket?",
        "city": "Nashville, TN",
    },
    {
        "query": "I have a beach day planned in Los Angeles next Monday. Will it be sunny or do I need to worry about rain?",
        "city": "Los Angeles, CA",
    },
    {
        "query": "I'm attending a conference in Atlanta this Friday. Is the weather going to be humid, requiring lighter clothing?",
        "city": "Atlanta, GA",
    },
    {
        "query": "I'm planning a road trip to Phoenix next week. Should I expect extremely hot temperatures?",
        "city": "Phoenix, AZ",
    },
    {
        "query": "I'm going on a fishing trip in New Orleans this Sunday. Will the weather be suitable for spending the day outdoors?",
        "city": "New Orleans, LA",
    },
    {
        "query": "I have an outdoor art show in Portland next Saturday. Will it be dry, or should I prepare for rain?",
        "city": "Portland, OR",
    },
    {
        "query": "I'm visiting the Space Needle in Seattle next Wednesday. Will I need a jacket for the cooler temperatures?",
        "city": "Seattle, WA",
    },
    {
        "query": "I'm going to an outdoor theatre in Minneapolis this Thursday. Do I need to dress warmly?",
        "city": "Minneapolis, MN",
    },
    {
        "query": "I have a garden tour in Austin next Tuesday. Will the weather be too hot for a long day outside?",
        "city": "Austin, TX",
    },
    {
        "query": "I'm going kayaking in Charleston this weekend. Should I expect sunny weather or prepare for potential rain?",
        "city": "Charleston, SC",
    },
    {
        "query": "I have a golf outing in Palm Springs next Monday. Will it be too hot for a midday game?",
        "city": "Palm Springs, CA",
    },
    {
        "query": "I'm attending a street festival in Philadelphia this Friday. Is the forecast predicting clear skies?",
        "city": "Philadelphia, PA",
    },
    {
        "query": "I'm visiting the Grand Canyon near Flagstaff next Sunday. Should I expect windy conditions or a calm day?",
        "city": "Flagstaff, AZ",
    },
]


# @pytest.mark.focus
@pytest.mark.parametrize("test", test_samples)
def test_location_chain(test):
    chain = LocationChain()

    query = test["query"]
    expected = test["city"]

    res = chain.invoke({"input": query, "history": ""})

    location = res["location"]

    assert location == expected, f"Expected {expected} for query: {query}"
