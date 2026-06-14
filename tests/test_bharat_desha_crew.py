import os
os.environ.setdefault("OPENROUTER_API_KEY", "x")
os.environ.setdefault("TAVILY_API_KEY", "x")

import config

def test_bharat_desha_table_config():
    assert config.BHARAT_DESHA_TABLE == "bharat_desha"


from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage

def test_trend_agent_returns_structured_output():
    from crews.bharat_desha.trend_agent import run_trend_agent

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [
            {"title": "Top spiritual destinations India 2025", "content": "Varanasi is trending..."},
            {"title": "Best time to visit Rishikesh", "content": "October to March is ideal..."},
        ]
    }

    mock_llm_response = AIMessage(content="""{
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
    }""")

    with patch("crews.bharat_desha.trend_agent.TavilyClient", return_value=mock_tavily), \
         patch("crews.bharat_desha.trend_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_llm_response
        mock_get_llm.return_value = mock_llm
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

    mock_llm_response = AIMessage(content="""{
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
    }""")

    trend_context = {"trends": ["Varanasi pilgrimages trending"], "seasonality": {}, "topic_suggestions": []}

    with patch("crews.bharat_desha.seo_agent.TavilyClient", return_value=mock_tavily), \
         patch("crews.bharat_desha.seo_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_llm_response
        mock_get_llm.return_value = mock_llm
        result = run_seo_agent("Varanasi spiritual tour", trend_context)

    assert "keywords" in result
    assert len(result["keywords"]) == 10
    assert "primary_keyword" in result
    assert all("keyword" in k and "intent" in k for k in result["keywords"])


def test_retrieval_agent_returns_chunks():
    from crews.bharat_desha.retrieval_agent import run_retrieval_agent

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [
            {"url": "https://example.com/varanasi", "title": "Varanasi Guide", "content": "Varanasi is the spiritual capital of India..."},
        ]
    }

    mock_vector_store = MagicMock()
    mock_vector_store.search.return_value = [
        {"text": "Varanasi is the spiritual capital of India...", "metadata": {"source": "https://example.com/varanasi"}}
    ]

    seo_context = {
        "keywords": [{"keyword": "Varanasi spiritual tour", "intent": "informational"}],
        "primary_keyword": "Varanasi spiritual tour"
    }

    with patch("crews.bharat_desha.retrieval_agent.TavilyClient", return_value=mock_tavily), \
         patch("crews.bharat_desha.retrieval_agent.VectorStore", return_value=mock_vector_store):
        result = run_retrieval_agent("Varanasi spiritual tour", seo_context)

    assert isinstance(result, list)
    assert len(result) > 0
    assert "text" in result[0]
    assert "metadata" in result[0]


def test_analysis_agent_returns_bharat_desha_lens():
    from crews.bharat_desha.analysis_agent import run_analysis_agent

    retrieved = [
        {"text": "Varanasi is considered the holiest city in Hinduism...", "metadata": {"source": "https://example.com"}},
        {"text": "Best time to visit is October to March for ghats walk...", "metadata": {"source": "https://example.com"}},
    ]
    seo_context = {"keywords": [{"keyword": "Varanasi spiritual tour", "intent": "informational"}], "primary_keyword": "Varanasi spiritual tour"}
    trend_context = {"seasonality": {"best_months": ["October", "March"], "active_festivals": ["Diwali"]}, "trends": []}

    mock_response = AIMessage(content="""{
        "spiritual": "Varanasi is the abode of Lord Shiva, one of the 12 Jyotirlingas...",
        "practical": "Fly to Varanasi airport (VNS), auto-rickshaw to ghats costs 150 INR...",
        "cultural": "Ganga aarti at Dashashwamedh Ghat runs every evening at 7pm...",
        "wellness": "Several ashrams offer 5-day yoga and meditation retreats near Assi Ghat...",
        "seasonal": "October to March is ideal; avoid June-August monsoon...",
        "key_points": ["Visit Kashi Vishwanath temple at dawn", "Sunrise boat ride on the Ganga"],
        "citations": ["https://example.com"]
    }""")

    with patch("crews.bharat_desha.analysis_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        result = run_analysis_agent(retrieved, seo_context, trend_context)

    for key in ["spiritual", "practical", "cultural", "wellness", "seasonal", "key_points", "citations"]:
        assert key in result
    assert isinstance(result["key_points"], list)


def test_content_agent_generates_blog_post():
    from crews.bharat_desha.content_agent import run_content_agent

    analysis = {
        "spiritual": "Varanasi is the abode of Lord Shiva...",
        "practical": "Fly into VNS airport...",
        "cultural": "Ganga aarti at Dashashwamedh Ghat...",
        "wellness": "Several ashrams near Assi Ghat...",
        "seasonal": "October to March is ideal...",
        "key_points": ["Visit at dawn", "Sunrise boat ride"],
        "citations": ["https://example.com"]
    }
    seo_context = {
        "keywords": [{"keyword": "Varanasi spiritual tour", "intent": "informational"}],
        "primary_keyword": "Varanasi spiritual tour"
    }

    mock_response = AIMessage(content="# Varanasi Spiritual Tour: Your Complete Guide\n\nVaranasi spiritual tour begins at dawn on the banks of the sacred Ganga river, one of the holiest journeys in Sanatan Dharma.")

    with patch("crews.bharat_desha.content_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        result = run_content_agent(analysis, seo_context, artifact_type="blog_post", tone="warm", depth="standard")

    assert result["type"] == "blog_post"
    assert len(result["content"]) > 100
    assert "citations" in result

def test_content_agent_generates_itinerary():
    from crews.bharat_desha.content_agent import run_content_agent

    analysis = {
        "spiritual": "...", "practical": "...", "cultural": "...",
        "wellness": "...", "seasonal": "...",
        "key_points": ["Day 1: Arrive", "Day 2: Ghats"],
        "citations": ["https://example.com"]
    }
    seo_context = {"keywords": [], "primary_keyword": "Varanasi itinerary"}

    mock_response = AIMessage(content="## Day 1: Arrival in Varanasi\n\nCheck into your hotel near Assi Ghat...")

    with patch("crews.bharat_desha.content_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        result = run_content_agent(analysis, seo_context, artifact_type="itinerary", tone="practical", depth="deep")

    assert result["type"] == "itinerary"
    assert "content" in result


def test_social_agent_generates_instagram():
    from crews.bharat_desha.social_agent import run_social_agent

    primary_artifact = {
        "type": "blog_post",
        "content": "# Varanasi Spiritual Tour\n\nVaranasi spiritual tour begins at dawn...",
        "citations": []
    }
    key_points = ["Visit Kashi Vishwanath at dawn", "Sunrise boat ride on the Ganga"]
    seo_context = {"primary_keyword": "Varanasi spiritual tour", "keywords": []}

    mock_response = AIMessage(content="Step into the sacred energy of Varanasi The ghats come alive at dawn...\n\n#VaranasiTravel #SpiritualIndia #BharatDesha")

    with patch("crews.bharat_desha.social_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        results = run_social_agent(primary_artifact, key_points, seo_context, platforms=["instagram"])

    assert len(results) == 1
    assert results[0]["type"] == "instagram"
    assert len(results[0]["content"]) > 50

def test_social_agent_generates_multiple_platforms():
    from crews.bharat_desha.social_agent import run_social_agent

    primary_artifact = {"type": "blog_post", "content": "Varanasi guide...", "citations": []}
    key_points = ["Key point 1"]
    seo_context = {"primary_keyword": "Varanasi guide", "keywords": []}

    with patch("crews.bharat_desha.social_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="mock social content")
        mock_get_llm.return_value = mock_llm
        results = run_social_agent(primary_artifact, key_points, seo_context, platforms=["instagram", "facebook", "x_post", "youtube"])

    assert len(results) == 4
    types = [r["type"] for r in results]
    assert set(types) == {"instagram", "facebook", "x_post", "youtube"}


def test_bharat_desha_crew_run_returns_crew_output():
    from crews.bharat_desha.crew import BharatDeshaCrew
    from crews.base_crew import ResearchBrief, CrewOutput

    brief = ResearchBrief(
        topic="Varanasi spiritual tour",
        persona="bharat_desha",
        audience="solo spiritual travellers",
        tone="warm",
        depth="standard",
        selected_artifacts=["blog_post", "instagram"],
    )

    mock_trend = {
        "trends": ["Varanasi trending"],
        "seasonality": {"best_months": ["October"], "avoid_months": [], "active_festivals": [], "advisories": []},
        "topic_suggestions": ["Varanasi ghats guide"]
    }
    mock_seo = {
        "keywords": [{"keyword": "Varanasi spiritual tour", "intent": "informational"}],
        "primary_keyword": "Varanasi spiritual tour"
    }
    mock_retrieved = [{"text": "Varanasi is sacred...", "metadata": {"source": "https://example.com"}}]
    mock_analysis = {
        "spiritual": "Sacred city...", "practical": "Fly to VNS...",
        "cultural": "Ganga aarti...", "wellness": "Ashrams nearby...",
        "seasonal": "Oct-March best...",
        "key_points": ["Visit at dawn"],
        "citations": ["https://example.com"]
    }
    mock_blog = {"type": "blog_post", "content": "# Varanasi Guide\n\n...", "citations": []}
    mock_social = [{"type": "instagram", "content": "Caption here..."}]

    with patch("crews.bharat_desha.crew.run_trend_agent", return_value=mock_trend), \
         patch("crews.bharat_desha.crew.run_seo_agent", return_value=mock_seo), \
         patch("crews.bharat_desha.crew.run_retrieval_agent", return_value=mock_retrieved), \
         patch("crews.bharat_desha.crew.run_analysis_agent", return_value=mock_analysis), \
         patch("crews.bharat_desha.crew.run_content_agent", return_value=mock_blog), \
         patch("crews.bharat_desha.crew.run_social_agent", return_value=mock_social):

        crew = BharatDeshaCrew()
        output = crew.run(brief)

    assert isinstance(output, CrewOutput)
    artifact_types = [a["type"] for a in output.artifacts]
    assert "blog_post" in artifact_types
    assert "instagram" in artifact_types
    assert "seo_keywords" in artifact_types   # always included
