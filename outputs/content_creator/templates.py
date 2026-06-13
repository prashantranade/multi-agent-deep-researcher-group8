# outputs/content_creator/templates.py

CONTENT_BRIEF_PROMPT = """Based on this analysis, write a structured content brief:
Analysis: {analysis}

Include:
- Topic overview (2-3 sentences)
- Key angles to cover (3-5 bullet points)
- Target audience profile
- Recommended tone and style
- 3 headline options
- Supporting facts and data points

Format as clean markdown."""

SOCIAL_DRAFT_PROMPT = """Write a social media post (LinkedIn/Instagram) based on this content analysis:
Analysis: {analysis}
Hook to use: {hook}
Tone: {tone}

Write 150-200 words. Start with the hook. Include a call to action."""

CAPTIONS_PROMPT = """Write 3 short social media captions (under 150 characters each) based on:
Analysis: {analysis}
Return as a numbered list."""

HASHTAGS_PROMPT = """Generate 20 relevant hashtags for this content:
Topic: {topic}
Analysis: {analysis}
Mix popular and niche hashtags. Return as space-separated #tags."""

CALENDAR_ENTRY_PROMPT = """Create a content calendar entry:
Analysis: {analysis}
Include: Best posting time, platform recommendation, content type, caption summary, hashtag count needed."""
