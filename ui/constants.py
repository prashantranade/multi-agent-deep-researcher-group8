PHASES = [
    (1, "Persona"),
    (2, "Topic"),
    (3, "Context"),
    (4, "Clarify"),
    (5, "Sources"),
    (6, "Outputs"),
    (7, "Deliverables"),
]

PERSONAS = [
    {
        "key": "content_creator",
        "title": "Content creator",
        "promise": "Hooks, captions, and social-ready drafts from curated sources",
    },
    {
        "key": "product_manager",
        "title": "Product manager",
        "promise": "Market signals, competition, and PRD-ready insights",
    },
    {
        "key": "bharat_desha",
        "title": "Bharat Desha",
        "promise": "SEO travel content with trend and keyword intelligence",
    },
]

ARTIFACT_OPTIONS = {
    "content_creator": [
        ("content_brief", "Content brief"),
        ("social_draft", "Social draft"),
        ("captions", "Captions"),
        ("hashtags", "Hashtags"),
        ("calendar_entry", "Calendar entry"),
    ],
    "product_manager": [
        ("research_brief", "Research brief"),
        ("competitive_summary", "Competitive summary"),
        ("opportunity_sizing", "Opportunity sizing"),
        ("prd_insights", "PRD insights"),
    ],
    "bharat_desha": [
        ("blog_post", "Blog post"),
        ("itinerary", "Itinerary"),
        ("destination_guide", "Destination guide"),
        ("wellness_guide", "Wellness guide"),
        ("instagram", "Instagram"),
        ("facebook", "Facebook"),
        ("x_post", "X post"),
        ("youtube", "YouTube"),
    ],
}

PIPELINES = {
    "content_creator": ["Retrieve", "Analyse", "Generate"],
    "product_manager": ["Retrieve", "Analyse", "Generate"],
    "bharat_desha": ["Trend", "SEO", "Retrieve", "Analyse", "Generate"],
}

PERSONA_LABELS = {p["key"]: p["title"] for p in PERSONAS}

CLARIFY_FIELDS = ["audience", "tone", "depth"]
