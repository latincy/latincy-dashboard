import streamlit as st

from latincy_preprocess.long_s import LongSNormalizer

st.set_page_config(page_title="Long-S Normalizer Demo", layout="wide")
st.sidebar.header("Long-S Normalizer Demo")

pass1_only = st.sidebar.checkbox(
    "Pass 1 only",
    value=False,
    help="Skip frequency-based Pass 2; apply only high-confidence bigram/trigram rules",
)

# Sample text (Cicero-style, with long-s OCR artifacts: f for s)
SAMPLE_TEXT = (
    "Cum autem fuper hac re fententiam dicere oporteat, patres confcripti, "
    "femper habui ftatuendum, nec fcientia fed etiam fpecie. "
    "Quoufque tandem abutere, Catilina, patientia noftra?"
)

# HTML styling
HTML_GREEN = '<span style="color: #28a745; font-weight: bold">'
HTML_GREY = '<span style="color: #6c757d">'
HTML_END = "</span>"


@st.cache_resource
def get_normalizer() -> LongSNormalizer:
    """Get cached normalizer instance."""
    return LongSNormalizer()


normalizer = get_normalizer()

st.title("Latin Long-S Normalizer")
st.markdown(
    "Correct OCR artifacts from historical Latin texts where long-s (ſ) was misread as 'f', "
    "using [latincy-preprocess](https://pypi.org/project/latincy-preprocess/)."
)

tab1, tab2 = st.tabs(["Normalize", "About"])

# === NORMALIZE TAB ===
with tab1:
    st.markdown(
        "Enter Latin text with long-s OCR artifacts (f instead of s) "
        "and normalize it."
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        text = st.text_area(
            "Input text (with OCR artifacts):",
            value=SAMPLE_TEXT,
            height=200,
            help="Enter Latin text where long-s (ſ) was misread as 'f' by OCR",
        )

    show_details = st.checkbox("Show correction details", value=False)

    if st.button("Normalize", type="primary"):
        if not text.strip():
            st.warning("Please enter some text")
        else:
            apply_pass2 = not pass1_only

            # Normalize word-by-word for colorization and rule details
            words = text.split()
            html_parts = []
            corrections = []

            for word in words:
                norm, rules = normalizer.normalize_word_full(
                    word, apply_pass2=apply_pass2
                )
                if word.lower() != norm:
                    html_parts.append(f"{HTML_GREEN}{norm}{HTML_END}")
                    corrections.append((word, norm, rules))
                else:
                    html_parts.append(f"{HTML_GREY}{norm}{HTML_END}")

            with col2:
                st.markdown("**Normalized text:**")
                st.markdown(" ".join(html_parts), unsafe_allow_html=True)

                total = len(words)
                modified = len(corrections)
                pct = (modified / total * 100) if total > 0 else 0
                st.markdown(
                    f"*{modified} word{'s' if modified != 1 else ''} corrected "
                    f"out of {total} total ({pct:.0f}%)*"
                )

            if show_details:
                if corrections:
                    with st.expander("Correction details", expanded=True):
                        seen = set()
                        for word, norm, rules in corrections:
                            key = (word.lower(), norm)
                            if key not in seen:
                                seen.add(key)
                                rule_str = "; ".join(rules) if rules else "unknown"
                                st.markdown(
                                    f"- **{word}** → **{norm}** — {rule_str}"
                                )
                else:
                    st.info("No corrections made")

# === ABOUT TAB ===
with tab2:
    st.markdown("""
    ## About

    ### The Long-S Problem

    In early printed Latin texts, the **long-s** (ſ) was used for the letter 's' in most
    positions. When these texts are digitized with OCR, the long-s is frequently misread
    as **'f'**, producing systematic errors like *fuper* for *super*, *ftatua* for *statua*,
    and *fcientia* for *scientia*.

    This tool automatically corrects these artifacts using a two-pass strategy.

    ### Two-Pass Correction

    **Pass 1 — High-Confidence Rules**

    Certain bigrams and trigrams containing 'f' are impossible or extremely rare in Latin,
    so they can be corrected with near-certainty:

    | Pattern | Correction | Reason |
    |---------|-----------|--------|
    | fp | sp | Impossible in Latin |
    | ft | st | Impossible in Latin |
    | fc | sc | Impossible in Latin |
    | fqu | squ | Impossible in Latin |
    | fpe | spe | Impossible in Latin |
    | word-final f | s | Extremely rare (0.01%) |

    **Pass 2 — Context-Dependent Disambiguation**

    Word-initial f/s ambiguity (e.g., *funt* vs. *sunt*, *fervus* vs. *servus*) is resolved
    using 4-gram frequency tables built from 842K words across 6 UD Latin treebanks:

    | Pattern | Correction | Method |
    |---------|-----------|--------|
    | fu- | su- | Trigram frequency comparison |
    | fe- | se- | Trigram frequency comparison |
    | fi- | si- | 4-gram frequency comparison |

    An **allowlist** of ~4,500 attested Latin f-words (e.g., *facio*, *fuit*, *forma*,
    *filia*) protects legitimate words from being incorrectly changed.

    ### Accuracy

    - **100%** on validated test set (852 word occurrences)
    - Pass 1 rules have zero false positives by design
    - Pass 2 uses conservative frequency thresholds

    ### Data Sources

    Training data drawn from 6 Universal Dependencies Latin treebanks (~842K words):
    ITTB, PROIEL, Perseus, LLCT, UDante, CIRCSE.

    ### Source

    [PyPI: latincy-preprocess](https://pypi.org/project/latincy-preprocess/)
    """)
