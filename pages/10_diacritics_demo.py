import streamlit as st

from latincy_diacritics import DiacriticRestorer, strip_diacritics, MUTABLE_CHARS, base_char

st.set_page_config(page_title="Greek Diacritics Restorer Demo", layout="wide")
st.sidebar.header("Greek Diacritics Restorer Demo")

# Opening of John 1:1, stripped of diacritics
SAMPLE_TEXT = (
    "εν αρχη ην ο λογος και ο λογος ην προς τον θεον και θεος ην ο λογος"
)

# HTML styling
HTML_GREEN = '<span style="color: #28a745; font-weight: bold">'
HTML_RED = '<span style="color: #dc3545; font-weight: bold">'
HTML_GREY = '<span style="color: #6c757d">'
HTML_END = "</span>"


@st.cache_resource
def get_restorer() -> DiacriticRestorer:
    """Get cached restorer instance."""
    return DiacriticRestorer()


def colorize_changes(original: str, restored: str, reference: str = None) -> str:
    """Create HTML with color-coded changes.

    Without reference: green=changed, grey=unchanged.
    With reference: green=correct, red=incorrect, grey=unchanged.
    """
    parts = []

    for i, (orig, rest) in enumerate(zip(original, restored)):
        if reference and i < len(reference):
            # Evaluate mode: compare against reference
            if rest == reference[i]:
                if orig != rest:
                    parts.append(f"{HTML_GREEN}{rest}{HTML_END}")
                else:
                    parts.append(f"{HTML_GREY}{rest}{HTML_END}")
            else:
                # Wrong — either changed to wrong char, or failed to change
                parts.append(f"{HTML_RED}{rest}{HTML_END}")
        elif orig != rest:
            parts.append(f"{HTML_GREEN}{rest}{HTML_END}")
        else:
            parts.append(f"{HTML_GREY}{rest}{HTML_END}")

    return "".join(parts)


restorer = get_restorer()

st.title("Greek Diacritics Restorer")
st.markdown(
    "Restore polytonic diacritics to undiacriticized Ancient Greek text "
    "using a character-level [CANINE-S](https://huggingface.co/google/canine-s) transformer, "
    "powered by [latincy-diacritics v0.1.0](https://huggingface.co/latincy/latincy-diacritics)."
)

tab1, tab2, tab3 = st.tabs(["Restore", "Evaluate", "About"])

