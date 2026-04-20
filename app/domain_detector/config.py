from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TrainingConfig:
    bm25_k1: float = 1.5
    bm25_b: float = 0.75
    semantic_lr: float = 0.2
    semantic_epochs: int = 300
    fusion_lr: float = 0.1
    fusion_epochs: int = 600
    fusion_hidden_dim: int = 8
    threshold: float = 0.5
    early_stopping_patience: int = 10
    early_stopping_min_delta: float = 1e-4

    @classmethod
    def from_dict(cls, payload: dict | None) -> "TrainingConfig":
        if not payload:
            return cls()
        return cls(**{k: v for k, v in payload.items() if k in cls.__annotations__})
