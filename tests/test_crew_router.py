import pytest

from crews.base_crew import BaseCrew
from crews.content_creator.crew import ContentCreatorCrew
from crews.product_manager.crew import ProductManagerCrew
from crews.bharat_desha.crew import BharatDeshaCrew
from crews.router import get_crew


def test_content_creator_crew_is_base_crew():
    assert issubclass(ContentCreatorCrew, BaseCrew)


def test_product_manager_crew_is_base_crew():
    assert issubclass(ProductManagerCrew, BaseCrew)


def test_get_crew_returns_correct_types():
    assert isinstance(get_crew("content_creator"), ContentCreatorCrew)
    assert isinstance(get_crew("product_manager"), ProductManagerCrew)
    assert isinstance(get_crew("bharat_desha"), BharatDeshaCrew)


def test_get_crew_unknown_persona_raises():
    with pytest.raises(ValueError, match="Unknown persona"):
        get_crew("unknown")
