# crews/content_creator/output_agent.py
from typing import List, Dict, Any
from infrastructure.llm_client import chat_with_fallback
from outputs.content_creator.templates import (
    CONTENT_BRIEF_PROMPT,
    SOCIAL_DRAFT_PROMPT,
    CAPTIONS_PROMPT,
    HASHTAGS_PROMPT,
    CALENDAR_ENTRY_PROMPT,
)
import config


class CCOutputAgent:
    def _generate(self, prompt: str) -> str:
        return chat_with_fallback([{"role": "user", "content": prompt}], model=config.OUTPUT_MODEL)

    def generate_artifacts(
        self, analysis: Dict[str, Any], selected_artifacts: List[str]
    ) -> List[Dict[str, Any]]:
        hook = analysis.get("hooks", [""])[0] if analysis.get("hooks") else ""
        tone = analysis.get("tone_notes", "informative")
        artifacts = []
        generators = {
            "content_brief": lambda: self._generate(CONTENT_BRIEF_PROMPT.format(analysis=analysis)),
            "social_draft": lambda: self._generate(
                SOCIAL_DRAFT_PROMPT.format(analysis=analysis, hook=hook, tone=tone)
            ),
            "captions": lambda: self._generate(CAPTIONS_PROMPT.format(analysis=analysis)),
            "hashtags": lambda: self._generate(
                HASHTAGS_PROMPT.format(topic=analysis.get("trends", [""])[0], analysis=analysis)
            ),
            "calendar_entry": lambda: self._generate(CALENDAR_ENTRY_PROMPT.format(analysis=analysis)),
        }
        for artifact_type in selected_artifacts:
            if artifact_type in generators:
                content = generators[artifact_type]()
                artifacts.append({"type": artifact_type, "content": content, "citations": []})
        return artifacts
