from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from app.domain_detector.config import TrainingConfig
from app.domain_detector.models import FusionBinaryNeuralNet, SemanticBinaryClassifier
from app.domain_detector.retrieval import InMemoryESBM25
from app.domain_detector.serialization import DetectorConfig, DetectorWeights, save_config, save_weights
from app.domain_detector.types import DomainSample
from app.domain_detector.vectorizer import TfidfVectorizer, cosine_similarity


class DomainDetectorTrainer:
    def __init__(self, domain_docs: Sequence[str], semantic_samples: Sequence[DomainSample], fusion_samples: Sequence[DomainSample], config: Dict | None = None) -> None:
        self.domain_docs = list(domain_docs)
        self.semantic_samples = list(semantic_samples)
        self.fusion_samples = list(fusion_samples)
        self.config = TrainingConfig.from_dict(config)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _mean_vector(vectors: List[List[float]]) -> List[float]:
        dim = len(vectors[0])
        result = [0.0] * dim
        for vec in vectors:
            for idx, value in enumerate(vec):
                result[idx] += value
        avg = [value / len(vectors) for value in result]
        norm = sum(v * v for v in avg) ** 0.5
        if norm == 0:
            return avg
        return [v / norm for v in avg]

    def _early_stop(self, loss: float, best_loss: float, stale_epochs: int) -> Tuple[bool, float, int]:
        if loss < best_loss - self.config.early_stopping_min_delta:
            return False, loss, 0
        stale_epochs += 1
        return stale_epochs >= self.config.early_stopping_patience, best_loss, stale_epochs

    def train(self) -> Tuple[DetectorConfig, DetectorWeights]:
        lexical = InMemoryESBM25(self.domain_docs, k1=self.config.bm25_k1, b=self.config.bm25_b)
        vectorizer = TfidfVectorizer(self.domain_docs + [sample.text for sample in self.semantic_samples])
        domain_vectors = [vectorizer.transform(doc) for doc in self.domain_docs]
        domain_prototype = self._mean_vector(domain_vectors)

        semantic_model = SemanticBinaryClassifier()
        semantic_train = []
        for sample in self.semantic_samples:
            lex = lexical.search(sample.text)
            cosine = cosine_similarity(vectorizer.transform(sample.text), domain_prototype)
            semantic_train.append(([cosine, lex.match_ratio], sample.label))

        best_loss = float("inf")
        stale_epochs = 0
        for epoch in range(self.config.semantic_epochs):
            loss = semantic_model.train_one_epoch(semantic_train, lr=self.config.semantic_lr)
            self.logger.info("semantic epoch=%s loss=%.6f", epoch + 1, loss)
            should_stop, best_loss, stale_epochs = self._early_stop(loss, best_loss, stale_epochs)
            if should_stop:
                self.logger.info("semantic early stop at epoch=%s", epoch + 1)
                break

        fusion_model = FusionBinaryNeuralNet(hidden_dim=self.config.fusion_hidden_dim)
        fusion_train = []
        for sample in self.fusion_samples:
            lex = lexical.search(sample.text)
            cosine = cosine_similarity(vectorizer.transform(sample.text), domain_prototype)
            semantic_label = semantic_model.predict_label([cosine, lex.match_ratio], self.config.threshold)
            fusion_train.append(([lex.bm25_score, lex.match_ratio, cosine, float(semantic_label)], sample.label))

        best_loss = float("inf")
        stale_epochs = 0
        for epoch in range(self.config.fusion_epochs):
            loss = fusion_model.train_one_epoch(fusion_train, lr=self.config.fusion_lr)
            self.logger.info("fusion epoch=%s loss=%.6f", epoch + 1, loss)
            should_stop, best_loss, stale_epochs = self._early_stop(loss, best_loss, stale_epochs)
            if should_stop:
                self.logger.info("fusion early stop at epoch=%s", epoch + 1)
                break

        config = DetectorConfig(
            vocab=vectorizer.vocab,
            idf=vectorizer.idf,
            threshold=self.config.threshold,
            bm25_k1=self.config.bm25_k1,
            bm25_b=self.config.bm25_b,
            fusion_hidden_dim=self.config.fusion_hidden_dim,
        )
        weights = DetectorWeights(
            vectorizer_idf={
                "domain_docs": self.domain_docs,
                "domain_prototype": domain_prototype,
                "semantic_weights": semantic_model.weights,
                "semantic_bias": semantic_model.bias,
            },
            fusion_mlp={
                "w1": fusion_model.w1,
                "b1": fusion_model.b1,
                "w2": fusion_model.w2,
                "b2": fusion_model.b2,
            },
        )
        return config, weights

    def train_and_save(self, config_path: Path, model_path: Path) -> None:
        config, weights = self.train()
        save_config(config, config_path)
        save_weights(weights, model_path)
