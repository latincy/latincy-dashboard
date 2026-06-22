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
[latincy-vocab](https://github.com/diyclassics/latincy-vocab) —
lemmatized, glossed, and sortable.
"""
)

DEFAULT_TEXT = (
    "Haec narrantur ā poētīs dē Perseō. Perseus fīlius erat Iovis, maximī "
    "deōrum; avus eius Acrisius appellābātur. Acrisius volēbat Perseum nepōtem "
    "suum necāre; nam propter ōrāculum puerum timēbat. Comprehendit igitur "
    "Perseum adhūc īnfantem, et cum mātre in arcā ligneā inclūsit. Tum arcam "
    "ipsam in mare coniēcit. Danaē, Perseī māter, magnopere territa est; "
    "tempestās enim magna mare turbābat. Perseus autem in sinū mātris dormiēbat."
)

model_name = st.sidebar.selectbox(
    "Choose model:",
    ("la_core_web_lg", "la_core_web_md", "la_core_web_sm"),
)


@st.cache_resource(show_spinner="Loading vocabulary pipeline…")
def load_pipeline(model: str) -> VocabPipeline:
    config = PipelineConfig(spacy_model=model)
    return VocabPipeline(config)


pipeline = load_pipeline(model_name)

tab1, tab2 = st.tabs(["Vocab List", "About"])

with tab1:
    text = st.text_area(
        "Latin text:",
        value=DEFAULT_TEXT,
        height=160,
        key="vocab_text",
    )

    if st.button("Build Vocabulary List", key="vocab_run"):
        with st.spinner("Processing…"):
            vocab: VocabList = pipeline.process(text)
        st.session_state["vocab_list"] = vocab
        st.session_state["vocab_sort"] = "alpha"

    if "vocab_list" in st.session_state:
        vocab: VocabList = st.session_state["vocab_list"]
        current_sort: str = st.session_state.get("vocab_sort", "alpha")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(
                "**Alphabetical**" if current_sort == "alpha" else "Alphabetical",
                key="sort_alpha",
                use_container_width=True,
            ):
                st.session_state["vocab_sort"] = "alpha"
                st.rerun()
        with col2:
            if st.button(
                "**First Occurrence**" if current_sort == "occurrence" else "First Occurrence",
                key="sort_occurrence",
                use_container_width=True,
            ):
                st.session_state["vocab_sort"] = "occurrence"
                st.rerun()
        with col3:
            if st.button(
                "**Frequency**" if current_sort == "freq" else "Frequency",
                key="sort_freq",
                use_container_width=True,
            ):
                st.session_state["vocab_sort"] = "freq"
                st.rerun()

        sort_key = st.session_state.get("vocab_sort", "alpha")
        if sort_key == "alpha":
            sorted_vocab = vocab.by_alpha()
        elif sort_key == "occurrence":
            sorted_vocab = vocab.by_first_occurrence()
        else:
            sorted_vocab = vocab.by_frequency()

        st.markdown(f"**{len(sorted_vocab)} entries**")
        st.markdown("---")

        lines = []
        for entry in sorted_vocab:
            parts = [f"**{entry.headword}**"]
            if entry.pos_marker:
                parts.append(f"*{entry.pos_marker}*")
            if entry.short_gloss:
                parts.append(entry.short_gloss)
            if entry.frequency > 1:
                parts.append(f"*(×{entry.frequency})*")
            lines.append("  \n".join(["&nbsp;&nbsp;".join(parts)]))

        st.markdown("\n\n".join(lines))

with tab2:
    st.markdown(
        """
### About

This demo uses **latincy-vocab** (`vocabbuilder.VocabPipeline`) to process a Latin
passage end-to-end:

1. **spaCy** tokenizes and annotates (lemma, POS, morphology)
2. **latincy-lexicon** attaches citation forms (principal parts, gen+gender)
3. **latincy-words** supplies Whitaker's Words glosses
4. `VocabList` deduplicates by lemma+POS and exposes three orderings

The default text is §1 of Ritchie's *Fabulae Faciles* (1902).

**Sort modes**
- *Alphabetical* — traditional glossary order
- *First Occurrence* — passage reading order (as in textbook footnotes)
- *Frequency* — most common lemmas first
"""
    )
