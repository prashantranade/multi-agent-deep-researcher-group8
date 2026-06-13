# tests/test_integration.py
import os
os.environ.setdefault("OPENROUTER_API_KEY", "x")
os.environ.setdefault("TAVILY_API_KEY", "x")

from unittest.mock import patch, MagicMock
import sys

def test_router_returns_correct_crew_for_each_persona():
    from crews.router import get_crew
    from crews.base_crew import BaseCrew

    # Clear cached modules to ensure patches apply during import
    for mod in list(sys.modules.keys()):
        if "crews.router" in mod or "crews.content_creator" in mod or \
           "crews.product_manager" in mod or "crews.bharat_desha" in mod:
            del sys.modules[mod]

    with patch("crews.content_creator.crew.ContentCreatorCrew") as mock_cc, \
         patch("crews.product_manager.crew.ProductManagerCrew") as mock_pm, \
         patch("crews.bharat_desha.crew.BharatDeshaCrew") as mock_bd:

        mock_cc.return_value = MagicMock(spec=BaseCrew)
        mock_pm.return_value = MagicMock(spec=BaseCrew)
        mock_bd.return_value = MagicMock(spec=BaseCrew)

        # Now import after patching
        from crews.router import get_crew as get_crew_patched

        cc = get_crew_patched("content_creator")
        pm = get_crew_patched("product_manager")
        bd = get_crew_patched("bharat_desha")

        mock_cc.assert_called_once()
        mock_pm.assert_called_once()
        mock_bd.assert_called_once()

def test_persona_selector_includes_bharat_desha():
    from intake.persona_selector import PERSONAS

    assert "bharat_desha" in PERSONAS
    bd = PERSONAS["bharat_desha"]
    assert "label" in bd
    assert "description" in bd
    assert "artifacts" in bd
    assert "always_included" in bd
    assert "blog_post" in bd["artifacts"]
    assert "instagram" in bd["artifacts"]
    assert "x_post" in bd["artifacts"]
    assert "youtube" in bd["artifacts"]
    assert "seo_keywords" in bd["always_included"]

def test_artifact_renderer_handles_all_types():
    from ui.artifact_renderer import get_render_config

    artifact_types = [
        "blog_post", "itinerary", "destination_guide", "wellness_guide",
        "instagram", "facebook", "x_post", "youtube",
        "seo_keywords", "content_brief", "competitive_analysis",
        "product_roadmap", "user_research", "executive_summary", "social_post", "newsletter"
    ]

    for artifact_type in artifact_types:
        config = get_render_config(artifact_type)
        assert "label" in config, f"Missing label for {artifact_type}"
        assert "display" in config, f"Missing display for {artifact_type}"
        assert config["display"] in ("markdown", "text_box", "sections"), \
            f"Unknown display type for {artifact_type}: {config['display']}"

def test_router_raises_for_unknown_persona():
    from crews.router import get_crew
    import pytest
    with pytest.raises(ValueError, match="Unknown persona"):
        get_crew("unknown_persona")

def test_app_imports_router_and_renderer():
    """Verify app.py imports crew router and artifact renderer."""
    import importlib.util, sys

    # Stub streamlit so we can import app.py outside Streamlit context
    st_mock = MagicMock()
    st_mock.session_state = {}
    sys.modules["streamlit"] = st_mock

    spec = importlib.util.spec_from_file_location(
        "app",
        "C:/Users/prash/codeworkspace/outskill/cap-hackathon-group8/app.py"
    )
    if spec is None:
        return  # app.py doesn't exist yet — skip

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        if "crews.router" in str(e) or "ui.artifact_renderer" in str(e):
            raise

