# crews/base_crew.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ResearchBrief:
    topic: str
    persona: str                        # "content_creator" | "product_manager"
    audience: str
    tone: str
    depth: str                          # "quick" | "standard" | "deep"
    context_text: Optional[str] = None  # from uploaded docs / URL / social handle
    selected_sources: List[Dict] = field(default_factory=list)
    selected_artifacts: List[str] = field(default_factory=list)

@dataclass
class CrewOutput:
    artifacts: List[Dict[str, Any]]     # [{"type": str, "content": str, "citations": List}]
    trace_id: Optional[str] = None
    notes: List[str] = field(default_factory=list)

class BaseCrew(ABC):
    """
    All persona crews implement this interface.
    Adding a new persona = subclass BaseCrew, implement three methods, done.
    """

    @abstractmethod
    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        """Retrieve and chunk content from selected sources into the vector store."""
        ...

    @abstractmethod
    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse retrieved content through a persona-specific lens."""
        ...

    @abstractmethod
    def generate_artifacts(
        self, analysis: Dict[str, Any], selected_artifacts: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate only the selected artifact types from the analysis."""
        ...

    def run(self, brief: ResearchBrief) -> CrewOutput:
        retrieved = self.retrieve(brief, brief.selected_sources)
        analysis = self.analyse(retrieved)
        artifacts = self.generate_artifacts(analysis, brief.selected_artifacts)
        return CrewOutput(artifacts=artifacts)
