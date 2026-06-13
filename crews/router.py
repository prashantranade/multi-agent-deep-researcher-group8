from crews.base_crew import BaseCrew


def get_crew(persona: str, **kwargs) -> BaseCrew:
    if persona == "content_creator":
        from crews.content_creator.crew import ContentCreatorCrew
        return ContentCreatorCrew(**kwargs)
    if persona == "product_manager":
        from crews.product_manager.crew import ProductManagerCrew
        return ProductManagerCrew(**kwargs)
    if persona == "bharat_desha":
        from crews.bharat_desha.crew import BharatDeshaCrew
        return BharatDeshaCrew()
    raise ValueError(f"Unknown persona: {persona}")
