from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AnalysisResult:
    similarity: float
    coverage: float
    score: float
    issues: List[str]
    missing: List[str]
    suggestions: List[str]
    sections: Dict[str, bool]

@dataclass
class ProfessionProfile:
    name: str
    display_name: str
    keywords: List[str]
    technologies: List[str]
    description: str
