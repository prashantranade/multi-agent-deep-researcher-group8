import os
os.environ.setdefault("OPENROUTER_API_KEY", "x")
os.environ.setdefault("TAVILY_API_KEY", "x")

import config

def test_bharat_desha_table_config():
    assert config.BHARAT_DESHA_TABLE == "bharat_desha"


from unittest.mock import patch, MagicMock

def test_trend_agent_returns_structured_output():
    from crews.bharat_desha.trend_agent import run_trend_agent

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [
            {"title": "Top spiritual destinations India 2025", "content": "Varanasi is trending..."},
            {"title": "Best time to visit Rishikesh", "content": "October to March is ideal..."},
        ]
    }

    mock_llm_response = """{
        "trends": ["Varanasi pilgrimages trending in 2025", "Yoga retreats in Rishikesh up 30%"],
        "seasonality": {
            "best_months": ["October", "November", "February", "March"],
            "avoid_months": ["June", "July", "August"],
            "active_festivals": ["Diwali (Oct)", "Mahashivratri (Feb)"],
            "advisories": []
        },
        "topic_suggestions": [
            "Varanasi spiritual guide for first-time visitors",
            "Rishikesh yoga retreat 7-day itinerary",
            "Best temples in Varanasi during Diwali"
        ]
    }"""

    with patch("crews.bharat_desha.trend_agent.TavilyClient", return_value=mock_tavily), \
         patch("crews.bharat_desha.trend_agent.chat_with_fallback", return_value=mock_llm_response):
        result = run_trend_agent("spiritual destinations Varanasi")

    assert "trends" in result
    assert "seasonality" in result
    assert "topic_suggestions" in result
    assert len(result["topic_suggestions"]) >= 1
    assert "best_months" in result["seasonality"]


def test_seo_agent_returns_ten_keywords():
    from crews.bharat_desha.seo_agent import run_seo_agent

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [
            {"content": "Varanasi ghats spiritual guide Kashi Vishwanath temple Ganga aarti"},
        ]
    }

    mock_llm_response = """{
        "keywords": [
            {"keyword": "Varanasi spiritual tour", "intent": "informational"},
            {"keyword": "Kashi Vishwanath temple guide", "intent": "informational"},
            {"keyword": "Ganga aarti Varanasi", "intent": "informational"},
            {"keyword": "Varanasi ghats walk", "intent": "informational"},
            {"keyword": "best time to visit Varanasi", "intent": "informational"},
            {"keyword": "Varanasi pilgrimage package", "intent": "transactional"},
            {"keyword": "Manikarnika ghat Varanasi", "intent": "navigational"},
            {"keyword": "Varanasi boat ride at sunrise", "intent": "informational"},
            {"keyword": "Sanatan Dharma sacred city India", "intent": "informational"},
            {"keyword": "Varanasi travel tips first time", "intent": "informational"}
        ],
        "primary_keyword": "Varanasi spiritual tour"
    }"""

    trend_context = {"trends": ["Varanasi pilgrimages trending"], "seasonality": {}, "topic_suggestions": []}

    with patch("crews.bharat_desha.seo_agent.TavilyClient", return_value=mock_tavily), \
         patch("crews.bharat_desha.seo_agent.chat_with_fallback", return_value=mock_llm_response):
        result = run_seo_agent("Varanasi spiritual tour", trend_context)

    assert "keywords" in result
    assert len(result["keywords"]) == 10
    assert "primary_keyword" in result
    assert all("keyword" in k and "intent" in k for k in result["keywords"])
