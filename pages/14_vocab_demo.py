import streamlit as st

from vocabbuilder import VocabPipeline
from vocabbuilder.core.config import PipelineConfig
from vocabbuilder.core.models import VocabList

st.set_page_config(page_title="Vocab Builder Demo", layout="wide")
st.sidebar.header("Vocab Builder Demo")

st.title("Latin Vocabulary Builder")
st.markdown(
    """
Generate a textbook-style vocabulary list from any Latin passage using
[latincy-vocab](https://github.com/latincy/latincy-vocab) —
lemmatized, glossed, and sortable.
"""
)

DEFAULT_TEXT = (
    "Haec narrantur a poetis de Perseo. Perseus filius erat Iovis, maximi "
    "deorum; avus eius Acrisius appellabatur. Acrisius volebat Perseum nepotem "
    "suum necare; nam propter oraculum puerum timebat. Comprehendit igitur "
    "Perseum adhuc infantem, et cum matre in arca lignea inclusit. Tum arcam "
    "ipsam in mare coniecit. Danae, Persei mater, magnopere territa est; "
    "tempestas enim magna mare turbabat. Perseus autem in sinu matris dormiebat."
)

@st.cache_resource(show_spinner="Loading vocabulary pipeline…")
def load_pipeline() -> VocabPipeline:
    config = PipelineConfig(spacy_model="la_core_web_lg")
    return VocabPipeline(config)


pipeline = load_pipeline()

tab1, tab2 = st.tabs(["Vocab List", "About"])

with tab1:
    col_input, col_vocab = st.columns([2, 3])

    with col_input:
        text = st.text_area(
            "Latin text:",
            value=DEFAULT_TEXT,
            height=280,
            key="vocab_text",
        )
        run = st.button("Build Vocabulary List", key="vocab_run")

    if run:
        with st.spinner("Processing…"):
            vocab: VocabList = pipeline.process(text)
        st.session_state["vocab_list"] = vocab
        st.session_state["vocab_sort"] = "alpha"

    with col_vocab:
        if "vocab_list" in st.session_state:
            vocab: VocabList = st.session_state["vocab_list"]
            current_sort = st.session_state.get("vocab_sort", "alpha")

            s1, s2, s3 = st.columns(3)
            with s1:
                if st.button("Alphabetical", key="sort_alpha", use_container_width=True):
                    st.session_state["vocab_sort"] = "alpha"
                    st.rerun()
            with s2:
                if st.button("First Occurrence", key="sort_occ", use_container_width=True):
                    st.session_state["vocab_sort"] = "occurrence"
                    st.rerun()
            with s3:
                if st.button("Frequency", key="sort_freq", use_container_width=True):
                    st.session_state["vocab_sort"] = "freq"
                    st.rerun()

            sort_key = st.session_state.get("vocab_sort", "alpha")
            if sort_key == "alpha":
                sorted_vocab = vocab.by_alpha()
            elif sort_key == "occurrence":
                sorted_vocab = vocab.by_first_occurrence()
            else:
                sorted_vocab = vocab.by_frequency()

            visible = [e for e in sorted_vocab if e.headword and e.headword[0].isalpha()]

            st.caption(
                f"{len(visible)} entries · assembled from probabilistic LatinCy "
                "pipeline annotations — verify before use"
            )

            lines = []
            for entry in visible:
                hw = f"<strong>{entry.headword}</strong>"
                pm = f" <em>{entry.pos_marker}</em>" if entry.pos_marker else ""
                gloss = f", {entry.short_gloss}" if entry.short_gloss else ""
                freq = f" <em>×{entry.frequency}</em>" if entry.frequency > 1 else ""
                lines.append(
                    f"<p style='margin:0 0 2px 0;line-height:1.4'>{hw}{pm}{gloss}{freq}</p>"
                )

            st.markdown("".join(lines), unsafe_allow_html=True)

with tab2:
    st.markdown(
        """
### About

This demo uses **latincy-vocab** (`vocabbuilder.VocabPipeline`) to process a Latin
passage end-to-end:

1. **spaCy** tokenizes and annotates (lemma, POS, morphology)
2. **latincy-lexicon** supplies Whitaker's Words glosses and display lemmas
3. **latincy-words** attaches citation forms where available
4. `VocabList` deduplicates by lemma+POS and exposes three orderings

> **Note:** vocabulary entries are assembled from probabilistic LatinCy pipeline
> annotations and should be verified before use in publication or teaching.

The default text is §1 of Ritchie's *Fabulae Faciles* (1902).

**Sort modes**
- *Alphabetical* — traditional glossary order
- *First Occurrence* — passage reading order (as in textbook footnotes)
- *Frequency* — most common lemmas first
"""
    )
