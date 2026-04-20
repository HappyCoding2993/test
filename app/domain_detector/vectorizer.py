from __future__ import annotations

import math
from typing import List, Sequence

from app.domain_detector.tokenizer import tokenize


class TfidfVectorizer:
    def __init__(self, corpus: Sequence[str] | None = None, vocab: List[str] | None = None, idf: List[float] | None = None) -> None:
        if vocab is not None and idf is not None:
            self.vocab = vocab
            self.idf = idf
            self.term_to_id = {term: idx for idx, term in enumerate(vocab)}
            return

        if corpus is None:
            raise ValueError("corpus 不能为空")

        corpus_tokens = [tokenize(text) for text in corpus]
        self.vocab = sorted({token for tokens in corpus_tokens for token in tokens})
        self.term_to_id = {term: idx for idx, term in enumerate(self.vocab)}

        n_docs = len(corpus_tokens)
        self.idf = [0.0] * len(self.vocab)
        for term, idx in self.term_to_id.items():
            df = sum(1 for tokens in corpus_tokens if term in tokens)
            self.idf[idx] = math.log((n_docs + 1) / (df + 1)) + 1

    @staticmethod
    def _l2_normalize(vec: List[float]) -> List[float]:
        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0:
            return vec
        return [v / norm for v in vec]

    def transform(self, text: str) -> List[float]:
        tokens = tokenize(text)
        tf = [0.0] * len(self.vocab)
        for token in tokens:
            idx = self.term_to_id.get(token)
            if idx is not None:
                tf[idx] += 1.0

        if tokens:
            token_count = float(len(tokens))
            tf = [value / token_count for value in tf]

        tfidf = [tf[idx] * self.idf[idx] for idx in range(len(self.vocab))]
        return self._l2_normalize(tfidf)


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    # transform() 已完成 L2 归一化，这里直接点积即可
    return sum(a * b for a, b in zip(vec_a, vec_b))
