# intake/clarification_agent.py
import json
from typing import Dict, Optional
from infrastructure.llm_client import chat_with_fallback
from crews.base_crew import ResearchBrief
import config

_SYSTEM_PROMPT = """You are a research intake assistant. Your job is to understand what a user needs to research and build a clear research brief.
Ask targeted questions one at a time. If context is provided (e.g. website content, social handle), use it to infer answers and skip those questions.
Always respond with valid JSON only."""

class ClarificationAgent:
    def __init__(self, model: str = None):
        self.model = model or config.INTAKE_MODEL

    def get_next_question(
        self, topic: str, persona: str, context_text: Optional[str], answers_so_far: Dict
    ) -> Optional[str]:
        context_block = f"\nContext already provided:\n{context_text[:500]}" if context_text else ""
        answers_block = f"\nAnswers collected so far: {json.dumps(answers_so_far)}" if answers_so_far else ""
        needed = [q for q in ["audience", "tone", "depth"] if q not in answers_so_far]
        if not needed:
            return None
        prompt = f"""Topic: {topic}\nPersona: {persona}{context_block}{answers_block}
Next question to ask (return ONLY a plain string, one question):
Still needed: {needed}
If context already answers any of these, skip them and return null."""
        content = chat_with_fallback(
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        ).strip()
        if content.lower() in ("null", "none", ""):
            return None
        return content.strip('"').strip("'")

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
