"""
verification/verify_classification_replay.py

NOT part of the original run. Paths adapted for this repository: it reads ../data/corpus_screened_classified.csv. Written during recovery to demonstrate that the recovered
prompt (prompts/classification_rule_CLS_RULE.txt) and the recovered parser (code/
03_domain_stage_llm_classification.py, cell 101) reproduce the published stage_llm column
exactly when replayed against the archived model responses in model_responses/.

Result when run: 1923/1923 records parsed, 0 unparsed, row-level agreement 1.0,
closed-loop count 363, matching the submitted manuscript.
"""
import json, re, collections, pandas as pd

import os
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(HERE, ".."))
corpus = pd.read_csv("../data/corpus_screened_classified.csv").rename(columns={"stage_implemented": "stage_llm"})
tape = json.load(open("model_responses/8468a5a2-ad2b-48f5-ba7d-e97ef69835ec-0.json", encoding="utf-8"))

recs = corpus[["id"]].to_dict("records")
CB = 20
cb = [recs[i:i+CB] for i in range(0, len(recs), CB)]
DOM, STG, bad = {}, {}, []
for b, rr in zip(cb, tape):
    ok = False
    if isinstance(rr, dict) and rr.get("text"):
        m = re.search(r"\[.*\]", rr["text"], re.S)
        if m:
            try:
                arr = json.loads(m.group(0))
                d = {int(o["n"]): o for o in arr if isinstance(o, dict) and "n" in o}
                for i, r in enumerate(b, start=1):
                    if i in d and "dom" in d[i] and "stage" in d[i]:
                        DOM[r["id"]] = str(d[i]["dom"]).strip().lower()
                        STG[r["id"]] = str(d[i]["stage"]).strip().lower()
                    else:
                        bad.append(r["id"])
                ok = True
            except Exception:
                pass
    if not ok:
        bad.extend([r["id"] for r in b])

STMAP = {"closed":"Closed loop", "auto":"Automated execution",
         "alg":"Algorithmic selection only", "pred":"Prediction / review only"}
rep = corpus.id.map(lambda w: STMAP.get(STG.get(w)))
print("parsed:", len(DOM), "unparsed:", len(bad))
print("agreement with published stage_llm:", float((rep == corpus.stage_llm).mean()))
print("closed-loop replayed:", int((rep == "Closed loop").sum()),
      "| published:", int((corpus.stage_llm == "Closed loop").sum()))
