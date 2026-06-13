# crews/router.py
from crews.base_crew import BaseCrew
from crews.content_creator.crew import ContentCreatorCrew
from crews.product_manager.crew import ProductManagerCrew
from crews.bharat_desha.crew import BharatDeshaCrew

import sys

def get_crew(persona: str) -> BaseCrew:
    _module = sys.modules[__name__]
    _CREW_MAP = {
        "content_creator": _module.ContentCreatorCrew,
        "product_manager": _module.ProductManagerCrew,
        "bharat_desha": _module.BharatDeshaCrew,
    }
    if persona not in _CREW_MAP:
        raise ValueError(f"Unknown persona: '{persona}'. Valid options: {list(_CREW_MAP.keys())}")
    return _CREW_MAP[persona]()
