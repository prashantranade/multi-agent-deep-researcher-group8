# tests/test_pm_agents.py
from unittest.mock import patch
from crews.product_manager.analysis_agent import PMAnalysisAgent
from crews.product_manager.output_agent import PMOutputAgent


def test_pm_analysis_returns_dict():
    with patch("crews.product_manager.analysis_agent.chat_with_fallback") as mock_llm:
        mock_llm.return_value = '{"market_size": "large", "competitors": ["A", "B"], "user_pain_points": ["cost"], "opportunity": "high", "contradictions": [], "key_data_points": []}'
        agent = PMAnalysisAgent()
        result = agent.analyse([{"text": "market data here", "metadata": {}}])
    assert "market_size" in result
    assert "competitors" in result
    assert result["market_size"] == "large"
    assert "A" in result["competitors"]


def test_pm_analysis_handles_invalid_json():
    with patch("crews.product_manager.analysis_agent.chat_with_fallback") as mock_llm:
        mock_llm.return_value = "Not valid JSON — just a narrative summary"
        agent = PMAnalysisAgent()
        result = agent.analyse([{"text": "some research", "metadata": {}}])
    assert "market_size" in result
    assert result["competitors"] == []
    assert "Not valid JSON" in result["opportunity"]


def test_pm_analysis_handles_fenced_json():
    with patch("crews.product_manager.analysis_agent.chat_with_fallback") as mock_llm:
        mock_llm.return_value = '```json\n{"market_size": "large", "competitors": ["X"], "user_pain_points": ["price"], "opportunity": "high", "contradictions": [], "key_data_points": []}\n```'
        agent = PMAnalysisAgent()
        result = agent.analyse([{"text": "market data", "metadata": {}}])
    assert result["market_size"] == "large"
    assert result["competitors"] == ["X"]
    assert result["opportunity"] == "high"


def test_pm_output_generates_selected_artifacts():
    with patch("crews.product_manager.output_agent.chat_with_fallback") as mock_llm:
        mock_llm.return_value = "Generated PM content"
        agent = PMOutputAgent()
        analysis = {
            "market_size": "large",
            "competitors": ["A"],
            "user_pain_points": ["cost"],
            "opportunity": "high",
            "contradictions": [],
        }
        artifacts = agent.generate_artifacts(analysis, selected_artifacts=["research_brief"])
    assert len(artifacts) == 1
    assert artifacts[0]["type"] == "research_brief"
    assert artifacts[0]["content"] == "Generated PM content"
    assert artifacts[0]["citations"] == []


def test_pm_output_only_generates_selected():
    with patch("crews.product_manager.output_agent.chat_with_fallback") as mock_llm:
        mock_llm.return_value = "Generated"
        agent = PMOutputAgent()
        analysis = {"market_size": "unknown", "competitors": [], "user_pain_points": [], "opportunity": "", "contradictions": []}
        artifacts = agent.generate_artifacts(analysis, selected_artifacts=["competitive_summary", "prd_insights"])
    types = [a["type"] for a in artifacts]
    assert "competitive_summary" in types
    assert "prd_insights" in types
    assert "research_brief" not in types
    assert "opportunity_sizing" not in types
    assert len(artifacts) == 2


def test_pm_output_uses_json_formatted_analysis():
    with patch("crews.product_manager.output_agent.chat_with_fallback") as mock_llm:
        mock_llm.return_value = "Generated"
        agent = PMOutputAgent()
        analysis = {"market_size": "large", "competitors": ["A"]}
        agent.generate_artifacts(analysis, selected_artifacts=["research_brief"])
        prompt = mock_llm.call_args[1]["messages"][0]["content"]
        assert '"market_size": "large"' in prompt
        assert '"competitors"' in prompt


def test_pm_output_skips_unknown_artifact_types():
    with patch("crews.product_manager.output_agent.chat_with_fallback") as mock_llm:
        mock_llm.return_value = "Generated"
        agent = PMOutputAgent()
        analysis = {"market_size": "unknown", "competitors": [], "user_pain_points": [], "opportunity": "", "contradictions": []}
        artifacts = agent.generate_artifacts(analysis, selected_artifacts=["research_brief", "nonexistent_type"])
    types = [a["type"] for a in artifacts]
    assert "research_brief" in types
    assert "nonexistent_type" not in types
    assert len(artifacts) == 1
