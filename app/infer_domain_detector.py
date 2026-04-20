from __future__ import annotations

import argparse
from pathlib import Path

from app.domain_detector import CoreNetworkExperienceDomainDetector


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="核心网体验策略领域判定推理")
    parser.add_argument("query", help="待判定的用户问题")
    parser.add_argument("--config", default=".data/domain_detector/config.json", help="配置文件路径")
    parser.add_argument("--model", default=".data/domain_detector/model.pt", help="模型权重文件路径")
    parser.add_argument("--threshold", type=float, default=None, help="可选覆盖阈值")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    detector = CoreNetworkExperienceDomainDetector(Path(args.config), Path(args.model))
    result = detector.analyze(args.query, threshold=args.threshold)

    print("用户问题:", args.query)
    print("BM25分数:", round(result.lexical.bm25_score, 4))
    print("关键词匹配占比:", round(result.lexical.match_ratio, 4))
    print("命中关键词:", result.lexical.matched_terms)
    print("余弦相似度:", round(result.semantic.cosine_similarity, 4))
    print("语义分类标签(1=领域内):", result.semantic.semantic_label)
    print("融合模型概率:", round(result.probability, 4))
    print("最终判定:", "属于该领域" if result.in_domain else "不属于该领域")


if __name__ == "__main__":
    main()
