from __future__ import annotations

import re
from typing import List


TOKEN_PATTERN = re.compile(r"[\u4e00-\u9fff]+|[a-zA-Z0-9]+")


def tokenize(text: str) -> List[str]:
    text = text.lower()
    rough_tokens = TOKEN_PATTERN.findall(text)
    tokens: List[str] = []

    for token in rough_tokens:
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            if len(token) == 1:
                continue
            tokens.extend(token[idx : idx + 2] for idx in range(len(token) - 1))
        else:
            tokens.append(token)
    return tokens
