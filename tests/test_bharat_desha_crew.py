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
