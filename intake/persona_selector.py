# intake/persona_selector.py
PERSONAS = {
    "content_creator": {
        "label": "Content Creator",
        "description": "Research and create engaging content for blogs, social media, and newsletters.",
        "artifacts": ["blog_post", "social_post", "newsletter", "content_brief"],
        "always_included": [],
    },
    "product_manager": {
        "label": "Product Manager",
        "description": "Competitive research, market analysis, and product strategy documents.",
        "artifacts": ["competitive_analysis", "product_roadmap", "user_research", "executive_summary"],
        "always_included": [],
    },
    "bharat_desha": {
        "label": "Bharat Desha",
        "description": "Spiritual India travel content — itineraries, destination guides, Sanatan Dharma philosophy, yoga & wellness, and social media repurposing.",
        "artifacts": [
            "blog_post",
            "itinerary",
            "destination_guide",
            "wellness_guide",
            "instagram",
            "facebook",
            "x_post",
            "youtube",
        ],
        "always_included": ["seo_keywords"],
    },
}
