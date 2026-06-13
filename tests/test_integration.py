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
