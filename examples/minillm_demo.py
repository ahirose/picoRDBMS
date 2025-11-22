"""Small demonstration script for the pure-Python TinyLLM class.

Usage:
    python examples/minillm_demo.py

This trains on a tiny nursery-rhyme style text and samples from the model
after a few epochs. No external dependencies are required.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from minillm import TinyLLM

TRAIN_TEXT = """
hello tiny model.
this is a short demo to show how a tiny llm can be trained.
repeat after me: tiny tiny tiny! 
""".strip()


def main() -> None:
    model = TinyLLM(TRAIN_TEXT, context=4, embed_dim=6, hidden_dim=24, learning_rate=0.2)
    model.train(epochs=120, report_every=30)

    seed = "hell"
    print("\nSeed:", seed)
    print("Sampled text:")
    print(model.sample(seed, max_new=120))


if __name__ == "__main__":
    main()
