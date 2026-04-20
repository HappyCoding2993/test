from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple

from app.domain_detector.tokenizer import tokenize
from app.domain_detector.types import LexicalMatchResult


class InMemoryESBM25:
    def __init__(self, docs: Sequence[str], k1: float, b: float) -> None:
        self.docs = list(docs)
        self.k1 = k1
        self.b = b
        self.doc_tokens = [tokenize(doc) for doc in self.docs]
        self.avgdl = sum(len(tokens) for tokens in self.doc_tokens) / max(len(self.doc_tokens), 1)

        self.doc_freq: Dict[str, int] = {}
        for tokens in self.doc_tokens:
            for term in set(tokens):
                self.doc_freq[term] = self.doc_freq.get(term, 0) + 1

        self.inverted_index: Dict[str, List[Tuple[int, int]]] = {}
        for doc_id, tokens in enumerate(self.doc_tokens):
            freq: Dict[str, int] = {}
            for term in tokens:
                freq[term] = freq.get(term, 0) + 1
            for term, count in freq.items():
                self.inverted_index.setdefault(term, []).append((doc_id, count))

    def _idf(self, term: str) -> float:
        n_docs = len(self.docs)
        df = self.doc_freq.get(term, 0)
        return math.log((n_docs - df + 0.5) / (df + 0.5) + 1)

    def search(self, query: str) -> LexicalMatchResult:
        q_tokens = tokenize(query)
        if not q_tokens:
            return LexicalMatchResult(0.0, 0.0, [])

        matched_terms = [term for term in set(q_tokens) if term in self.inverted_index]
        match_ratio = len(matched_terms) / len(set(q_tokens))

        best_score = 0.0
        for doc_tokens in self.doc_tokens:
            dl = len(doc_tokens)
            term_freq: Dict[str, int] = {}
            for term in doc_tokens:
                term_freq[term] = term_freq.get(term, 0) + 1

            score = 0.0
            for term in q_tokens:
                f = term_freq.get(term, 0)
                if f == 0:
                    continue
                idf = self._idf(term)
                numerator = f * (self.k1 + 1)
                denominator = f + self.k1 * (1 - self.b + self.b * dl / max(self.avgdl, 1e-9))
                score += idf * (numerator / denominator)
            best_score = max(best_score, score)

        return LexicalMatchResult(best_score, match_ratio, matched_terms)
