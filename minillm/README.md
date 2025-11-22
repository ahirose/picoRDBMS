# TinyLLM walkthrough

`TinyLLM` is a dependency-free, fully manual character-level language model meant to show the moving parts of a decoder-only network. Everything lives in `minillm/model.py` and uses just the Python standard library.

## Architecture
- **Vocabulary**: characters observed in the training text.
- **Context window**: last *n* characters are used to predict the next one.
- **Embedding table**: look up a small vector for each character (matrix `E`).
- **Two-layer MLP**: flatten the embeddings, push through `W1` + ReLU and `W2` to produce logits.
- **Softmax**: turn logits into probabilities for the next character.

## Training loop
1. Slide a window over the text to build `(context -> next_char)` pairs.
2. Forward pass to get probabilities for the target character.
3. Cross-entropy loss and manual backprop over all parameters.
4. Update parameters with gradient descent (full-batch for clarity).

The `TinyLLM.train()` method prints loss every few epochs; `TinyLLM.loss()` lets you measure progress without training.

## Sampling
Call `model.sample(seed, max_new=40)` to repeatedly predict the next character and append it to the string. A newline stops generation early.

## Quick demo
```
python examples/minillm_demo.py
```

To experiment interactively, tweak `context`, `embed_dim`, or `hidden_dim` and rerun the demo. Smaller values train faster; larger ones capture a bit more structure.
