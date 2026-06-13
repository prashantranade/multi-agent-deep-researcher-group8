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

def test_router_raises_for_unknown_persona():
    from crews.router import get_crew
    import pytest
    with pytest.raises(ValueError, match="Unknown persona"):
        get_crew("unknown_persona")
