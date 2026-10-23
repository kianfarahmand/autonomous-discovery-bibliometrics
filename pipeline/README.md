# Pipeline: retrieval, screening, classification and analysis

The code that built the corpus and every reported number, recovered from the execution log of the
original analysis session. The rest of this repository (`../data`, `../code`) is enough to
reproduce the figures and statistics from the classified corpus; this folder documents how the
corpus and its classifications were produced.

```
00_RUN_ORDER.csv      index of all 121 logged operations in the original session
code/                 recovered analysis code, in run order (01 to 09, plus ALL_CELLS_chronological.py)
prompts/              screening rule and classification rule, verbatim
model_responses/      raw model responses for every screening and classification call
environment/          full conda and pip package listings
verification/         replay check that reproduces the published classifications
```

## Which file does what

| Step | File | Original session cells |
|---|---|---|
| OpenAlex retrieval: phrase queries, recall queries, snowballing, deduplication, document-type filter | `code/01_retrieval_openalex.py` | 3-15, 20-21, 27-35, 69, 72-73, 87 |
| Relevance screening | `code/02_relevance_screening.py`, `prompts/screening_rule_RULE.txt` | 16-19, 23-26, 68, 70-71 |
| Domain and implemented-stage classification | `code/03_domain_stage_llm_classification.py`, `prompts/classification_rule_CLS_RULE.txt` | 101-102 |
| Keyword (regular-expression) stage classification | `code/04_regex_stage_classification.py` | 49 (first pass), 77 (final) |
| Precision audit sampling | `code/05_precision_audit.py` | 19, 24 (first pass), 74 (final) |
| Clustering, network, statistics | `code/06_analysis_clustering_network_stats.py` | 39-47, 50-51, 75-79, 102-105, 111 |
| Figures of the earlier manuscript version | `code/07_figures.py`, `code/10_submitted_figure_revisions/` | 36-38, 44-45, 48, 52-53, 80-86, 106-107 |
| Package versions | `code/08_environment.md` | |
| Manuscript assembly and session administration | `code/09_manuscript_tables_and_session_admin.py` | remaining cells |

These are notebook-style session cells, not standalone scripts: later cells depend on state
built by earlier ones. Where the session contains a superseded first pass and a final pass, the
reported numbers come from the later cells (corpus: cell 87; high-precision screening: cell 71;
keyword stage: cell 77; clustering and statistics: cells 75-79 and 102-105).

## Model and settings

Screening and classification used `claude-haiku-4-5-20251001`, as reported in every archived
response payload in `model_responses/`.

- Screening: batches of 25 records, `max_tokens=1500`, 8 concurrent requests
- Classification: batches of 20 records, `max_tokens=1800`, 8 concurrent requests
- Temperature: not set by the calling code and not reported in the responses
- Parsing: the first `[...]` span of each response was read as JSON. For classification, all
  1,923 records parsed and all 97 responses ended normally (no truncation).

`model_responses/INDEX.json` maps each response file to the session cell that produced it.

## Verify the classifications

```
python verification/verify_classification_replay.py
```

Expected output:

```
parsed: 1923 unparsed: 0
agreement with published stage_llm: 1.0
closed-loop replayed: 363 | published: 363
```

This replays the recorded prompt and parser against the archived responses and reproduces the
published `stage_implemented` column exactly. It needs only pandas, no API key and no network.

## Random seeds

- Precision sample (final): corpus sorted by OpenAlex id, then `sample(100, random_state=7)` (cell 74)
- TF-IDF reduction: `TruncatedSVD(n_components=120, random_state=0)`
- Final clustering: `KMeans(n_clusters=15, n_init=25, random_state=0)`
- Stability: seeds 1 to 4 at 15 clusters, and 10, 12, 14, 18, 20 clusters at seed 0
- t-SNE: `TSNE(n_components=2, perplexity=30, init="pca", random_state=0)`

## Environment

Python 3.11.16, pandas 2.3.3, numpy 2.4.6, scikit-learn 1.9.1, scipy 1.17.1, networkx 3.6.1,
matplotlib 3.11.2, read from the preserved environment that ran the analysis. No run-time
lockfile was captured. Full listings are in `environment/`.

## Limitations of this record

1. Re-running retrieval needs an OpenAlex API key and will not return exactly this corpus, because
   OpenAlex changes over time. The corpus in `../data` is the October 2026 snapshot.
2. Re-running screening or classification needs access to the same model. The original calls used
   a platform interface (`host.llm`) that is not available elsewhere; prompts, batch sizes, model
   and parser are fully specified here, and `model_responses/` allows verification without
   re-running.
3. Temperature was not recorded, and no run-time lockfile exists.
4. The collaboration network in session cell 76 was built from author-level affiliations fetched
   from OpenAlex (112 institutions, 480 links). The network reported in the article is rebuilt by
   `../code/build_network.py` from the affiliation lists stored in the corpus file, so that it can
   be reproduced from this repository (117 institutions, 385 links). Both rank Lawrence Berkeley
   National Laboratory first by betweenness.
5. Manual check records: see `../hand_checks/` once added.

## Changes from the session record

The only edits to the recovered code are: long dashes inside strings and comments replaced by
hyphens (also inside the archived model response text); local file paths removed from `00_RUN_ORDER.csv`; and the verification script's input
path pointed at `../data/corpus_screened_classified.csv`. Analysis logic is unchanged.
