from __future__ import annotations

import argparse
import logging
from pathlib import Path

from app.data_loader import build_default_training_data
from app.domain_detector import DomainDetectorTrainer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="离线训练核心网体验策略领域判定模型")
    parser.add_argument("--config-output", default=".data/domain_detector/config.json", help="配置输出路径")
    parser.add_argument("--model-output", default=".data/domain_detector/model.pt", help="权重输出路径")
    parser.add_argument("--threshold", type=float, default=0.5, help="默认推理阈值")
    return parser


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = build_parser().parse_args()
    domain_docs, semantic_samples, fusion_samples = build_default_training_data()

    trainer = DomainDetectorTrainer(
        domain_docs,
        semantic_samples,
        fusion_samples,
        config={"threshold": args.threshold},
    )
    trainer.train_and_save(Path(args.config_output), Path(args.model_output))
    print(f"训练完成，配置已保存到: {args.config_output}")
    print(f"训练完成，权重已保存到: {args.model_output}")


if __name__ == "__main__":
    main()
