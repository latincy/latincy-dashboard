import streamlit as st
import spacy
from spacy_streamlit import visualize_ner

st.set_page_config(page_title="NER Demo", layout="wide")
st.sidebar.header("NER Demo")

default_text = """Iason et Medea e Thessalia expulsi ad urbem Corinthum venerunt, cuius urbis Creon quidam regnum tum obtinebat."""

st.title("Latin Named Entity Recognition")

st.markdown(
    """
This demo highlights **named entities** in Latin text — people, places,
groups, events, works, and dates — using LatinCy's NER component.

**Entity types:** PERSON, NORP, GPE, LOC, EVENT, WORK, DATE
"""
)

model_selectbox = st.sidebar.selectbox(
    "Choose model:", ("la_core_web_lg", "la_core_web_md", "la_core_web_sm")
)


@st.cache_resource
def load_model(model_name):
    return spacy.load(model_name)


nlp = load_model(model_selectbox)

tab1, tab2 = st.tabs(["Recognize", "About"])

with tab1:
    text = st.text_area(
        "Enter Latin text to analyze (max ~200 tokens):", value=default_text, height=200
    )

    if st.button("Find Entities"):
        tokens = text.split()
        if len(tokens) > 200:
            st.warning("Text trimmed to ~200 tokens.")
            text = " ".join(tokens[:200])
        doc = nlp(text)
        ner_labels = nlp.get_pipe("ner").labels
        visualize_ner(doc, labels=ner_labels, show_table=False, title="")

with tab2:
    st.markdown("""
    ## About

    **Named Entity Recognition (NER)** is the task of identifying and
    classifying named entities — such as people, places, and events — in
    unstructured text. LatinCy's NER component locates spans of tokens that
    refer to real-world entities and assigns each span a category label.

    ### Entity Types

    | Label | Description | Examples |
    |-------|-------------|----------|
    | **PERSON** | Named individuals | *Cicero*, *Caesar*, *Medea* |
    | **NORP** | Nationalities, religious/political groups | *Belgae*, *Aquitani*, *Romani* |
    | **GPE** | Geo-political entities (cities, provinces, states) | *Roma*, *Carthago*, *Athenae* |
    | **LOC** | Non-GPE locations (rivers, mountains, regions) | *Rhenus*, *Alpes*, *Gallia* |
    | **EVENT** | Named battles, wars, festivals | *Pharsalia*, *Saturnalia* |
    | **WORK** | Titles of literary or artistic works | *Aeneis*, *Metamorphoses* |
    | **DATE** | Temporal expressions | *Idibus Martiis*, *anno consulatus* |

    ### Training Data

    The NER model was trained on manually annotated Latin texts from
    multiple sources:

    - **Tesserae texts** — a broad corpus of classical Latin prose and poetry
    - **DCD annotations** — annotations derived from Augustine's
      *De Civitate Dei*
    - **Biblical texts** — annotated passages from the Vulgate

    These sources span historical prose, poetry, philosophical works, and
    biblical text, giving the model exposure to diverse entity contexts.

    ### Model Performance

    NER F1 scores by pipeline size:

    | Pipeline | NER F1 |
    |----------|--------|
    | **la_core_web_sm** | 80.4% |
    | **la_core_web_md** | 82.2% |
    | **la_core_web_lg** | 82.6% |
    | **la_core_web_trf** | 84.8% |

    Larger pipelines benefit from richer word vectors (md, lg) or a
    transformer encoder (trf), which improve the model's ability to
    disambiguate entities from common nouns and adjectives.

    ### Interpreting Entity Annotations

    Entities are shown as highlighted spans in the text. Each span is
    labeled with its entity type. A few tips for interpretation:

    - **Overlapping categories:** A word like *Romani* could be NORP
      (the Roman people) or GPE (the Roman state), depending on context.
      The model picks the most likely label, but ambiguous cases exist.
    - **Boundary errors:** The model may occasionally include or exclude
      a word at the edge of a multi-token entity. Check the full span.
    - **Unknown entities:** Rare names not seen in training may be missed.
      Larger models generally have better recall on uncommon entities.

    ### Source

    [GitHub: diyclassics/latincy](https://github.com/diyclassics/latincy)
    """)
