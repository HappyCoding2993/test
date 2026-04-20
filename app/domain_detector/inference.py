from __future__ import annotations

from pathlib import Path

from app.domain_detector.models import FusionBinaryNeuralNet, SemanticBinaryClassifier
from app.domain_detector.retrieval import InMemoryESBM25
from app.domain_detector.serialization import load_config, load_weights
from app.domain_detector.types import DomainDecision, SemanticMatchResult
from app.domain_detector.vectorizer import TfidfVectorizer, cosine_similarity


class CoreNetworkExperienceDomainDetector:
    def __init__(self, config_path: Path, model_path: Path) -> None:
        config = load_config(config_path)
        weights = load_weights(model_path)

        vectorizer_idf = weights.vectorizer_idf
        fusion_mlp = weights.fusion_mlp

        self.threshold = config.threshold
        self.vectorizer = TfidfVectorizer(vocab=config.vocab, idf=config.idf)
        self.lexical_retriever = InMemoryESBM25(
            vectorizer_idf["domain_docs"],
            k1=config.bm25_k1,
            b=config.bm25_b,
        )
        self.domain_prototype = vectorizer_idf["domain_prototype"]
        self.semantic_classifier = SemanticBinaryClassifier(
            weights=vectorizer_idf["semantic_weights"],
            bias=vectorizer_idf["semantic_bias"],
        )
        self.fusion_model = FusionBinaryNeuralNet(
            hidden_dim=config.fusion_hidden_dim,
            w1=fusion_mlp["w1"],
            b1=fusion_mlp["b1"],
            w2=fusion_mlp["w2"],
            b2=fusion_mlp["b2"],
        )

    def analyze(self, user_query: str, threshold: float | None = None) -> DomainDecision:
        actual_threshold = self.threshold if threshold is None else threshold

        lexical = self.lexical_retriever.search(user_query)
        vector = self.vectorizer.transform(user_query)
        cosine = cosine_similarity(vector, self.domain_prototype)
        semantic_label = self.semantic_classifier.predict_label([cosine, lexical.match_ratio], actual_threshold)

        features = [lexical.bm25_score, lexical.match_ratio, cosine, float(semantic_label)]
        probability = self.fusion_model.predict_proba(features)

        return DomainDecision(
            in_domain=probability >= actual_threshold,
            probability=probability,
            lexical=lexical,
            semantic=SemanticMatchResult(cosine_similarity=cosine, semantic_label=semantic_label),
        )
