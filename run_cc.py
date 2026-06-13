#!/usr/bin/env python3
"""Run Content Creator crew from the command line."""

from crews.base_crew import ResearchBrief
from crews.content_creator.retrieval_agent import CCRetrievalAgent
from crews.content_creator.analysis_agent import CCAnalysisAgent
from crews.content_creator.output_agent import CCOutputAgent
from infrastructure.artifact_exporter import export_artifact

# ── EDIT THESE ──────────────────────────────────────────────
# TOPIC = "Sustainable travel in Rajasthan for millennials"
# AUDIENCE = "millennials"
# TONE = "inspirational"
# CONTEXT = "Social media creator handle: @bharatdesha. Inspirational India travel content."

# SOURCES = [
#     {
#         "url": "https://www.lonelyplanet.com/articles/sustainable-travel",
#         "title": "Sustainable Travel",
#         "domain": "lonelyplanet.com",
#         "date": "2025-01-01",
#     },
# ]

# ARTIFACTS = ["content_brief", "captions", "hashtags"]


HANDLE = "VaibhavSisinty"  # without @

TOPIC = "How to grow money with AI"
AUDIENCE = "AI influencers"
TONE = "motivational , inspirational"

CONTEXT = f"""Social context:
Twitter/X handle: @{HANDLE}
Profile: https://x.com/{HANDLE}
Creator niche: founder
Typical content: artifical intelligence, startups, entrepreneurship
Voice/style: motivational, inspirational
Recent themes: artifical intelligence, startups, entrepreneurship
Generate content that fits this creator's brand and audience."""

SOURCES = [
    # # Research about the TOPIC (required — scraper works on normal sites)
    # {
    #     "url": "https://en.wikipedia.org/wiki/<relevant-topic>",
    #     "title": "...",
    #     "domain": "wikipedia.org",
    #     "date": "2025-01-01",
    # },
    # # Optional: creator's website / newsletter / link-in-bio (not x.com)
    # {
    #     "url": "https://creator-website.com/about",
    #     "title": "About creator",
    #     "domain": "creator-website.com",
    #     "date": "2025-01-01",
    # },
]

ARTIFACTS = ["content_brief", "captions", "hashtags", "social_draft"]
# ─────────────────────────────────────────────────────────────

def main():
    brief = ResearchBrief(
        topic=TOPIC,
        persona="content_creator",
        audience=AUDIENCE,
        tone=TONE,
        depth="standard",
        context_text=CONTEXT or None,
        selected_sources=SOURCES,
        selected_artifacts=ARTIFACTS,
    )

    retrieval = CCRetrievalAgent()
    analysis = CCAnalysisAgent()
    output = CCOutputAgent()

    print("Step 1/3: Retrieving...")
    retrieved = retrieval.retrieve(brief, brief.selected_sources)
    print(f"  → {len(retrieved)} chunks retrieved")

    print("Step 2/3: Analyzing...")
    analysed = analysis.analyse(retrieved)
    print(f"  → trends: {analysed.get('trends', [])}")
    print(f"  → hooks: {analysed.get('hooks', [])}")

    print("Step 3/3: Generating artifacts...")
    artifacts = output.generate_artifacts(analysed, brief.selected_artifacts)

    for artifact in artifacts:
        print("\n" + "=" * 60)
        print(artifact["type"].replace("_", " ").upper())
        print("=" * 60)
        print(export_artifact(artifact))

if __name__ == "__main__":
    main()