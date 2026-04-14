import pandas as pd
import streamlit as st

from lexicon_helpers import load_lexicon_pipeline, sentence_picker

st.set_page_config(page_title="Paradigm Demo", layout="wide")
st.sidebar.header("Paradigm Demo")

st.title("Latin Paradigm Generator")
st.markdown(
    """
Pick a token from a Latin sentence to see its complete inflectional
paradigm — every form the lemma can take, generated from Whitaker's
Words inflection tables.
"""
)

model_name = st.sidebar.selectbox(
    "Choose model:",
    ("la_core_web_lg", "la_core_web_md", "la_core_web_sm"),
)

nlp = load_lexicon_pipeline(model_name)


def _feats_to_dict(feats) -> dict:
    """Normalize feats to a plain dict (accepts dict or UD-string)."""
    if isinstance(feats, dict):
        return feats
    if isinstance(feats, str):
        return dict(
            kv.split("=", 1) for kv in feats.split("|") if "=" in kv
        )
    return {}


tab1, tab2 = st.tabs(["Paradigm", "About"])

with tab1:
    text = sentence_picker("paradigm")

    if st.button("Analyze", key="paradigm_analyze"):
        doc = nlp(text)
        tokens = []
        for token in doc:
            if token.is_punct or token.is_space:
                continue
            paradigm = token._.paradigm or []
            # Serialize to plain dicts so we can stash in session state.
            serialized = [
                {
                    "form": f.get("form") if isinstance(f, dict) else f.form,
                    "lemma": f.get("lemma") if isinstance(f, dict) else f.lemma,
                    "upos": f.get("upos") if isinstance(f, dict) else f.upos,
                    "feats": _feats_to_dict(
                        f.get("feats") if isinstance(f, dict) else f.feats
                    ),
                }
                for f in paradigm
            ]
            tokens.append(
                {
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "paradigm": serialized,
                }
            )
        st.session_state["paradigm_tokens"] = tokens

    if "paradigm_tokens" in st.session_state:
        tokens = st.session_state["paradigm_tokens"]

        overview = pd.DataFrame(
            [
                {
                    "Token": t["text"],
                    "Lemma": t["lemma"],
                    "POS": t["pos"],
                    "Forms": len(t["paradigm"]),
                }
                for t in tokens
            ]
        )
        st.dataframe(overview, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("**Select a token to see its full paradigm:**")
        options = [
            f"{t['text']} — {t['lemma']} ({t['pos']})" for t in tokens
        ]
        idx = st.selectbox(
            "Token:",
            range(len(options)),
            format_func=lambda i: options[i],
            key="paradigm_token",
        )

        if idx is not None:
            t = tokens[idx]
            if not t["paradigm"]:
                st.info(
                    f"No paradigm available for {t['text']} "
                    "(unknown lemma or closed-class word)."
                )
            else:
                # Build a wide table: Form | UPOS | <feat columns>
                rows = []
                all_feats: list[str] = []
                for f in t["paradigm"]:
                    for k in f["feats"]:
                        if k not in all_feats:
                            all_feats.append(k)
                for f in t["paradigm"]:
                    row = {"Form": f["form"], "UPOS": f["upos"]}
                    for k in all_feats:
                        row[k] = f["feats"].get(k, "")
                    rows.append(row)

                st.markdown(
                    f"### `{t['lemma']}` — {len(t['paradigm'])} forms"
                )

                # Optional feature filter
                with st.expander("Filter by feature", expanded=False):
                    filters: dict[str, str] = {}
                    cols = st.columns(min(len(all_feats), 4) or 1)
                    for i, feat in enumerate(all_feats):
                        vals = sorted(
                            {f["feats"].get(feat, "") for f in t["paradigm"]}
                            - {""}
                        )
                        if not vals:
                            continue
                        with cols[i % len(cols)]:
                            choice = st.selectbox(
                                feat,
                                ["(any)"] + vals,
                                key=f"filter_{feat}",
                            )
                            if choice != "(any)":
                                filters[feat] = choice

                if filters:
                    rows = [
                        r
                        for r in rows
                        if all(r.get(k) == v for k, v in filters.items())
                    ]
                    st.caption(f"Showing {len(rows)} form(s) matching filters.")

                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.markdown(
        """
        ## About

        The `paradigm_generator` component attaches a full inflectional
        paradigm to each token via `token._.paradigm` — the inverse of
        Whitaker's analyzer: given a lemma, produce every form the lemma
        can take.

        ### Form counts to expect

        | POS | Forms | Notes |
        |-----|-------|-------|
        | Verb (regular) | 200–280 | Person × Number × Tense × Mood × Voice |
        | Adjective (3 endings) | ~84 | Case × Number × Gender × Degree |
        | Noun | 10–15 | Case × Number |
        | `sum` (irregular) | ~143 | Includes suppletive stems (s-, es-, fu-, fo-) |

        ### How it works

        Each entry in the shipped analyzer JSON knows its inflection
        pattern (declension or conjugation). The generator applies every
        applicable ending from the WW inflection tables, filters by age
        and frequency where appropriate, and returns forms tagged with
        UD morphological features.
        """
    )
