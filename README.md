# Data and code: Implemented versus discussed autonomy

Supporting data and code for: Farahmand, K. "Implemented versus discussed autonomy: A screened bibliometric analysis of the autonomous scientific discovery literature." Submitted to *Quantitative Science Studies*.

Author: Kian Farahmand, Department of Materials Science and Engineering, Shiraz University, Shiraz, Iran (k3farahmand@gmail.com)

Retrieval date: OpenAlex records retrieved to 3 October 2026. Citation counts are OpenAlex snapshots from October 2026. The 2026 publication year is partial.

## Contents

### data/

| File | Rows | Contents |
|---|---|---|
| `corpus_screened_classified.csv` | 1,923 | The screened corpus, one row per work, with OpenAlex metadata and all classifications (column dictionary below) |
| `stage_keyword_vs_implemented.csv` | 5 | Cross-tabulation of keyword stage against implemented stage (Table 2 of the paper) |
| `domain_by_stage.csv` | 10 | Material domain by implemented stage (Table 3, Figure 3a) |
| `annual_structure.csv` | 12 | Works per year, preprint share, industry and national laboratory shares (Figure 1a, 1b) |
| `affiliations_by_country.csv` | 30 | Author-level affiliation counts by country (Figure 1d) |
| `affiliations_by_institution.csv` | 40 | Author-level affiliation counts by institution |
| `subfield_summary.csv` | 15 | Per-cluster size, recency, closed-loop and no-material rates, median citations (Figure 4b, Table S3) |
| `subfield_by_domain.csv` | 15 | Cluster by material domain counts |
| `collaboration_network_nodes.csv` | 117 | Institutions on at least eight works, with degree, betweenness and most frequent family (Figure 5a) |
| `collaboration_network_edges.csv` | 385 | Institution pairs sharing at least two works |
| `named_platforms.csv` | 15 | Named platforms with works naming them, first year and citations (Figure 5b) |
| `seminal_works.csv` | 69 | Most-cited and most central works, with CrossRef verification and retraction status |
| `robustness_checks.csv` | 6 | Robustness checks recorded by the pipeline (Table S4) |
| `gap_analysis_earlier_corpus.csv` | 14 | Under-populated intersections and verdicts from the earlier corpus version (Table S5) |
| `query_set.json` | | Query phrases, hit counts, rejected phrases, recall validation and corrections |
| `screening_rule.txt` | | Verbatim relevance screening instruction |

### code/

| File | Purpose |
|---|---|
| `build_network.py` | Rebuilds the collaboration network files from the corpus |
| `reproduce_figures.py` | Regenerates Figures 1 to 5 into `code/figures/` |
| `reproduce_statistics.py` | Prints every statistic reported in the paper (kappa, confidence intervals, chi-squared, Spearman, Mann-Whitney, annual rates) |

Run from inside `code/` with Python 3.10 or later, pandas, numpy, scipy, scikit-learn, networkx and matplotlib.

### pipeline/

The code that produced the corpus and its classifications: OpenAlex retrieval, relevance screening, domain and implemented-stage classification with `claude-haiku-4-5-20251001`, the keyword classifier, clustering and statistics, recovered from the original analysis session, with the prompts and every raw model response. `pipeline/verification/verify_classification_replay.py` reproduces the published classifications exactly from the archived responses. See `pipeline/README.md`.

## Column dictionary for corpus_screened_classified.csv

| Column | Meaning |
|---|---|
| `id`, `doi` | OpenAlex work ID and DOI |
| `title`, `year`, `date`, `type`, `venue`, `venue_type`, `publisher`, `lang`, `abstract` | OpenAlex metadata |
| `cites` | OpenAlex citation count, October 2026 snapshot |
| `n_authors`, `first_author`, `institutions`, `countries`, `n_countries`, `is_intl` | Authorship and affiliation fields |
| `has_company`, `has_facility`, `has_edu` | Work has at least one industry, national laboratory or government, or university affiliation |
| `openalex_topic`, `openalex_subfield`, `openalex_field`, `openalex_domain`, `topics_all` | OpenAlex topic classification of the work |
| `retrieval_stratum` | `high_precision`, `recall_oriented` or `citation_snowball` |
| `matched_phrases`, `subfield_seed` | Query phrases matched and the seed subfield of the phrase |
| `n_refs`, `in_corpus_cites` | Reference count, and citations received from other corpus works |
| `material_domain` | Primary material or application domain (per-work classification) |
| `stage_implemented` | Highest implemented autonomy stage (per-work classification) |
| `stage_keyword` | Autonomy stage assigned by the regular-expression classifier, for comparison |
| `cluster_id`, `cluster_name`, `designation`, `family` | Subfield cluster from TF-IDF abstract clustering and its family |
| `tsne_x`, `tsne_y` | Two-dimensional t-SNE coordinates used for display |

## Licence

Code: MIT (`LICENSE`). Data: CC BY 4.0 (`LICENSE-DATA.md`).

## Notes

Long dashes in source titles and text fields have been normalized to hyphens. Abstracts and metadata come from OpenAlex and are released under CC0. The derived classifications and tables are released under CC BY 4.0.

## Citation

Farahmand, K. (2026). Screened corpus, classifications and code for "Implemented versus discussed autonomy" [Data set and software]. Zenodo. [DOI to be assigned]
