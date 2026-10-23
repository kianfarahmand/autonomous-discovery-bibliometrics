"""
03_domain_stage_llm_classification.py
Per-work domain and autonomy-stage classification -> dom_llm, stage_llm

VERBATIM cell sources recovered from the execution log of frame
dab9690f-bbbb-4695-a3e4-9e476b9fd59e (project proj_593d8a44f5b4).
Cells appear in original run order. Nothing has been rewritten, reordered or tidied.
Cells: [101, 102]
"""

# ======================================================================================
# CELL 101  |  run 2026-10-05 18:46:14Z  |  env=python  |  exit=ok
# ======================================================================================
CLS_RULE = """Classify each bibliographic record on two axes. Judge ONLY what the work itself
reports, not what it discusses, reviews, or proposes as future work.

AXIS 1 - primary material/application domain. Exactly one code:
  inorganic = inorganic solids, ceramics, solid-state synthesis
  organic   = organic synthesis, reaction discovery, medicinal chemistry
  polymer   = polymers, soft matter, colloids, hydrogels
  nano      = nanoparticles, nanocrystals, quantum dots, nanotubes
  bio       = proteins, enzymes, peptides, nucleic acids, synthetic biology, cells
  catalysis = catalysts and catalytic processes (hetero, electro, photo)
  battery   = batteries, electrolytes, photovoltaics, fuel cells
  thinfilm  = thin films, semiconductors, devices, deposition
  quantum   = quantum or photonic materials and devices, optoelectronics
  none      = no specific material class: methods, software, agents, reviews, infrastructure

AXIS 2 - highest autonomy stage ACTUALLY IMPLEMENTED in this work. Exactly one code:
  closed = an algorithm selects the next experiment AND apparatus executes it, iterated in
           a loop, demonstrated in this work
  auto   = physical experiments are automated or robotic, but experiment selection is not
           algorithmic or the loop is not closed
  alg    = algorithmic experiment selection or design (Bayesian optimisation, active learning)
           without automated physical execution in this work
  pred   = computation, prediction, simulation, benchmark, review, perspective, position
           paper, or software with no physical experiment reported in this work

A review, roadmap, perspective or position paper is ALWAYS stage=pred, whatever it describes.

Reply with ONLY a JSON array, one object per numbered record:
[{"n":1,"dom":"catalysis","stage":"closed"},...]
No prose, no code fences."""

recs = c2[["id","title","venue","year","abstract","type"]].to_dict("records")
def ctx(i, r):
    return (f'{i}. TITLE: {str(r["title"])[:170]}\n   TYPE: {r["type"]}  VENUE: '
            f'{str(r.get("venue") or "n/a")[:50]} ({r.get("year")})\n'
            f'   ABSTRACT: {str(r.get("abstract") or "")[:430]}')
CB = 20
cb = [recs[i:i+CB] for i in range(0, len(recs), CB)]
creqs = [{"prompt": CLS_RULE + "\n\nRECORDS:\n" + "\n".join(ctx(i+1, r) for i, r in enumerate(b)),
          "max_tokens": 1800} for b in cb]
cres = host.llm(creqs, max_concurrency=8)
DOM, STG, bad = {}, {}, []
for b, rr in zip(cb, cres):
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
                    else: bad.append(r["id"])
                ok = True
            except Exception: pass
    if not ok: bad.extend([r["id"] for r in b])
print(f"batches={len(cb)} classified={len(DOM)} unparsed={len(bad)}")
print("domain mix:", dict(Counter(DOM.values()).most_common()))
print("stage mix:", dict(Counter(STG.values()).most_common()))


# ======================================================================================
# CELL 102  |  run 2026-10-05 18:47:57Z  |  env=python  |  exit=ok
# ======================================================================================
from sklearn.metrics import adjusted_rand_score
DOMNAME = {"inorganic":"Inorganic solids & ceramics","organic":"Organic synthesis & reactions",
 "polymer":"Polymers & soft matter","nano":"Nanomaterials","bio":"Biomolecules & proteins",
 "catalysis":"Catalysis","battery":"Batteries & energy","thinfilm":"Thin films & devices",
 "quantum":"Quantum & photonic","none":"No material class named"}
STGNAME = {"pred":"Prediction / review only","alg":"Algorithmic selection only",
           "auto":"Automated execution","closed":"Closed loop"}
c2["dom_llm"] = c2.id.map(DOM).map(DOMNAME)
c2["stage_llm"] = c2.id.map(STG).map(STGNAME)
M3 = (pd.crosstab(c2.dom_llm, c2.stage_llm)
        .reindex(columns=[STGNAME[k] for k in ("pred","alg","auto","closed")], fill_value=0))
M3["domain_total"] = M3.sum(axis=1)
M3["closed_loop_share"] = (M3["Closed loop"]/M3.domain_total).round(3)
mat = M3.drop(index="No material class named")
print(mat.sort_values("closed_loop_share", ascending=False).to_string())
print("\nno-material-class row:", M3.loc["No material class named","domain_total"],
      f"({M3.loc['No material class named','domain_total']/len(c2):.1%})",
      "| its closed-loop share:", M3.loc["No material class named","closed_loop_share"])
print("\nregex vs model closed-loop count:", 919, "->", int(M3['Closed loop'].sum()))

ari_seed = [adjusted_rand_score(km2.labels_, KMeans(n_clusters=15, n_init=25, random_state=s)
            .fit(Xr2).labels_) for s in (1,2,3)]
ari_k = {k: adjusted_rand_score(km2.labels_, KMeans(n_clusters=k, n_init=25, random_state=0)
         .fit(Xr2).labels_) for k in (13,14,16,17)}
print(f"\ncluster stability: ARI across seeds (k=15) = {[round(a,3) for a in ari_seed]}")
print("ARI vs neighbouring k:", {k: round(v,3) for k,v in ari_k.items()})


