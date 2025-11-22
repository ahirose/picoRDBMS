"""
Tiny character-level language model implemented with only the Python standard library.

The goal of this module is to provide a readable, dependency-free reference for how a
minimal decoder-style neural language model can be trained end-to-end.

Design choices:
- character-level vocabulary extracted from training text.
- fixed-size context window (n previous characters -> predict next).
- single hidden layer with ReLU non-linearity.
- manual forward and backward pass with cross-entropy loss.

This is intentionally small and not optimized for performance or accuracy. It is
suitable for short demo texts to illustrate the training loop and sampling process.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple


Vector = List[float]
Matrix = List[List[float]]


def zeros(rows: int, cols: int) -> Matrix:
    return [[0.0 for _ in range(cols)] for _ in range(rows)]


def random_matrix(rows: int, cols: int, scale: float = 0.1) -> Matrix:
    return [[random.uniform(-scale, scale) for _ in range(cols)] for _ in range(rows)]


def matvec(mat: Matrix, vec: Vector) -> Vector:
    return [sum(m_ij * v_j for m_ij, v_j in zip(row, vec)) for row in mat]


def add_inplace(target: Vector, src: Vector) -> None:
    for i, val in enumerate(src):
        target[i] += val


def relu(vec: Vector) -> Vector:
    return [max(0.0, v) for v in vec]


def softmax(vec: Vector) -> Vector:
    max_v = max(vec)
    exps = [math.exp(v - max_v) for v in vec]
    total = sum(exps)
    return [e / total for e in exps]


@dataclass
class Dataset:
    inputs: List[List[int]]
    targets: List[int]


class TinyLLM:
    """Extremely small character-level language model with manual gradients."""

    def __init__(
        self,
        text: str,
        context: int = 4,
        embed_dim: int = 8,
        hidden_dim: int = 32,
        learning_rate: float = 0.1,
        seed: int | None = 42,
    ) -> None:
        if seed is not None:
            random.seed(seed)
        if len(text) <= context:
            raise ValueError("Training text must be longer than context window")

        self.context = context
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim
        self.learning_rate = learning_rate

        self.vocab, self.stoi, self.itos = self._build_vocab(text)
        self.dataset = self._build_dataset(text)

        vocab_size = len(self.vocab)
        input_dim = context * embed_dim

        # Parameters
        self.E: Matrix = random_matrix(vocab_size, embed_dim, scale=0.5)
        self.W1: Matrix = random_matrix(hidden_dim, input_dim, scale=0.1)
        self.b1: Vector = [0.0 for _ in range(hidden_dim)]
        self.W2: Matrix = random_matrix(vocab_size, hidden_dim, scale=0.1)
        self.b2: Vector = [0.0 for _ in range(vocab_size)]

    # ------------------------- evaluation helpers -------------------------
    def loss(self) -> float:
        """Compute average negative log-likelihood over the dataset."""

        total_loss = 0.0
        for x_idx, target_idx in zip(self.dataset.inputs, self.dataset.targets):
            probs, _ = self._forward(x_idx)
            # add a tiny constant to avoid log(0)
            total_loss += -math.log(probs[target_idx] + 1e-12)
        return total_loss / len(self.dataset.inputs)

    # ------------------------- data preparation -------------------------
    def _build_vocab(self, text: str) -> Tuple[List[str], Dict[str, int], Dict[int, str]]:
        vocab = sorted(set(text))
        stoi = {ch: i for i, ch in enumerate(vocab)}
        itos = {i: ch for ch, i in stoi.items()}
        return vocab, stoi, itos

    def _encode(self, chars: Iterable[str]) -> List[int]:
        return [self.stoi[c] for c in chars]

    def _build_dataset(self, text: str) -> Dataset:
        inputs: List[List[int]] = []
        targets: List[int] = []
        for i in range(len(text) - self.context):
            window = text[i : i + self.context]
            target = text[i + self.context]
            inputs.append(self._encode(window))
            targets.append(self.stoi[target])
        return Dataset(inputs, targets)

    # ------------------------------ model ------------------------------
    def _forward(self, x_idx: List[int]):
        # Embedding lookup and flatten
        embed_vectors = [self.E[idx] for idx in x_idx]
        x_flat: Vector = [val for vec in embed_vectors for val in vec]

        # Layer 1
        hidden_raw = matvec(self.W1, x_flat)
        add_inplace(hidden_raw, self.b1)
        hidden = relu(hidden_raw)

        # Layer 2
        logits = matvec(self.W2, hidden)
        add_inplace(logits, self.b2)
        probs = softmax(logits)

        cache = {
            "x_indices": x_idx,
            "x_flat": x_flat,
            "hidden": hidden,
            "hidden_raw": hidden_raw,
            "probs": probs,
        }
        return probs, cache

    def _backward(self, cache, target_idx: int):
        probs: Vector = cache["probs"]
        hidden: Vector = cache["hidden"]
        hidden_raw: Vector = cache["hidden_raw"]
        x_flat: Vector = cache["x_flat"]
        x_indices: Sequence[int] = cache["x_indices"]

        vocab_size = len(self.vocab)
        input_dim = self.context * self.embed_dim

        # Gradients placeholders
        grad_logits = probs[:]
        grad_logits[target_idx] -= 1.0

        grad_W2 = zeros(vocab_size, self.hidden_dim)
        grad_b2 = grad_logits[:]
        grad_hidden = [0.0 for _ in range(self.hidden_dim)]

        for i in range(vocab_size):
            for j in range(self.hidden_dim):
                grad_W2[i][j] = grad_logits[i] * hidden[j]
                grad_hidden[j] += self.W2[i][j] * grad_logits[i]

        # ReLU backward
        for j, raw in enumerate(hidden_raw):
            if raw <= 0:
                grad_hidden[j] = 0.0

        grad_W1 = zeros(self.hidden_dim, input_dim)
        grad_b1 = grad_hidden[:]
        grad_x_flat = [0.0 for _ in range(input_dim)]

        for j in range(self.hidden_dim):
            for k in range(input_dim):
                grad_W1[j][k] = grad_hidden[j] * x_flat[k]
                grad_x_flat[k] += self.W1[j][k] * grad_hidden[j]

        grad_E = zeros(len(self.vocab), self.embed_dim)
        for pos, vocab_idx in enumerate(x_indices):
            for d in range(self.embed_dim):
                grad_E[vocab_idx][d] += grad_x_flat[pos * self.embed_dim + d]

        return grad_E, grad_W1, grad_b1, grad_W2, grad_b2

    # ------------------------------ training ------------------------------
    def _apply_grads(
        self,
        grad_E: Matrix,
        grad_W1: Matrix,
        grad_b1: Vector,
        grad_W2: Matrix,
        grad_b2: Vector,
    ) -> None:
        lr = self.learning_rate

        for i in range(len(self.E)):
            for j in range(self.embed_dim):
                self.E[i][j] -= lr * grad_E[i][j]

        for i in range(self.hidden_dim):
            for j in range(self.context * self.embed_dim):
                self.W1[i][j] -= lr * grad_W1[i][j]
            self.b1[i] -= lr * grad_b1[i]

        for i in range(len(self.vocab)):
            for j in range(self.hidden_dim):
                self.W2[i][j] -= lr * grad_W2[i][j]
            self.b2[i] -= lr * grad_b2[i]

    def train(self, epochs: int = 200, report_every: int = 20) -> None:
        """Train on the prepared dataset using full-batch gradient descent."""

        num_samples = len(self.dataset.inputs)
        for epoch in range(1, epochs + 1):
            total_loss = 0.0
            grad_E_total = zeros(len(self.vocab), self.embed_dim)
            grad_W1_total = zeros(self.hidden_dim, self.context * self.embed_dim)
            grad_b1_total = [0.0 for _ in range(self.hidden_dim)]
            grad_W2_total = zeros(len(self.vocab), self.hidden_dim)
            grad_b2_total = [0.0 for _ in range(len(self.vocab))]

            for x_idx, target_idx in zip(self.dataset.inputs, self.dataset.targets):
                probs, cache = self._forward(x_idx)
                loss = -math.log(probs[target_idx] + 1e-12)
                total_loss += loss
                grads = self._backward(cache, target_idx)
                gE, gW1, gb1, gW2, gb2 = grads

                for i in range(len(self.vocab)):
                    for j in range(self.embed_dim):
                        grad_E_total[i][j] += gE[i][j]
                for i in range(self.hidden_dim):
                    for j in range(self.context * self.embed_dim):
                        grad_W1_total[i][j] += gW1[i][j]
                    grad_b1_total[i] += gb1[i]
                for i in range(len(self.vocab)):
                    for j in range(self.hidden_dim):
                        grad_W2_total[i][j] += gW2[i][j]
                    grad_b2_total[i] += gb2[i]

            # Average gradients to keep updates stable regardless of dataset size.
            inv_n = 1.0 / num_samples
            for i in range(len(self.vocab)):
                for j in range(self.embed_dim):
                    grad_E_total[i][j] *= inv_n
            for i in range(self.hidden_dim):
                for j in range(self.context * self.embed_dim):
                    grad_W1_total[i][j] *= inv_n
                grad_b1_total[i] *= inv_n
            for i in range(len(self.vocab)):
                for j in range(self.hidden_dim):
                    grad_W2_total[i][j] *= inv_n
                grad_b2_total[i] *= inv_n

            self._apply_grads(
                grad_E_total, grad_W1_total, grad_b1_total, grad_W2_total, grad_b2_total
            )

            if epoch % report_every == 0:
                avg_loss = total_loss / num_samples
                print(f"Epoch {epoch:03d} | loss={avg_loss:.4f}")

    # ------------------------------ generation ------------------------------
    def predict_next(self, context_text: str) -> Tuple[str, Vector]:
        if len(context_text) != self.context:
            raise ValueError(f"context_text must be length {self.context}")
        idxs = self._encode(context_text)
        probs, _ = self._forward(idxs)
        return self.itos[max(range(len(probs)), key=lambda i: probs[i])], probs

    def sample(self, seed: str, max_new: int = 40) -> str:
        if len(seed) < self.context:
            seed = seed.rjust(self.context)
        seed = seed[-self.context :]
        generated = list(seed)
        for _ in range(max_new):
            next_ch, probs = self.predict_next("".join(generated[-self.context :]))
            generated.append(next_ch)
            if next_ch == "\n":
                break
        return "".join(generated)


__all__ = ["TinyLLM"]
