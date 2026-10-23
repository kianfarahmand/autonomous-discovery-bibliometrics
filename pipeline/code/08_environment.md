# 08 - Environment and package versions

Recovered from the preserved conda environment that executed the analysis:
`~/.claude-science.old/conda/envs/python`

The execution log records `conda_env` per cell: **98 of 107 Python cells ran in the `python`
environment**; the remaining 9 ran in the control-plane kernel (`_operon`), which performs no
numerical work. No environment snapshot was captured with the artifacts, so these versions are
read from the environment's own `conda-meta` and `*.dist-info` records rather than from a
lockfile written at run time.

## Versions used for every reported number

| Package | Version |
|---|---|
| Python | 3.11.16 |
| pandas | 2.3.3 |
| numpy | 2.4.6 |
| scikit-learn | 1.9.1 |
| scipy | 1.17.1 |
| networkx | 3.6.1 |
| matplotlib | 3.11.2 |
| requests | 2.34.2 |
| joblib | 1.6.0 |
| threadpoolctl | 3.7.0 |

Full listings: `conda_packages_full.txt` (127 conda packages),
`pip_dist_info_full.txt` (48 distributions).

## Caveat

These are the versions present in that environment when it was preserved on 2026-10-07. The
environment was not modified between the analysis and the preservation as far as the record
shows, but no run-time lockfile exists to prove it. Treat the table as the environment of record,
not as a verified run-time snapshot.
