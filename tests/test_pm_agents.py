# tests/test_pm_agents.py
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from crews.product_manager.analysis_agent import PMAnalysisAgent
from crews.product_manager.output_agent import PMOutputAgent


def test_pm_analysis_returns_dict():
    with patch("crews.product_manager.analysis_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content='{"market_size": "large", "competitors": ["A", "B"], "user_pain_points": ["cost"], "opportunity": "high", "contradictions": [], "key_data_points": []}')
        mock_get_llm.return_value = mock_llm
        agent = PMAnalysisAgent()
        result = agent.analyse([{"text": "market data here", "metadata": {}}])
    assert "market_size" in result
    assert "competitors" in result
    assert result["market_size"] == "large"
    assert "A" in result["competitors"]


def test_pm_analysis_handles_invalid_json():
    with patch("crews.product_manager.analysis_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Not valid JSON — just a narrative summary")
        mock_get_llm.return_value = mock_llm
        agent = PMAnalysisAgent()
        result = agent.analyse([{"text": "some research", "metadata": {}}])
    assert "market_size" in result
    assert result["competitors"] == []
    assert "Not valid JSON" in result["opportunity"]


def test_pm_analysis_handles_fenced_json():
    with patch("crews.product_manager.analysis_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content='```json\n{"market_size": "large", "competitors": ["X"], "user_pain_points": ["price"], "opportunity": "high", "contradictions": [], "key_data_points": []}\n```')
        mock_get_llm.return_value = mock_llm
        agent = PMAnalysisAgent()
        result = agent.analyse([{"text": "market data", "metadata": {}}])
    assert result["market_size"] == "large"
    assert result["competitors"] == ["X"]
    assert result["opportunity"] == "high"


def test_pm_output_generates_selected_artifacts():
    with patch("crews.product_manager.output_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Generated PM content")
        mock_get_llm.return_value = mock_llm
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
    with patch("crews.product_manager.output_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Generated")
        mock_get_llm.return_value = mock_llm
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
    with patch("crews.product_manager.output_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Generated")
        mock_get_llm.return_value = mock_llm
        agent = PMOutputAgent()
        analysis = {"market_size": "large", "competitors": ["A"]}
        agent.generate_artifacts(analysis, selected_artifacts=["research_brief"])
        # inspect first element (HumanMessage) in call_args
        messages = mock_llm.invoke.call_args[0][0]
        prompt = messages[0].content
        assert '"market_size": "large"' in prompt
        assert '"competitors"' in prompt


def test_pm_output_skips_unknown_artifact_types():
    with patch("crews.product_manager.output_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Generated")
        mock_get_llm.return_value = mock_llm
        agent = PMOutputAgent()
        analysis = {"market_size": "unknown", "competitors": [], "user_pain_points": [], "opportunity": "", "contradictions": []}
        artifacts = agent.generate_artifacts(analysis, selected_artifacts=["research_brief", "nonexistent_type"])
    types = [a["type"] for a in artifacts]
    assert "research_brief" in types
    assert "nonexistent_type" not in types
    assert len(artifacts) == 1

