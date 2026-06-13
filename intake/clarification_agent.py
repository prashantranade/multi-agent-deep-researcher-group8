# intake/clarification_agent.py
from typing import Dict, Optional, Tuple

from crews.base_crew import ResearchBrief

FIELD_ORDER = ["audience", "tone", "depth"]


class ClarificationAgent:
    def get_next_question(
        self, topic: str, persona: str, context_text: Optional[str], answers_so_far: Dict
    ) -> Optional[Tuple[str, str]]:
        """Return the next (field, question) pair, or None when all fields are collected."""
        for field in FIELD_ORDER:
            if field not in answers_so_far:
                return field, self._question_for(field, topic, persona)
        return None

    def _question_for(self, field: str, topic: str, persona: str) -> str:
        persona_label = persona.replace("_", " ")
        questions = {
            "audience": f"Who is the target audience for your research on \"{topic}\"?",
            "tone": f"What tone should this {persona_label} output have? (e.g. inspirational, analytical)",
            "depth": "How deep should the research go? (quick, standard, or deep)",
        }
        return questions[field]

    def build_brief(
        self, topic: str, persona: str, context_text: Optional[str], answers: Dict
    ) -> ResearchBrief:
        return ResearchBrief(
            topic=topic,
            persona=persona,
            audience=answers.get("audience", "general audience"),
            tone=answers.get("tone", "neutral"),
            depth=answers.get("depth", "standard"),
            context_text=context_text,
        )
