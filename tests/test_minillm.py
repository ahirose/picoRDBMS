import math

from minillm import TinyLLM


def test_loss_decreases_with_training():
    text = "hello tiny model."
    model = TinyLLM(text, context=3, embed_dim=4, hidden_dim=12, learning_rate=0.2, seed=1)

    initial = model.loss()
    model.train(epochs=40, report_every=1000)  # suppress console logs
    final = model.loss()

    # Training should make measurable progress even with tiny hyperparameters.
    assert final < initial * 0.95, (initial, final)


def test_predict_next_probabilities_sum_to_one():
    text = "abcabcabc"
    model = TinyLLM(text, context=2, embed_dim=3, hidden_dim=6, learning_rate=0.3, seed=2)

    char, probs = model.predict_next("ab")
    assert isinstance(char, str)
    assert len(probs) == len(model.vocab)
    assert math.isclose(sum(probs), 1.0, rel_tol=1e-9)
