# crews/router.py
from crews.base_crew import BaseCrew
from crews.content_creator.crew import ContentCreatorCrew
from crews.product_manager.crew import ProductManagerCrew
from crews.bharat_desha.crew import BharatDeshaCrew

def get_crew(persona: str) -> BaseCrew:
    _CREW_MAP = {
        "content_creator": ContentCreatorCrew,
        "product_manager": ProductManagerCrew,
        "bharat_desha": BharatDeshaCrew,
    }
    if persona not in _CREW_MAP:
        raise ValueError(f"Unknown persona: '{persona}'. Valid options: {list(_CREW_MAP.keys())}")
    return _CREW_MAP[persona]()
