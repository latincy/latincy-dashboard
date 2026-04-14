"""Shared helpers for latincy-lexicon demo pages (11, 12, 13)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st


DEFAULT_SENTENCE = "Poeta bonus carmina pulchra scribit."


@st.cache_resource(show_spinner="Building Whitaker's Words data (first load only)…")
def build_lexicon_artifacts() -> tuple[Path, Path]:
    """Build lexicon.json + analyzer.json once per session.

    Artifacts are cached under a temp directory. First call takes
    ~5–10s; subsequent calls short-circuit via Streamlit's
    cache_resource and are instant.
    """
    from latincy_lexicon.build import build

    output_dir = Path(tempfile.gettempdir()) / "latincy-dashboard-lexicon"
    output_dir.mkdir(parents=True, exist_ok=True)

    lexicon_path = output_dir / "lexicon.json"
    analyzer_path = output_dir / "analyzer.json"

    if not (lexicon_path.exists() and analyzer_path.exists()):
        build(output_dir=output_dir)

    return lexicon_path, analyzer_path


@st.cache_resource(show_spinner="Loading LatinCy pipeline…")
def load_lexicon_pipeline(model_name: str):
    """Load a LatinCy model with whitakers_words + paradigm_generator attached.

    Cached per model_name — all three lexicon demo pages share the same
    pipeline instance, so switching pages is instant after the first
    load.
    """
    import spacy

    nlp = spacy.load(model_name)
    lexicon_path, analyzer_path = build_lexicon_artifacts()

    nlp.add_pipe(
        "whitakers_words",
        config={
            "lexicon_path": str(lexicon_path),
            "analyzer_path": str(analyzer_path),
        },
        last=True,
    )
    nlp.add_pipe(
        "paradigm_generator",
        config={"analyzer_path": str(analyzer_path)},
        last=True,
    )
    return nlp


def sentence_picker(key: str) -> str:
    """Render a free-text area prefilled with a simple example sentence."""
    return st.text_area(
        "Latin text:",
        value=DEFAULT_SENTENCE,
        height=100,
        key=f"text_{key}",
    )
