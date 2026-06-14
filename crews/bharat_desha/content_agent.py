from typing import Dict
from langchain_core.messages import HumanMessage
from infrastructure.llm_client import get_llm
import config

_ARTIFACT_INSTRUCTIONS = {
    "blog_post": "Write an 800-1500 word SEO-optimised blog post with H2/H3 headings. Include the primary keyword in the title and opening paragraph.",
    "itinerary": "Write a day-by-day travel itinerary with timings, transport options, accommodation suggestions, and spiritual stops. Be specific and practical.",
    "destination_guide": "Write a comprehensive destination guide structured by theme: Getting There, Spiritual Highlights, Cultural Experiences, Practical Tips, Best Time to Visit.",
    "wellness_guide": "Write a wellness-focused guide covering yoga retreats, meditation centres, sound healing, Ayurveda treatments, and ashram stays. Include pricing where possible.",
}

def run_content_agent(analysis: Dict, seo_context: dict, artifact_type: str, tone: str, depth: str) -> Dict:
    keywords = ", ".join(k["keyword"] for k in seo_context.get("keywords", []))
    primary_keyword = seo_context.get("primary_keyword", "")
    instruction = _ARTIFACT_INSTRUCTIONS.get(artifact_type, _ARTIFACT_INSTRUCTIONS["blog_post"])

    prompt = f"""You are a content writer for BharatDesha, a spiritual India travel platform.
Tone: {tone}. Depth: {depth}.

{instruction}

Weave these SEO keywords naturally throughout the content: {keywords}
Primary keyword "{primary_keyword}" must appear in the first 100 words.

Research summary:
- Spiritual: {analysis["spiritual"]}
- Practical: {analysis["practical"]}
- Cultural: {analysis["cultural"]}
- Wellness: {analysis["wellness"]}
- Seasonal: {analysis["seasonal"]}
- Key points: {", ".join(analysis["key_points"])}

Write the content now. Use markdown formatting."""

    llm = get_llm(config.OUTPUT_MODEL)
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content

    return {
        "type": artifact_type,
        "content": content,
        "citations": analysis.get("citations", []),
    }

