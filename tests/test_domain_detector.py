from pathlib import Path

import pytest

from app.data_loader import build_default_training_data
from app.domain_detector import CoreNetworkExperienceDomainDetector, DomainDetectorTrainer, tokenize
from app.domain_detector.serialization import load_config


def test_tokenize_contains_cn_gram() -> None:
    tokens = tokenize("核心网体验策略")
    assert "核心" in tokens
    assert "策略" in tokens


def test_train_save_load_and_infer(tmp_path: Path) -> None:
    domain_docs, semantic_samples, fusion_samples = build_default_training_data()
    trainer = DomainDetectorTrainer(domain_docs, semantic_samples, fusion_samples)

    config_path = tmp_path / "config.json"
    model_path = tmp_path / "model.pt"
    trainer.train_and_save(config_path, model_path)

    detector = CoreNetworkExperienceDomainDetector(config_path, model_path)
    in_domain = detector.analyze("核心网体验策略中PCF和SMF如何协同保障时延")
    out_domain = detector.analyze("推荐一部适合周末看的电影")

    assert in_domain.in_domain is True
    assert out_domain.in_domain is False


def test_load_config_validates_required_fields(tmp_path: Path) -> None:
    broken = tmp_path / "broken_config.json"
    broken.write_text('{"vocab": ["a"]}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(broken)
