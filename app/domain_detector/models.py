from __future__ import annotations

import math
from typing import List, Sequence, Tuple


class SemanticBinaryClassifier:
    def __init__(self, weights: List[float] | None = None, bias: float = 0.0) -> None:
        self.weights = weights or [0.0, 0.0]
        self.bias = bias

    @staticmethod
    def _sigmoid(x: float) -> float:
        if x >= 0:
            z = math.exp(-x)
            return 1 / (1 + z)
        z = math.exp(x)
        return z / (1 + z)

    def _predict(self, features: Sequence[float]) -> float:
        z = sum(w * x for w, x in zip(self.weights, features)) + self.bias
        return self._sigmoid(z)

    def train_one_epoch(self, samples: Sequence[Tuple[List[float], int]], lr: float) -> float:
        total_loss = 0.0
        for features, label in samples:
            pred = self._predict(features)
            clipped = min(max(pred, 1e-8), 1 - 1e-8)
            total_loss += -(label * math.log(clipped) + (1 - label) * math.log(1 - clipped))

            grad = pred - label
            for idx in range(len(self.weights)):
                self.weights[idx] -= lr * grad * features[idx]
            self.bias -= lr * grad

        return total_loss / max(len(samples), 1)

    def predict_label(self, features: Sequence[float], threshold: float) -> int:
        return int(self._predict(features) >= threshold)


class FusionBinaryNeuralNet:
    def __init__(
        self,
        input_dim: int = 4,
        hidden_dim: int = 8,
        seed: int = 13,
        w1: List[List[float]] | None = None,
        b1: List[float] | None = None,
        w2: List[float] | None = None,
        b2: float = 0.0,
    ) -> None:
        if w1 is not None and b1 is not None and w2 is not None:
            self.w1 = w1
            self.b1 = b1
            self.w2 = w2
            self.b2 = b2
            return

        state = seed

        def rand() -> float:
            nonlocal state
            state = (1103515245 * state + 12345) % 2**31
            return state / 2**31 - 0.5

        self.w1 = [[rand() * 0.2 for _ in range(input_dim)] for _ in range(hidden_dim)]
        self.b1 = [0.0 for _ in range(hidden_dim)]
        self.w2 = [rand() * 0.2 for _ in range(hidden_dim)]
        self.b2 = 0.0

    @staticmethod
    def _relu(x: float) -> float:
        return x if x > 0 else 0.0

    @staticmethod
    def _relu_grad(x: float) -> float:
        return 1.0 if x > 0 else 0.0

    @staticmethod
    def _sigmoid(x: float) -> float:
        if x >= 0:
            z = math.exp(-x)
            return 1 / (1 + z)
        z = math.exp(x)
        return z / (1 + z)

    def _forward(self, x: Sequence[float]) -> Tuple[List[float], List[float], float]:
        z1 = [sum(w * xv for w, xv in zip(row, x)) + b for row, b in zip(self.w1, self.b1)]
        h = [self._relu(v) for v in z1]
        z2 = sum(w * hv for w, hv in zip(self.w2, h)) + self.b2
        return z1, h, self._sigmoid(z2)

    def train_one_epoch(self, samples: Sequence[Tuple[List[float], int]], lr: float) -> float:
        total_loss = 0.0
        for x, label in samples:
            z1, h, y = self._forward(x)
            clipped = min(max(y, 1e-8), 1 - 1e-8)
            total_loss += -(label * math.log(clipped) + (1 - label) * math.log(1 - clipped))

            dz2 = y - label
            prev_w2 = self.w2[:]
            for j in range(len(self.w2)):
                self.w2[j] -= lr * dz2 * h[j]
            self.b2 -= lr * dz2

            for j in range(len(self.w1)):
                dh = dz2 * prev_w2[j]
                dz1 = dh * self._relu_grad(z1[j])
                for i in range(len(self.w1[j])):
                    self.w1[j][i] -= lr * dz1 * x[i]
                self.b1[j] -= lr * dz1

        return total_loss / max(len(samples), 1)

    def predict_proba(self, x: Sequence[float]) -> float:
        _, _, y = self._forward(x)
        return y
