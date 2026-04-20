from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class DomainSample:
    text: str
    label: int


@dataclass
class LexicalMatchResult:
    bm25_score: float
    match_ratio: float
    matched_terms: List[str]


@dataclass
class SemanticMatchResult:
    cosine_similarity: float
    semantic_label: int


@dataclass
class DomainDecision:
    in_domain: bool
    probability: float
    lexical: LexicalMatchResult
    semantic: SemanticMatchResult
