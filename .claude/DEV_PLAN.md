# Development Plan: latincy-dashboard

**LatinCy Release Target:** v3.9.0

## Current Status

Streamlit app with 8 interactive demos, deployed to HF Spaces (latincy.streamlit.app). All demos functional against v3.8.0 models. Recent work: U/V normalizer demo added (Feb 9).

## Current Focus

**Waiting for v3.9.0 pipeline release** to update models. Minor polish tasks available now.

## Tasks

### v3.9.0 Model Update (blocked on latincy-pipelines)
- [ ] Update requirements.txt model URLs to v3.9.0 wheels
- [ ] Test all 8 demos against v3.9.0 models
- [ ] Verify NER demo handles any new entity types or label changes
- [ ] Verify similarity demo works with retrained floret vectors
- [ ] Update README model version references
- [ ] Redeploy to HF Spaces

### About Tabs for All Demos
- [ ] Add About tab to parsing demo (UD column explanations, links)
- [ ] Add About tab to custom label demo (DCC Core vocab explanation)
- [ ] Add About tab to senter demo (model info, accuracy, links)
- [ ] Add About tab to NER demo (entity types, training data sources)
- [ ] Add About tab to dependency demo (UD deprel reference)
- [ ] Add About tab to similarity demo (floret vectors explanation)
- [ ] Add About tab to morphology demo (UD feature inventory for Latin)
- U/V normalizer demo already has About tab — use as template

### Known Issues
- [ ] Senter splits on "pl." abbreviation (tracked in latincy-pipelines)
- [ ] Download button resets Streamlit app (upstream Streamlit issue)

### Future Enhancements
- [ ] Add concordance/KWIC demo (when latincy-readers is on PyPI)
- [ ] Add lemmatizer comparison demo (lookup vs trainable)
- [ ] Consider adding trf model option (requires GPU or patience)

## Completed

- [x] 8 interactive demos implemented (parsing, custom labels, senter, NER, dependency, similarity, morphology, U/V normalizer)
- [x] Deployed to HF Spaces
- [x] README updated with model versions (v3.8.0) and SDK (1.45.1)
- [x] Fixed morphology word selector session state bug (2026-02-08)
- [x] U/V normalizer demo with About tab (2026-02-09)

## Notes

- **Deployment:** Push to `space` remote for HF Spaces
- **Models:** la_core_web_{sm,md,lg} v3.8.0 from HuggingFace
- **Dependencies:** latincy-uv (git URL), spacy-lookups-data (git URL)
- **Pattern:** Each demo is self-contained in `pages/N_demo_name.py`