# === RESTORE TAB ===
with tab1:
    st.markdown(
        "Enter undiacriticized Ancient Greek text and restore polytonic diacritics."
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        text = st.text_area(
            "Input text (without diacritics):",
            value=SAMPLE_TEXT,
            height=200,
            help="Enter Ancient Greek text stripped of diacritics",
        )

    show_details = st.checkbox("Show character details", value=False)

    if st.button("Restore", type="primary"):
        if not text.strip():
            st.warning("Please enter some text")
        else:
            result = restorer.restore_detailed(text)
            input_text = result["input"]
            output_text = result["output"]
            predictions = result["predictions"]

            with col2:
                st.markdown("**Restored text:**")
                colored = colorize_changes(input_text, output_text)
                st.markdown(colored, unsafe_allow_html=True)

                # Count changes and mutable positions
                changes = []
                mutable_count = 0
                for in_ch, out_ch in predictions:
                    if base_char(in_ch) in MUTABLE_CHARS:
                        mutable_count += 1
                    if in_ch != out_ch:
                        changes.append((in_ch, out_ch))

                n_changes = len(changes)
                st.markdown(
                    f"*{n_changes} character{'s' if n_changes != 1 else ''} restored "
                    f"out of {mutable_count} mutable position{'s' if mutable_count != 1 else ''}*"
                )

            if show_details:
                if changes:
                    with st.expander("Character details", expanded=True):
                        seen = set()
                        for in_ch, out_ch in changes:
                            key = (in_ch, out_ch)
                            if key not in seen:
                                seen.add(key)
                                st.markdown(f"- **{in_ch}** → **{out_ch}**")
                else:
                    st.info("No characters changed")

# === EVALUATE TAB ===
with tab2:
    st.markdown(
        "Enter correctly diacriticized text to evaluate accuracy. "
        "The system strips diacritics, restores them, and compares against your reference."
    )

    # Reference text: John 1:1 with correct polytonic diacritics
    REFERENCE_SAMPLE = (
        "ἐν ἀρχῇ ἦν ὁ λόγος καὶ ὁ λόγος ἦν πρὸς τὸν θεόν καὶ θεὸς ἦν ὁ λόγος"
    )

    reference = st.text_area(
        "Reference text (with correct diacritics):",
        value=REFERENCE_SAMPLE,
        height=200,
        help="Enter Ancient Greek text with correct polytonic diacritics",
    )

    if st.button("Evaluate", type="primary"):
        if not reference.strip():
            st.warning("Please enter reference text")
        else:
            # Lowercase reference to match strip_diacritics (which lowercases)
            # so evaluation measures diacritic accuracy, not case
            reference_lc = reference.lower()
            stripped = strip_diacritics(reference_lc)
            restored = restorer.restore(stripped)

            # Calculate metrics
            total_chars = min(len(stripped), len(restored), len(reference_lc))
            total_mutable = 0
            correct_mutable = 0
            total_correct = 0

            for i in range(total_chars):
                s, r, ref = stripped[i], restored[i], reference_lc[i]

                if r == ref:
                    total_correct += 1

                if base_char(s) in MUTABLE_CHARS:
                    total_mutable += 1
                    if r == ref:
                        correct_mutable += 1

            overall_acc = total_correct / total_chars if total_chars > 0 else 1.0
            mutable_acc = correct_mutable / total_mutable if total_mutable > 0 else 1.0

            # Sentence-level accuracy
            ref_sentences = [s.strip() for s in reference_lc.split(".") if s.strip()]
            strip_sentences = [s.strip() for s in stripped.split(".") if s.strip()]
            sentences_correct = 0
            total_sentences = len(ref_sentences)

            for ref_sent, strip_sent in zip(ref_sentences, strip_sentences):
                restored_sent = restorer.restore(strip_sent)
                if restored_sent == ref_sent:
                    sentences_correct += 1

            sentence_acc = sentences_correct / total_sentences if total_sentences > 0 else 1.0

            st.subheader("Evaluation Results")
            colored = colorize_changes(stripped, restored, reference_lc)
            st.markdown(colored, unsafe_allow_html=True)

            st.markdown(
                f"**Legend:** {HTML_GREEN}Correct{HTML_END} &middot; "
                f"{HTML_RED}Incorrect{HTML_END} &middot; "
                f"{HTML_GREY}Unchanged{HTML_END}",
                unsafe_allow_html=True,
            )

            st.subheader("Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Mutable Accuracy", f"{mutable_acc:.1%}")
            col2.metric("Overall Accuracy", f"{overall_acc:.1%}")
            col3.metric("Sentence Accuracy", f"{sentence_acc:.1%}")

            with st.expander("Detailed Statistics"):
                st.markdown(f"""
                - **Total characters:** {total_chars}
                - **Mutable positions:** {total_mutable}
                - **Mutable correct:** {correct_mutable}
                - **Overall correct:** {total_correct}
                - **Sentences:** {sentences_correct}/{total_sentences} perfect
                """)

# === ABOUT TAB ===
with tab3:
    st.markdown("""
    ## About

    ### The Diacritics Problem

    Ancient Greek in its polytonic form uses breathing marks, accents, iota
    subscripts, and diaeresis. Some digital texts lack these diacritics —
    whether stripped for NLP processing, stored in monotonic form, or
    entered without a polytonic keyboard.

    This tool automatically restores polytonic diacritics using a trained
    character-level transformer.

    ### CANINE-S Architecture

    The model uses [CANINE-S](https://huggingface.co/google/canine-s), a
    **character-level** transformer from Google that operates directly on Unicode
    code points — no subword tokenization needed. This makes it ideal for
    diacritics restoration, where the task is inherently character-level.

    The model predicts, for each **mutable** character position, which polytonic
    variant (from 2–25 options per base character) is correct in context.

    ### Mutable vs. Immutable Characters

    Only **vowels and rho** (α, ε, η, ι, ο, υ, ω, ρ) carry diacritics in Greek.
    These are the "mutable" characters. Consonants, punctuation, and spaces pass
    through unchanged — so **mutable accuracy** is the primary metric, since
    overall accuracy is inflated by trivial identity predictions.

    ### Accuracy

    - **97.21% mutable accuracy** on held-out test set
    - Trained on aligned pairs from UD Ancient Greek treebanks (Perseus, PROIEL)
    - Replaces a v0 CNN that capped at 96.9% mutable accuracy

    ### Source

    - **Model:** [latincy-diacritics v0.1.0](https://huggingface.co/latincy/latincy-diacritics) on Hugging Face
    - **Code:** [latincy-diacritics](https://github.com/diyclassics/latincy-diacritics) on GitHub
    """)
