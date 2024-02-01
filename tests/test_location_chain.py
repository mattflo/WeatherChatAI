from pprint import pprint

import pytest

from weather_chat_ai.location_chain import LocationChain

test_samples = [
    {
        "query": "I'm planning a picnic in Central Park this Saturday. Will the weather be sunny enough?",
        "expected": "New York, NY",
    },
    {
        "query": "I have a business meeting in Chicago next Wednesday. Should I expect snow and bring appropriate clothing?",
        "expected": "Chicago, IL",
    },
    {
        "query": "I'm attending a wedding in Miami this weekend. Is it going to be hot, or do I need something for cooler evenings?",
        "expected": "Miami, FL",
    },
    {
        "query": "I have a hiking trip scheduled in Denver next Tuesday. Will there be any rain or should I prepare for a dry day?",
        "expected": "Denver, CO",
    },
    {
        "query": "I'm going to a baseball game in Boston on Friday. Will it be clear or should I bring a poncho?",
        "expected": "Boston, MA",
    },
    {
        "query": "I'm visiting family in Dallas this Thursday. Is the weather going to be warm enough for outdoor activities?",
        "expected": "Dallas, TX",
    },
    {
        "query": "I'm taking a photography tour in San Francisco next Sunday. Will fog affect visibility?",
        "expected": "San Francisco, CA",
    },
    {
        "query": "I'm going to a concert in Nashville next Saturday. Should I prepare for hot weather or bring a light jacket?",
        "expected": "Nashville, TN",
    },
    {
        "query": "I have a beach day planned in Los Angeles next Monday. Will it be sunny or do I need to worry about rain?",
        "expected": "Los Angeles, CA",
    },
    {
        "query": "I'm attending a conference in Atlanta this Friday. Is the weather going to be humid, requiring lighter clothing?",
        "expected": "Atlanta, GA",
    },
    {
        "query": "I'm planning a road trip to Phoenix next week. Should I expect extremely hot temperatures?",
        "expected": "Phoenix, AZ",
    },
    {
        "query": "I'm going on a fishing trip in New Orleans this Sunday. Will the weather be suitable for spending the day outdoors?",
        "expected": "New Orleans, LA",
    },
    {
        "query": "I have an outdoor art show in Portland next Saturday. Will it be dry, or should I prepare for rain?",
        "expected": "Portland, OR",
    },
    {
        "query": "I'm visiting the Space Needle in Seattle next Wednesday. Will I need a jacket for the cooler temperatures?",
        "expected": "Seattle, WA",
    },
    {
        "query": "I'm going to an outdoor theatre in Minneapolis this Thursday. Do I need to dress warmly?",
        "expected": "Minneapolis, MN",
    },
    {
        "query": "I have a garden tour in Austin next Tuesday. Will the weather be too hot for a long day outside?",
        "expected": "Austin, TX",
    },
    {
        "query": "I'm going kayaking in Charleston this weekend. Should I expect sunny weather or prepare for potential rain?",
        "expected": "Charleston, SC",
    },
    {
        "query": "I have a golf outing in Palm Springs next Monday. Will it be too hot for a midday game?",
        "expected": "Palm Springs, CA",
    },
    {
        "query": "I'm attending a street festival in Philadelphia this Friday. Is the forecast predicting clear skies?",
        "expected": "Philadelphia, PA",
    },
    {
        "query": "I'm visiting the Grand Canyon near Flagstaff next Sunday. Should I expect windy conditions or a calm day?",
        "expected": "Flagstaff, AZ",
    },
]


chain = LocationChain()


def run_chain(test):
    query = test["query"]
    res = chain.invoke({"input": query, "history": ""})

    test["actual"] = res["location"]
    return test


@pytest.mark.skip
@pytest.mark.parametrize("test", test_samples[:])
def test_location_chain(test):
    result = run_chain(test)
    expected, actual, query = result["expected"], result["actual"], result["query"]

    assert (
        actual == expected
    ), f"Expected {expected}, but got {actual} for query: {query}"


# @pytest.mark.focus
def test_threshold_location_chain():
    results = [run_chain(test) for test in test_samples[:]]
    incorrect = [r for r in results if r["expected"] != r["actual"]]

    if incorrect:
        print("Incorrect results:")
        pprint(incorrect)

    total = len(results)
    accuracy = 1 - len(incorrect) / total
    print(f"Accuracy: {accuracy * 100:.2f}% for {total} samples.")

    threshold = 0.95
    assert accuracy >= threshold, f"Accuracy is below threshold of {threshold}"
