from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import pickle
from typing import Any, Dict, List


@dataclass
class DetectorConfig:
    vocab: List[str]
    idf: List[float]
    threshold: float
    bm25_k1: float
    bm25_b: float
    fusion_hidden_dim: int


@dataclass
class DetectorWeights:
    # 按建议将中间层/顶层权重聚合保存
    vectorizer_idf: Dict[str, Any]  # LR 层参数集合
    fusion_mlp: Dict[str, Any]      # MLP 层参数集合


def save_config(config: DetectorConfig, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8")


def save_weights(weights: DetectorWeights, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        pickle.dump(asdict(weights), f)


def load_config(input_path: Path) -> DetectorConfig:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    required = ["vocab", "idf", "threshold", "bm25_k1", "bm25_b", "fusion_hidden_dim"]
    for key in required:
        if key not in payload:
            raise ValueError(f"config 缺少字段: {key}")
    return DetectorConfig(
        vocab=list(payload["vocab"]),
        idf=list(payload["idf"]),
        threshold=float(payload["threshold"]),
        bm25_k1=float(payload["bm25_k1"]),
        bm25_b=float(payload["bm25_b"]),
        fusion_hidden_dim=int(payload["fusion_hidden_dim"]),
    )


def load_weights(input_path: Path) -> DetectorWeights:
    with input_path.open("rb") as f:
        payload = pickle.load(f)

    if not isinstance(payload, dict):
        raise ValueError("weights 文件格式错误: 顶层必须是 dict")
    if "vectorizer_idf" not in payload or "fusion_mlp" not in payload:
        raise ValueError("weights 文件缺少 vectorizer_idf 或 fusion_mlp 字段")

    vectorizer_idf = payload["vectorizer_idf"]
    fusion_mlp = payload["fusion_mlp"]
    if not isinstance(vectorizer_idf, dict) or not isinstance(fusion_mlp, dict):
        raise ValueError("weights 子字段必须是 dict")

    return DetectorWeights(vectorizer_idf=vectorizer_idf, fusion_mlp=fusion_mlp)
