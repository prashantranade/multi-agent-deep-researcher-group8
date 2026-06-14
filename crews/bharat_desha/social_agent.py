from typing import List, Dict
from langchain_core.messages import HumanMessage
from infrastructure.llm_client import get_llm
import config

_PLATFORM_PROMPTS = {
    "instagram": """Write an Instagram caption for BharatDesha (spiritual India travel).
- 150-220 words, warm and evocative tone
- End with exactly 15 hashtags on a new line (mix broad India travel + niche spiritual tags)
- Include the primary keyword naturally""",

    "facebook": """Write a Facebook post for BharatDesha (spiritual India travel).
- 100-150 words, informative and engaging
- Follow with 2 sentences of link preview text (label it "Link preview:")
- Include the primary keyword naturally""",

    "x_post": """Write an X (Twitter) thread for BharatDesha (spiritual India travel).
- 5 tweets, each under 280 characters
- Number each tweet (1/5, 2/5, etc.)
- First tweet must hook attention and include the primary keyword
- Last tweet ends with a call to action""",

    "youtube": """Write YouTube metadata for BharatDesha (spiritual India travel).
- Title: under 70 characters, primary keyword first
- Description: 300 words, first 2 sentences hook viewers, includes keywords naturally
- 5 chapter suggestions with placeholder timestamps (e.g. 0:00 Introduction)
Format as:
TITLE: ...
DESCRIPTION: ...
CHAPTERS:
0:00 ...""",
}

def run_social_agent(primary_artifact: Dict, key_points: List[str], seo_context: dict, platforms: List[str]) -> List[Dict]:
    primary_keyword = seo_context.get("primary_keyword", "")
    points_summary = "\n".join(f"- {p}" for p in key_points)
    content_snippet = primary_artifact["content"][:600]

    artifacts = []
    for platform in platforms:
        platform_instruction = _PLATFORM_PROMPTS.get(platform, _PLATFORM_PROMPTS["instagram"])

        prompt = f"""{platform_instruction}

Primary keyword: {primary_keyword}
Key points from the article:
{points_summary}

Article excerpt:
{content_snippet}

Write the content now."""

        llm = get_llm(config.OUTPUT_MODEL)
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content
        artifacts.append({"type": platform, "content": content})

    return artifacts