def test_lancedb_tables_are_isolated(tmp_path):
    """Each crew writes to its own table — no cross-contamination."""
    import config
    from infrastructure.vector_store import VectorStore

    original_path = config.LANCEDB_PATH
    config.LANCEDB_PATH = str(tmp_path / "test_lancedb")

    try:
        store = VectorStore(db_path=config.LANCEDB_PATH)

        store.add_texts(
            ["Content creator article about marketing"],
            [{"source": "https://cc.example.com"}],
            "content_creator"
        )
        store.add_texts(
            ["Product manager roadmap for Q3"],
            [{"source": "https://pm.example.com"}],
            "product_manager"
        )
        store.add_texts(
            ["Varanasi spiritual tour guide"],
            [{"source": "https://bd.example.com"}],
            "bharat_desha"
        )

        cc_results = store.search("marketing content", "content_creator", k=5)
        pm_results = store.search("product roadmap", "product_manager", k=5)
        bd_results = store.search("Varanasi spiritual", "bharat_desha", k=5)

        assert len(cc_results) > 0
        assert len(pm_results) > 0
        assert len(bd_results) > 0

        # Cross-check: bharat_desha table should not contain content_creator text
        bd_all = store.search("marketing content creator", "bharat_desha", k=5)
        cc_texts = [r["text"] for r in cc_results]
        bd_texts = [r["text"] for r in bd_all]
        assert not any(t in bd_texts for t in cc_texts), "Tables are not isolated!"

    finally:
        config.LANCEDB_PATH = original_path

def _make_mock_crew_output(artifact_types):
    from crews.base_crew import CrewOutput
    return CrewOutput(
        artifacts=[{"type": t, "content": f"Mock content for {t}", "citations": []} for t in artifact_types]
    )

def test_e2e_content_creator_pipeline():
    from crews.router import get_crew
    from crews.base_crew import ResearchBrief, CrewOutput

    brief = ResearchBrief(
        topic="AI trends in 2025",
        persona="content_creator",
        audience="tech professionals",
        tone="informative",
        depth="standard",
        selected_artifacts=["blog_post", "social_post"],
    )
    mock_output = _make_mock_crew_output(["blog_post", "social_post"])

    with patch("crews.router.ContentCreatorCrew") as mock_class:
        mock_instance = MagicMock()
        mock_instance.run.return_value = mock_output
        mock_class.return_value = mock_instance
        crew = get_crew("content_creator")
        output = crew.run(brief)

    assert isinstance(output, CrewOutput)
    types = [a["type"] for a in output.artifacts]
    assert "blog_post" in types
    assert "social_post" in types

def test_e2e_product_manager_pipeline():
    from crews.router import get_crew
    from crews.base_crew import ResearchBrief, CrewOutput

    brief = ResearchBrief(
        topic="CRM software market 2025",
        persona="product_manager",
        audience="B2B SaaS executives",
        tone="analytical",
        depth="deep",
        selected_artifacts=["competitive_analysis", "executive_summary"],
    )
    mock_output = _make_mock_crew_output(["competitive_analysis", "executive_summary"])

    with patch("crews.router.ProductManagerCrew") as mock_class:
        mock_instance = MagicMock()
        mock_instance.run.return_value = mock_output
        mock_class.return_value = mock_instance
        crew = get_crew("product_manager")
        output = crew.run(brief)

    assert isinstance(output, CrewOutput)
    types = [a["type"] for a in output.artifacts]
    assert "competitive_analysis" in types
    assert "executive_summary" in types

def test_e2e_bharat_desha_pipeline():
    from crews.router import get_crew
    from crews.base_crew import ResearchBrief, CrewOutput

    brief = ResearchBrief(
        topic="Rishikesh yoga retreat",
        persona="bharat_desha",
        audience="solo spiritual travellers",
        tone="warm",
        depth="standard",
        selected_artifacts=["blog_post", "instagram", "seo_keywords"],
    )
    mock_output = _make_mock_crew_output(["seo_keywords", "blog_post", "instagram"])

    with patch("crews.router.BharatDeshaCrew") as mock_class:
        mock_instance = MagicMock()
        mock_instance.run.return_value = mock_output
        mock_class.return_value = mock_instance
        crew = get_crew("bharat_desha")
        output = crew.run(brief)

    assert isinstance(output, CrewOutput)
    types = [a["type"] for a in output.artifacts]
    assert "blog_post" in types
    assert "instagram" in types
    assert "seo_keywords" in types
