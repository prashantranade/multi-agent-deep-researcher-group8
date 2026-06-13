# outputs/product_manager/templates.py

RESEARCH_BRIEF_PROMPT = """Write a structured research brief for a product manager based on:
Analysis: {analysis}

Include:
- Executive summary (3 sentences)
- Key findings (5 bullet points with data)
- Market landscape
- Identified gaps and opportunities
- Recommended next steps

Format as clean markdown with headers."""

COMPETITIVE_SUMMARY_PROMPT = """Write a competitive landscape summary based on:
Analysis: {analysis}

Include for each competitor: positioning, strengths, weaknesses, market share if known.
Format as a markdown table followed by 3 strategic insights."""

OPPORTUNITY_SIZING_PROMPT = """Write an opportunity sizing analysis based on:
Analysis: {analysis}

Include: TAM/SAM/SOM estimates (with caveats), growth rate, key assumptions, confidence level."""

PRD_INSIGHTS_PROMPT = """Extract PRD-ready insights from:
Analysis: {analysis}

Format as:
## User Problems
- Problem: [description] | Evidence: [source]

## Opportunity Statement
[One paragraph]

## Success Metrics
- [Metric]: [target]"""
