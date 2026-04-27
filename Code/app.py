"""Main script, uses other modules to generate sample text in a web app."""

from pathlib import Path

from flask import Flask, render_template, request

from histogram import histogram, sample_uniform, sample_weighted
from markov import build_markov_chain, generate_sentence


app = Flask(__name__)

# Build histogram and Markov chain once when the server starts.
CORPUS_PATH = Path(__file__).resolve().parent / "data" / "corpus.txt"
FALLBACK_TEXT = "one fish two fish red fish blue fish"

_source = str(CORPUS_PATH) if CORPUS_PATH.exists() else FALLBACK_TEXT
WORD_HISTOGRAM = histogram(_source)
MARKOV_CHAIN = build_markov_chain(_source)


def generate_words(num_words: int, mode: str) -> list[str]:
    """Generate words from the global histogram using the requested mode."""
    sampler = sample_uniform if mode == "uniform" else sample_weighted
    return [sampler(WORD_HISTOGRAM) for _ in range(num_words)]


@app.route("/")
def home():
    """Render home page with newly sampled words on each request."""
    mode = request.args.get("mode", "markov").lower()
    if mode not in {"uniform", "weighted", "markov"}:
        mode = "markov"

    num_arg = request.args.get("num", "15")
    try:
        num = int(num_arg)
    except ValueError:
        num = 15
    num = max(1, min(num, 50))

    if mode == "markov":
        generated_text = generate_sentence(MARKOV_CHAIN, num_words=num)
    else:
        words = generate_words(num_words=num, mode=mode)
        generated_text = " ".join(words)

    return render_template(
        "index.html",
        generated_text=generated_text,
        mode=mode,
        num=num,
        corpus_source=str(CORPUS_PATH) if CORPUS_PATH.exists() else "fallback text",
    )


if __name__ == "__main__":
    """To run the Flask server, execute `python app.py` in your terminal.
       To learn more about Flask's DEBUG mode, visit
       https://flask.palletsprojects.com/en/2.0.x/server/#in-code"""
    app.run(debug=True)
