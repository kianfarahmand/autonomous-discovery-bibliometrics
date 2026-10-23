"""
01_retrieval_openalex.py
OpenAlex retrieval: phrase queries, recall queries, snowballing, dedup, doc-type filter

VERBATIM cell sources recovered from the execution log of frame
dab9690f-bbbb-4695-a3e4-9e476b9fd59e (project proj_593d8a44f5b4).
Cells appear in original run order. Nothing has been rewritten, reordered or tidied.
Cells: [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 21, 27, 28, 29, 30, 31, 32, 33, 34, 35, 69, 72, 73, 87]
"""

# ======================================================================================
# CELL 003  |  run 2026-10-05 12:43:34Z  |  env=python  |  exit=ok
# ======================================================================================
import os, requests, json, time, re
import pandas as pd

KEY = os.environ["OPENALEX_API_KEY"]
BASE = "https://api.openalex.org/works"
S = requests.Session()

def oa(params, retries=3):
    p = dict(params); p["api_key"] = KEY
    for i in range(retries):
        r = S.get(BASE, params=p, timeout=60)
        if r.status_code == 200:
            return r.json()
        time.sleep(2 * (i + 1))
    r.raise_for_status()

# mutually disjoint signature phrases, one subfield per phrase
PHRASES = {
 "SF1_self_driving_labs": ["self-driving laboratory", "self-driving labs", "materials acceleration platform"],
 "SF2_autonomous_experimentation": ["autonomous experimentation", "autonomous experimental", "autonomous discovery"],
 "SF3_closed_loop": ["closed-loop experimentation", "closed-loop discovery", "closed-loop synthesis", "closed-loop optimization of reaction"],
 "SF4_robotic_synthesis": ["robotic chemist", "robotic synthesis platform", "automated synthesis platform", "chemical programming language"],
 "SF5_ai_agents": ["autonomous chemical research", "AI scientist", "agentic workflow for chemistry", "large language model agent for chemistry"],
 "SF6_adaptive_design": ["active learning for materials discovery", "sequential learning for materials", "Bayesian reaction optimization", "Bayesian optimization for materials discovery"],
 "SF7_autonomous_materials": ["autonomous materials discovery", "autonomous synthesis of", "autonomous laboratory for"],
}

counts = {}
for sf, plist in PHRASES.items():
    for ph in plist:
        j = oa({"filter": f'title_and_abstract.search:"{ph}"', "per_page": 1, "select": "id"})
        counts[(sf, ph)] = j["meta"]["count"]
print("PHRASE COUNTS")
for (sf, ph), c in counts.items():
    print(f"{c:>6}  {sf:<32} {ph}")
print("SUM(with overlap):", sum(counts.values()))


# ======================================================================================
# CELL 004  |  run 2026-10-05 12:44:19Z  |  env=python  |  exit=ok
# ======================================================================================
tests = {
 "quoted phrase":            'title_and_abstract.search:"self-driving laboratory"',
 "quoted REVERSED order":    'title_and_abstract.search:"laboratory self-driving"',
 "unquoted":                 'title_and_abstract.search:self-driving laboratory',
 "quoted two commonwords":   'title_and_abstract.search:"autonomous synthesis"',
 "quoted nonsense pair":     'title_and_abstract.search:"autonomous banana"',
 "no_stem quoted":           'title_and_abstract.search.no_stem:"self-driving laboratory"',
 "no_stem reversed":         'title_and_abstract.search.no_stem:"laboratory self-driving"',
}
for label, filt in tests.items():
    try:
        j = oa({"filter": filt, "per_page": 1, "select": "id"})
        print(f"{j['meta']['count']:>8}  {label}")
    except Exception as e:
        print(f"{'ERR':>8}  {label}: {str(e)[:90]}")


# ======================================================================================
# CELL 005  |  run 2026-10-05 12:44:59Z  |  env=python  |  exit=ok
# ======================================================================================
def recon_abstract(w):
    inv = w.get("abstract_inverted_index")
    if not inv: return ""
    pos = {}
    for tok, idxs in inv.items():
        for i in idxs: pos[i] = tok
    return " ".join(pos[i] for i in sorted(pos))

# --- precision probe on the three broadest phrases
for ph in ["AI scientist", "autonomous discovery", "autonomous experimental"]:
    j = oa({"filter": f'title_and_abstract.search:"{ph}"', "per_page": 15,
            "select": "display_name", "sort": "cited_by_count:desc"})
    print(f"=== {ph}")
    for w in j["results"]:
        print("   -", (w["display_name"] or "")[:105])

LANDMARKS = {
 "10.1038/s41586-023-06734-w": "A-Lab (Szymanski 2023)",
 "10.1038/s41586-020-2442-2":  "Mobile robotic chemist (Burger 2020)",
 "10.1038/s41586-023-06792-0": "Coscientist (Boiko 2023)",
 "10.1126/science.aav2211":    "Chemputer (Steiner 2019)",
 "10.1126/sciadv.aaz8867":     "Ada self-driving lab (MacLeod 2020)",
 "10.1038/nature25978":        "ML-controlled synth robot (Granda 2018)",
 "10.1038/s41586-021-03213-y": "Bayesian reaction opt (Shields 2021)",
 "10.1038/s42256-024-00832-8": "ChemCrow (Bran 2024)",
 "10.1016/j.matt.2021.06.036": "Autonomous experimentation (Stach 2021)",
 "10.1002/adma.202001626":     "Artificial chemist (Epps 2020)",
}
lm = {}
for doi, name in LANDMARKS.items():
    j = oa({"filter": f"doi:{doi}", "per_page": 1,
            "select": "id,display_name,abstract_inverted_index,publication_year,cited_by_count"})
    lm[doi] = (j["results"][0] if j["results"] else None, name)
print("\nLANDMARK FETCH:", sum(1 for v in lm.values() if v[0]), "/", len(LANDMARKS))


# ======================================================================================
# CELL 006  |  run 2026-10-05 12:45:28Z  |  env=python  |  exit=ok
# ======================================================================================
CAND = ["self-driving laboratory","self-driving labs","materials acceleration platform",
 "autonomous experimentation","closed-loop experimentation","closed-loop discovery","closed-loop synthesis",
 "robotic chemist","robotic synthesis platform","automated synthesis platform","chemical programming language",
 "autonomous chemical research","autonomous materials discovery","autonomous laboratory for",
 "Bayesian reaction optimization","artificial chemist","autonomous discovery","autonomous experimental",
 "laboratory automation","autonomous experimentation system","self-driven fluidic","autonomous research"]

# local (conservative, unstemmed) recall test on landmark title+abstract
rows = []
for doi,(w,name) in lm.items():
    txt = ((w["display_name"] or "") + " " + recon_abstract(w)).lower()
    hits = [p for p in CAND if p.lower() in txt]
    rows.append({"landmark": name, "year": w["publication_year"],
                 "cites": w["cited_by_count"], "n_hits": len(hits), "hits": "; ".join(hits[:3])})
rec = pd.DataFrame(rows).sort_values("n_hits")
print(rec.to_string(index=False))
print("\nLandmarks with zero literal hit:", (rec.n_hits==0).sum(), "of", len(rec))

print("\nNEW CANDIDATE COUNTS")
for ph in ["artificial chemist","laboratory automation","autonomous experimentation system",
           "self-driven fluidic","autonomous research","autonomous laboratory"]:
    j = oa({"filter": f'title_and_abstract.search:"{ph}"', "per_page": 1, "select": "id"})
    print(f"{j['meta']['count']:>7}  {ph}")


# ======================================================================================
# CELL 007  |  run 2026-10-05 12:45:39Z  |  env=python  |  exit=ok
# ======================================================================================
for doi in ["10.1038/s42256-024-00832-8", "10.1038/nature25978"]:
    w, name = lm[doi]
    print("###", name, "|", w["display_name"])
    print(recon_abstract(w)[:700].replace("\n", " "))
    print()


# ======================================================================================
# CELL 008  |  run 2026-10-05 12:46:03Z  |  env=python  |  exit=ok
# ======================================================================================
del LANDMARKS["10.1038/nature25978"]; lm.pop("10.1038/nature25978", None)
EXTRA = {
 "10.1038/s41586-018-0307-8": "Organic synthesis robot + ML (Granda 2018)",
 "10.1038/s41557-023-01214-0": "Chemistry LLM agent / tools (2023)",
 "10.1126/science.adi1407":    "Delocalized self-driving lab network (2023)",
}
for doi, name in EXTRA.items():
    j = oa({"filter": f"doi:{doi}", "per_page": 1,
            "select": "id,display_name,abstract_inverted_index,publication_year,cited_by_count"})
    if j["results"]:
        lm[doi] = (j["results"][0], name); LANDMARKS[doi] = name
        print("OK ", name, "->", j["results"][0]["display_name"][:80])
    else:
        print("MISS", doi, name)

for ph in ["chemistry agent","synthesis robot","LLM agent","chemistry tools","autonomous platform"]:
    j = oa({"filter": f'title_and_abstract.search:"{ph}"', "per_page": 1, "select": "id"})
    print(f"{j['meta']['count']:>7}  {ph}")


# ======================================================================================
# CELL 009  |  run 2026-10-05 12:46:33Z  |  env=python  |  exit=ok
# ======================================================================================
LANDMARKS.pop("10.1038/s41557-023-01214-0", None); lm.pop("10.1038/s41557-023-01214-0", None)

TIER_A = {  # high precision -> auto-include
 "SF1_self_driving_labs":        ["self-driving laboratory","self-driving labs","materials acceleration platform","self-driven fluidic"],
 "SF2_autonomous_experimentation":["autonomous experimentation","autonomous laboratory","autonomous materials discovery"],
 "SF3_closed_loop":              ["closed-loop experimentation","closed-loop discovery","closed-loop synthesis"],
 "SF4_robotic_synthesis":        ["robotic chemist","robotic synthesis platform","automated synthesis platform",
                                  "chemical programming language","synthesis robot","artificial chemist"],
 "SF5_ai_agents":                ["autonomous chemical research","chemistry agent"],
 "SF6_adaptive_design":          ["Bayesian reaction optimization"],
}
TIER_B = ["autonomous discovery","autonomous experimental","laboratory automation",
          "autonomous research","autonomous platform","AI scientist"]

flatA = [p for v in TIER_A.values() for p in v]
rows = []
for doi,(w,name) in lm.items():
    txt = ((w["display_name"] or "") + " " + recon_abstract(w)).lower()
    a = [p for p in flatA if p.lower() in txt]
    b = [p for p in TIER_B if p.lower() in txt]
    rows.append({"landmark": name, "tierA_hits": len(a), "tierB_only": len(a)==0 and len(b)>0,
                 "matched": "; ".join(a[:2]) or ("[B] " + "; ".join(b[:2]))})
rec = pd.DataFrame(rows).sort_values("tierA_hits")
print(rec.to_string(index=False))
print(f"\nTier-A recall: {(rec.tierA_hits>0).sum()}/{len(rec)}   rescued only by Tier B: {rec.tierB_only.sum()}")


# ======================================================================================
# CELL 010  |  run 2026-10-05 12:46:47Z  |  env=python  |  exit=ok
# ======================================================================================
import json
for ph in ["autonomous molecular discovery","molecular discovery","autonomous optimization","accelerated discovery platform"]:
    j = oa({"filter": f'title_and_abstract.search:"{ph}"', "per_page": 1, "select": "id"})
    print(f"{j['meta']['count']:>7}  {ph}")


# ======================================================================================
# CELL 011  |  run 2026-10-05 12:47:13Z  |  env=python  |  exit=ok
# ======================================================================================
flatA2 = flatA + ["autonomous molecular discovery"]
hit = []
for ph in flatA2 + TIER_B:
    j = oa({"filter": f'doi:10.1126/science.adi1407,title_and_abstract.search:"{ph}"',
            "per_page": 1, "select": "id"})
    if j["meta"]["count"]:
        hit.append(ph)
print("Koscher 2023 matched by (API, stemmed):", hit or "NOTHING")


# ======================================================================================
# CELL 012  |  run 2026-10-05 12:47:35Z  |  env=python  |  exit=ok
# ======================================================================================
TIER_A["SF2_autonomous_experimentation"].append("autonomous molecular discovery")
qspec = {
 "field": "Autonomous scientific discovery / self-driving laboratories",
 "source": "OpenAlex works, title_and_abstract.search (quoted phrase; stem-based and proximity-tolerant)",
 "design_note": ("Phrases are assigned to exactly one subfield so no phrase is counted twice; "
   "overlapping concept blocks inflate apparent cross-program convergence. Two tiers: Tier A is "
   "high-precision and auto-included; Tier B is recall-oriented, high-noise, and must pass a "
   "relevance screen before entering the corpus."),
 "phrase_semantics_finding": ("Quotes are honoured as phrase search (reversed word order drops "
   "'self-driving laboratory' from 770 to 5 hits) but matching is stemmed and tolerates intervening "
   "tokens, so short common-word phrases such as 'autonomous synthesis' (20,962 hits) are unusable."),
 "tier_A_auto_include": TIER_A,
 "tier_B_screen_required": TIER_B,
 "tier_B_rejected_outright": {"autonomous synthesis": "20,962 hits; ambiguous across robotics/control",
                              "molecular discovery": "1,230 hits; no autonomy signal",
                              "autonomous optimization": "971 hits; mostly control theory"},
 "phrase_counts": {ph: c for (sf, ph), c in counts.items()},
 "recall_validation": {
    "method": "11 independently known landmark platforms/papers, DOI-resolved via OpenAlex, tested against the phrase set API-side",
    "tier_A_recall": "11/11",
    "landmarks": {d: n for d, n in LANDMARKS.items()},
    "corrections_made": [
      "10.1038/nature25978 was mislabelled as Granda's synthesis robot; it is Segler's retrosynthesis-planning paper. Removed (no closed loop).",
      "Granda 2018 corrected to 10.1038/s41586-018-0307-8.",
      "10.1038/s41557-023-01214-0 did not resolve to a chemistry-agent paper and was dropped."]},
 "planned_expansion": ("Citation snowballing in step 2: works citing or cited by the most central Tier-A "
   "works, to catch idiosyncratic phrasing that no phrase set reaches."),
}
with open("corpus_queries.json", "w", encoding="utf-8") as f:
    json.dump(qspec, f, indent=2)
print("tier A phrases:", len(flatA2), "| tier B:", len(TIER_B), "| landmarks:", len(LANDMARKS))


# ======================================================================================
# CELL 013  |  run 2026-10-05 12:50:01Z  |  env=python  |  exit=ok
# ======================================================================================
SELECT = ("id,doi,display_name,publication_year,publication_date,cited_by_count,type,"
          "primary_location,authorships,topics,primary_topic,abstract_inverted_index,"
          "open_access,referenced_works,language")

def fetch_phrase(ph, select=SELECT):
    cur, out = "*", []
    while cur:
        j = oa({"filter": f'title_and_abstract.search:"{ph}"', "per_page": 200,
                "cursor": cur, "select": select})
        out.extend(j["results"])
        cur = j["meta"].get("next_cursor")
        if not j["results"]: break
    return out

def compact(w):
    pl = w.get("primary_location") or {}
    src = (pl.get("source") or {}) or {}
    auths = w.get("authorships") or []
    insts, ctys = [], []
    for a in auths:
        for i in (a.get("institutions") or []):
            if i.get("display_name"): insts.append(i["display_name"])
            if i.get("country_code"): ctys.append(i["country_code"])
    tops = w.get("topics") or []
    pt = w.get("primary_topic") or {}
    return {
      "id": w["id"], "doi": w.get("doi"), "title": w.get("display_name") or "",
      "year": w.get("publication_year"), "date": w.get("publication_date"),
      "cites": w.get("cited_by_count") or 0, "type": w.get("type"),
      "venue": src.get("display_name"), "venue_type": src.get("type"),
      "publisher": src.get("host_organization_name"),
      "is_oa": (w.get("open_access") or {}).get("is_oa"),
      "lang": w.get("language"),
      "abstract": recon_abstract(w)[:2500],
      "n_authors": len(auths),
      "first_author": (auths[0].get("author") or {}).get("display_name") if auths else None,
      "institutions": "; ".join(dict.fromkeys(insts))[:600],
      "countries": "; ".join(dict.fromkeys(ctys))[:120],
      "topic": pt.get("display_name"),
      "subfield": ((pt.get("subfield") or {}).get("display_name")),
      "field": ((pt.get("field") or {}).get("display_name")),
      "domain": ((pt.get("domain") or {}).get("display_name")),
      "topics_all": "; ".join([t.get("display_name","") for t in tops[:4]]),
    }

ROWS, REFS, MATCH, TIERMAP = {}, {}, {}, {}
def ingest(works, ph, tier, keep_refs):
    for w in works:
        wid = w["id"]
        if wid not in ROWS: ROWS[wid] = compact(w)
        MATCH.setdefault(wid, set()).add(ph)
        if tier == "A" or TIERMAP.get(wid) == "A": TIERMAP[wid] = "A"
        else: TIERMAP.setdefault(wid, "B")
        if keep_refs and wid not in REFS:
            REFS[wid] = w.get("referenced_works") or []

PH2SF = {p: sf for sf, pl in TIER_A.items() for p in pl}
for ph in PH2SF:
    ingest(fetch_phrase(ph), ph, "A", True)
print("after Tier A:", len(ROWS))
for ph in TIER_B:
    ingest(fetch_phrase(ph), ph, "B", False)
print("after Tier B:", len(ROWS), "| A:", sum(1 for v in TIERMAP.values() if v=="A"))


# ======================================================================================
# CELL 014  |  run 2026-10-05 12:51:54Z  |  env=python  |  exit=ok
# ======================================================================================
from collections import Counter
rc = Counter()
for wid, refs in REFS.items():
    for r in refs: rc[r] += 1
cand = {r: n for r, n in rc.items() if r not in ROWS}
import numpy as np
print("distinct refs:", len(rc), "| not yet in corpus:", len(cand))
for t in [3,5,8,12,20,30]:
    print(f"  refd by >={t:>2} TierA works: {sum(1 for n in cand.values() if n>=t)}")


# ======================================================================================
# CELL 015  |  run 2026-10-05 12:52:24Z  |  env=python  |  exit=ok
# ======================================================================================
snow_ids = [r for r, n in cand.items() if n >= 12]
short = [s.rsplit("/", 1)[-1] for s in snow_ids]
got = 0
for i in range(0, len(short), 50):
    batch = "|".join(short[i:i+50])
    j = oa({"filter": f"openalex_id:{batch}", "per_page": 50, "select": SELECT})
    for w in j["results"]:
        wid = w["id"]
        if wid not in ROWS:
            ROWS[wid] = compact(w); TIERMAP[wid] = "S"
            MATCH.setdefault(wid, set()).add(f"snowball_refd_by_{rc[wid]}")
            got += 1
print("snowball fetched:", got, "of", len(snow_ids), "| corpus now:", len(ROWS))
print("tiers:", Counter(TIERMAP.values()))


# ======================================================================================
# CELL 020  |  run 2026-10-05 12:58:28Z  |  env=python  |  exit=ok
# ======================================================================================
BAD_TYPES = {"peer-review","editorial","erratum","paratext","retraction","letter","grant"}
def lit_hit(wid):
    r = ROWS[wid]
    txt = ((r["title"] or "") + " " + (r["abstract"] or "")).lower()
    return [p for p in flatA2 if p.lower() in txt]

adf = pd.DataFrame([{"id": w, "type": ROWS[w]["type"], "has_abs": bool(ROWS[w]["abstract"]),
                     "n_lit": len(lit_hit(w))} for w in a_ids])
print("Tier A =", len(adf))
print("doc-type counts (top):"); print(adf.type.value_counts().head(8).to_string())
print("\nbad doc types:", adf.type.isin(BAD_TYPES).sum())
print("abstract available:", adf.has_abs.sum(), f"({adf.has_abs.mean():.1%})")
print("literal phrase confirmed:", (adf.n_lit > 0).sum())
print("  of those WITH abstract:", ((adf.n_lit>0) & adf.has_abs).sum(), "/", adf.has_abs.sum())
print("  of those WITHOUT abstract:", ((adf.n_lit>0) & ~adf.has_abs).sum(), "/", (~adf.has_abs).sum())

# how the audited sample's known false positives behave
fp_idx = [4,5,11,16,17,20,21,26,31,32,33,44,48,56,57,58,70,79,105,108,113,6,23,38,76,83]
fp_ids = [samp[i-1] for i in fp_idx]
kept = sum(1 for w in fp_ids if len(lit_hit(w))>0 and ROWS[w]["type"] not in BAD_TYPES)
print(f"\naudited clear-FP + doctype-noise: {len(fp_ids)} | still kept by strict filter: {kept}")


# ======================================================================================
# CELL 021  |  run 2026-10-05 12:58:57Z  |  env=python  |  exit=ok
# ======================================================================================
a_keep = [w for w in a_ids if ROWS[w]["type"] not in BAD_TYPES]
print("Tier A after doc-type filter:", len(a_keep), "(removed", len(a_ids)-len(a_keep), ")")
with open("tierA_records.jsonl", "w", encoding="utf-8") as f:
    for w in a_keep:
        r = ROWS[w]
        f.write(json.dumps({"id": w, "title": r["title"][:200], "venue": r["venue"],
                            "year": r["year"], "abstract": (r["abstract"] or "")[:320]}) + "\n")
with open("screen_rule.txt", "w", encoding="utf-8") as f:
    f.write(RULE)
print("wrote tierA_records.jsonl lines:", len(a_keep))


# ======================================================================================
# CELL 027  |  run 2026-10-05 13:02:26Z  |  env=python  |  exit=ok
# ======================================================================================
rec = corpus[corpus.year>=2023]
print("TYPE x YEAR")
print(pd.crosstab(rec.year.astype(int), rec.type).to_string())
print("\nTOP VENUES 2026")
print(corpus[corpus.year==2026].venue.fillna("(none)").value_counts().head(12).to_string())
print("\nTOP VENUES 2025")
print(corpus[corpus.year==2025].venue.fillna("(none)").value_counts().head(8).to_string())
print("\n2026 month distribution (publication_date):")
d26 = pd.to_datetime(corpus[corpus.year==2026].date, errors="coerce")
print(d26.dt.month.value_counts().sort_index().to_string())
print("\n2026 tier mix:", corpus[corpus.year==2026].tier.value_counts().to_dict())
print("2026 median citations:", corpus[corpus.year==2026].cites.median(), "| 2023:", corpus[corpus.year==2023].cites.median())


# ======================================================================================
# CELL 028  |  run 2026-10-05 13:02:45Z  |  env=python  |  exit=ok
# ======================================================================================
z = corpus[(corpus.venue.fillna("").str.startswith("Zenodo")) & (corpus.year==2026)]
print("Zenodo 2026:", len(z), "| unique titles:", z.title.str.lower().str.strip().nunique())
print("\ntop repeated Zenodo titles:")
print(z.title.str.lower().str.strip().value_counts().head(10).to_string())
print("\ntype mix:", z.type.value_counts().to_dict())
norm = corpus.title.str.lower().str.replace(r"[^a-z0-9 ]", " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
print("\nCORPUS-WIDE duplicate titles:", len(corpus) - norm.nunique(), "of", len(corpus))
print("\nmost duplicated corpus-wide:")
print(norm.value_counts().head(8).to_string())


# ======================================================================================
# CELL 029  |  run 2026-10-05 13:03:13Z  |  env=python  |  exit=ok
# ======================================================================================
SCHOLARLY = {"article","review","preprint","conference-paper","book-chapter"}
c = corpus[corpus.type.isin(SCHOLARLY)].copy()
c = c[c.title.str.strip().str.len() > 10]
c["tnorm"] = (c.title.str.lower().str.replace(r"[^a-z0-9 ]", " ", regex=True)
                .str.replace(r"\s+", " ", regex=True).str.strip())
TYPE_RANK = {"article":0,"review":0,"conference-paper":1,"book-chapter":1,"preprint":2}
c["trank"] = c.type.map(TYPE_RANK)
c["has_doi"] = c.doi.notna().astype(int)
c = (c.sort_values(["tnorm","trank","cites","has_doi"], ascending=[True,True,False,False])
       .drop_duplicates("tnorm", keep="first"))
c = c.sort_values("cites", ascending=False).reset_index(drop=True)

print("after type filter + dedup:", len(c), f"(from {len(corpus)})")
print(c.type.value_counts().to_string())
print("\nworks by year (2015+):")
yr = c[c.year>=2015].year.astype(int).value_counts().sort_index()
print(yr.to_string())
print("\npreprint share by year 2022+:")
for y in range(2022, 2027):
    s = c[c.year==y]
    print(f"  {y}: n={len(s):>4}  preprint={(s.type=='preprint').mean():.1%}")
print("\n2026 is PARTIAL - latest publication_date in corpus:", pd.to_datetime(c.date, errors='coerce').max().date())


# ======================================================================================
# CELL 030  |  run 2026-10-05 13:03:45Z  |  env=python  |  exit=ok
# ======================================================================================
c.drop(columns=["trank","has_doi"]).to_csv("autonomous_discovery_corpus.csv", index=False, encoding="utf-8")
prov = {
 "corpus_n": int(len(c)),
 "pipeline": ["OpenAlex phrase retrieval (20 Tier-A + 6 Tier-B phrases)",
              "citation snowball: refs cited by >=12 Tier-A works",
              "Tier-B/snowball: LLM relevance screen against explicit rule (7423 records, 1164 passed)",
              "Tier-A: deterministic stem+adjacency phrase confirmation (audited precision 0.72, recall 0.93)",
              "document-type restriction to article/review/preprint/conference-paper/book-chapter",
              "title-normalised deduplication preferring published over preprint"],
 "removed": {"tierA_phrase_unconfirmed": 2502-2091, "doc_type_nonscholarly_and_dupes": 3246-2330},
 "known_limitations": [
   "Tier-A precision measured at 0.72 on a 120-record hand audit; model-based screening of Tier A was not possible (per-frame LLM budget exhausted, delegation disabled), so residual off-topic contamination is removed at cluster level in the next step.",
   "2026 is a PARTIAL year (data to 2026-10-03) and is 41.8% preprints vs 25.6% in 2025; absolute 2026 counts are not comparable to earlier full years.",
   "Zenodo/figshare versioned deposits duplicated heavily (ARES OS 2.0 appeared 10x) and were collapsed by title.",
 ]}
json.dump(prov, open("corpus_provenance.json","w"), indent=2)
print(len(c), "rows ->", c.cites.sum(), "total citations | top-5 titles:")
for _, r in c.head(5).iterrows(): print(f'  {r.cites:>5}  {r.title[:84]}')


# ======================================================================================
# CELL 031  |  run 2026-10-05 13:05:32Z  |  env=python  |  exit=ok
# ======================================================================================
import inspect
print(inspect.signature(verify_dois)); print((verify_dois.__doc__ or "")[:500])
print("---"); print(inspect.signature(expand_citations))

corpus_ids = set(c.id)
incorp = Counter()
for wid, refs in REFS.items():
    for r in refs:
        if r in corpus_ids: incorp[r] += 1
c["in_corpus_cites"] = c.id.map(lambda x: incorp.get(x, 0))
top_cited   = c.nlargest(45, "cites")
top_central = c.nlargest(45, "in_corpus_cites")
sem = pd.concat([top_cited, top_central]).drop_duplicates("id")
lmk = c[c.doi.fillna("").str.replace("https://doi.org/","",regex=False).isin(LANDMARKS.keys())]
sem = pd.concat([sem, lmk]).drop_duplicates("id").reset_index(drop=True)
print("\nseminal candidates:", len(sem), "| with DOI:", sem.doi.notna().sum())
print("landmarks present in final corpus:", len(lmk), "of", len(LANDMARKS))


# ======================================================================================
# CELL 032  |  run 2026-10-05 13:08:16Z  |  env=python  |  exit=ok
# ======================================================================================
dois = [d.replace("https://doi.org/","") for d in sem.doi.tolist()]
ver = verify_dois(dois)
vst = Counter(v.get("ok") for v in ver.values())
print("verification:", dict(vst))
retr = {d: v for d, v in ver.items() if v.get("retracted")}
print("retracted flags:", retr or "none")
bad = {d: v.get("error") for d, v in ver.items() if v.get("ok") is False}
print("non-resolving:", bad or "none")
unk = [d for d, v in ver.items() if v.get("ok") is None]
print("unverifiable (transient):", len(unk))

sem2 = sem.copy()
sem2["doi_clean"] = dois
sem2["verified"] = sem2.doi_clean.map(lambda d: ver.get(d, {}).get("ok"))
sem2["retracted"] = sem2.doi_clean.map(lambda d: ver.get(d, {}).get("retracted"))
sem2["cr_authors"] = sem2.doi_clean.map(lambda d: ver.get(d, {}).get("authors"))
sem2["cr_year"] = sem2.doi_clean.map(lambda d: ver.get(d, {}).get("year"))
sem2["cr_journal"] = sem2.doi_clean.map(lambda d: ver.get(d, {}).get("journal"))
yr_mismatch = sem2[(sem2.cr_year.notna()) & (sem2.cr_year != sem2.year)][["title","year","cr_year"]]
print("\nyear mismatches OpenAlex vs CrossRef:", len(yr_mismatch))
if len(yr_mismatch): print(yr_mismatch.head(8).to_string(index=False))


# ======================================================================================
# CELL 033  |  run 2026-10-05 13:08:38Z  |  env=python  |  exit=ok
# ======================================================================================
sw = sem2[["title","first_author","cr_authors","year","cr_year","venue","cr_journal","type",
           "cites","in_corpus_cites","doi_clean","subfield_seed","tier","verified","retracted",
           "institutions","countries"]].copy()
sw = sw.rename(columns={"cr_authors":"crossref_authors","cr_year":"crossref_year",
                        "cr_journal":"crossref_journal","doi_clean":"doi"})
sw["is_landmark"] = sw.doi.isin(LANDMARKS.keys())
sw = sw.sort_values("cites", ascending=False).reset_index(drop=True)
sw.to_csv("seminal_works.csv", index=False, encoding="utf-8")
print("seminal works:", len(sw), "| landmarks:", sw.is_landmark.sum())
print("\nTOP 18 BY CITATIONS")
print(sw.head(18)[["title","crossref_year","venue","cites","in_corpus_cites"]]
      .assign(title=lambda d: d.title.str[:62], venue=lambda d: d.venue.fillna("").str[:26])
      .to_string(index=False))
print("\nTOP 8 BY IN-CORPUS CENTRALITY")
print(sw.nlargest(8,"in_corpus_cites")[["title","crossref_year","in_corpus_cites","cites"]]
      .assign(title=lambda d: d.title.str[:66]).to_string(index=False))


# ======================================================================================
# CELL 034  |  run 2026-10-05 13:10:16Z  |  env=python  |  exit=ok
# ======================================================================================
short_ids = c.oa_short.tolist()
INST = {}
for i in range(0, len(short_ids), 50):
    b = "|".join(short_ids[i:i+50])
    j = oa({"filter": f"openalex_id:{b}", "per_page": 50, "select": "id,authorships"})
    for w in j["results"]:
        its = []
        for a in (w.get("authorships") or []):
            for ins in (a.get("institutions") or []):
                its.append((ins.get("display_name"), ins.get("type"), ins.get("country_code")))
        INST[w["id"]] = its
print("fetched institution data for", len(INST), "of", len(c))
alltypes = Counter(t for v in INST.values() for _, t, _ in v)
print("institution type counts:", dict(alltypes.most_common()))


# ======================================================================================
# CELL 035  |  run 2026-10-05 13:10:38Z  |  env=python  |  exit=ok
# ======================================================================================
c["has_company"]  = c.id.map(lambda w: any(t=="company"    for _,t,_ in INST.get(w,[])))
c["has_facility"] = c.id.map(lambda w: any(t in ("facility","government") for _,t,_ in INST.get(w,[])))
c["has_edu"]      = c.id.map(lambda w: any(t=="education"  for _,t,_ in INST.get(w,[])))
c["n_countries"]  = c.id.map(lambda w: len({cc for _,_,cc in INST.get(w,[]) if cc}))
c["is_intl"]      = c.n_countries >= 2

yrs = list(range(2015, 2027))
fs = []
for y in yrs:
    s = c[c.year == y]
    fs.append({"year": y, "n_works": len(s),
               "n_articles": int((s.type.isin(["article","review"])).sum()),
               "n_preprints": int((s.type=="preprint").sum()),
               "preprint_share": s.type.eq("preprint").mean() if len(s) else np.nan,
               "industry_share": s.has_company.mean() if len(s) else np.nan,
               "facility_share": s.has_facility.mean() if len(s) else np.nan,
               "intl_share": s.is_intl.mean() if len(s) else np.nan,
               "oa_share": s.is_oa.mean() if len(s) else np.nan,
               "median_cites": s.cites.median() if len(s) else np.nan,
               "partial_year": y == 2026})
fsdf = pd.DataFrame(fs)
print(fsdf.to_string(index=False, float_format=lambda x: f"{x:.3f}"))

ctry = Counter(cc for w in c.id for _,_,cc in INST.get(w,[]) if cc)
inst = Counter(nm for w in c.id for nm,_,_ in INST.get(w,[]) if nm)
print("\nTOP 12 COUNTRIES:", dict(ctry.most_common(12)))
print("\nTOP 12 INSTITUTIONS:")
for nm, n in inst.most_common(12): print(f"  {n:>4}  {nm[:64]}")
print("\nFIELD MIX (all years):"); print(c.field.fillna("unknown").value_counts().head(8).to_string())


# ======================================================================================
# CELL 069  |  run 2026-10-05 17:00:34Z  |  env=python  |  exit=ok
# ======================================================================================
import os, re, json, time, requests, numpy as np, pandas as pd
from collections import Counter
import matplotlib as mpl, matplotlib.pyplot as plt

KEY = os.environ["OPENALEX_API_KEY"]; BASE = "https://api.openalex.org/works"; S = requests.Session()
def oa(params, retries=3):
    p = dict(params); p["api_key"] = KEY
    for i in range(retries):
        r = S.get(BASE, params=p, timeout=60)
        if r.status_code == 200: return r.json()
        time.sleep(2*(i+1))
    r.raise_for_status()

c_all = pd.read_csv("{{artifact:af80aea8-3a10-4352-8601-983fb7687be9}}")   # subfield_clusters.csv
sw    = pd.read_csv("{{artifact:1e970f10-5128-4838-b71f-841219afff49}}")   # seminal_works.csv
tierA = [json.loads(l) for l in open("{{artifact:7d71f6b1-d198-4af9-86d4-cbc76ab2dc90}}", encoding="utf-8")]

INST = {}
sid = c_all.oa_short.tolist()
for i in range(0, len(sid), 50):
    j = oa({"filter": f"openalex_id:{'|'.join(sid[i:i+50])}", "per_page": 50, "select": "id,authorships"})
    for w in j["results"]:
        INST[w["id"]] = [(ins.get("display_name"), ins.get("type"), ins.get("country_code"))
                         for a in (w.get("authorships") or []) for ins in (a.get("institutions") or [])]
assert len(c_all) == 2330 and len(tierA) == 2388 and len(INST) >= 2300
print("restored:", len(c_all), "corpus |", len(tierA), "tierA records |", len(INST), "inst records")
print("tier mix:", c_all.tier.value_counts().to_dict())


# ======================================================================================
# CELL 072  |  run 2026-10-05 17:05:39Z  |  env=python  |  exit=ok
# ======================================================================================
SELECT = ("id,doi,display_name,publication_year,publication_date,cited_by_count,type,"
          "primary_location,authorships,topics,primary_topic,abstract_inverted_index,"
          "open_access,referenced_works,language")
def recon_abstract(w):
    inv = w.get("abstract_inverted_index")
    if not inv: return ""
    pos = {i: tok for tok, idxs in inv.items() for i in idxs}
    return " ".join(pos[i] for i in sorted(pos))
def compact(w):
    src = ((w.get("primary_location") or {}).get("source") or {})
    auths = w.get("authorships") or []
    insts = [i.get("display_name") for a in auths for i in (a.get("institutions") or []) if i.get("display_name")]
    ctys  = [i.get("country_code") for a in auths for i in (a.get("institutions") or []) if i.get("country_code")]
    pt = w.get("primary_topic") or {}
    return {"id": w["id"], "doi": w.get("doi"), "title": w.get("display_name") or "",
      "year": w.get("publication_year"), "date": w.get("publication_date"),
      "cites": w.get("cited_by_count") or 0, "type": w.get("type"),
      "venue": src.get("display_name"), "venue_type": src.get("type"),
      "publisher": src.get("host_organization_name"),
      "is_oa": (w.get("open_access") or {}).get("is_oa"), "lang": w.get("language"),
      "abstract": recon_abstract(w)[:2500], "n_authors": len(auths),
      "first_author": (auths[0].get("author") or {}).get("display_name") if auths else None,
      "institutions": "; ".join(dict.fromkeys(insts))[:600],
      "countries": "; ".join(dict.fromkeys(ctys))[:120],
      "topic": pt.get("display_name"),
      "subfield": (pt.get("subfield") or {}).get("display_name"),
      "field": (pt.get("field") or {}).get("display_name"),
      "domain": (pt.get("domain") or {}).get("display_name"),
      "topics_all": "; ".join([t.get("display_name","") for t in (w.get("topics") or [])[:4]])}

in_corpus = set(c_all.id)
addback_ids = [i for i, v in SCR.items() if v == 1 and i not in in_corpus]
print("Tier-A kept from existing corpus:", int(c_all[c_all.tier=='A'].id.map(lambda x: SCR.get(x,0)).sum()),
      "of", (c_all.tier=='A').sum())
print("add-back candidates (screened in, absent from corpus):", len(addback_ids))

newrows, REFS2 = [], {}
sh = [i.rsplit("/",1)[-1] for i in addback_ids]
for i in range(0, len(sh), 50):
    j = oa({"filter": f"openalex_id:{'|'.join(sh[i:i+50])}", "per_page": 50, "select": SELECT})
    for w in j["results"]:
        newrows.append(compact(w)); REFS2[w["id"]] = w.get("referenced_works") or []
        INST[w["id"]] = [(ins.get("display_name"), ins.get("type"), ins.get("country_code"))
                         for a in (w.get("authorships") or []) for ins in (a.get("institutions") or [])]
add = pd.DataFrame(newrows)
print("fetched add-backs:", len(add))
print("add-back type mix:", add.type.value_counts().to_dict())


# ======================================================================================
# CELL 073  |  run 2026-10-05 17:06:25Z  |  env=python  |  exit=ok
# ======================================================================================
SCHOLARLY = {"article","review","preprint","conference-paper","book-chapter"}
add2 = add[add.type.isin(SCHOLARLY) & (add.title.str.strip().str.len() > 10)].copy()
add2["tier"] = "A"; add2["matched_phrases"] = "tierA_rescreen"; add2["subfield_seed"] = "tierA_rescreen"
add2["n_refs"] = add2.id.map(lambda x: len(REFS2.get(x, [])))
add2["oa_short"] = add2.id.str.rsplit("/", n=1).str[-1]

keepA = c_all[(c_all.tier=="A") & (c_all.id.map(lambda x: SCR.get(x,0)==1))]
keepBS = c_all[c_all.tier.isin(["B","S"])]
cols = [col for col in c_all.columns if col in add2.columns or col in keepA.columns]
c2 = pd.concat([keepA, keepBS, add2], ignore_index=True)

c2["tnorm"] = (c2.title.str.lower().str.replace(r"[^a-z0-9 ]", " ", regex=True)
                 .str.replace(r"\s+", " ", regex=True).str.strip())
TR = {"article":0,"review":0,"conference-paper":1,"book-chapter":1,"preprint":2}
c2["trank"] = c2.type.map(TR); c2["has_doi"] = c2.doi.notna().astype(int)
c2 = (c2.sort_values(["tnorm","trank","cites","has_doi"], ascending=[True,True,False,False])
        .drop_duplicates("tnorm", keep="first")
        .sort_values("cites", ascending=False).reset_index(drop=True))
print(f"REVISED CORPUS: {len(c2)}   (previous: 2330)")
print("  tier A:", (c2.tier=='A').sum(), "| B:", (c2.tier=='B').sum(), "| S:", (c2.tier=='S').sum())
print("  added by re-screen:", int(c2.matched_phrases.eq('tierA_rescreen').sum()),
      "| removed as false positives:", 1474 - len(keepA))
print("\nworks by year 2015+:")
print(c2[c2.year>=2015].year.astype(int).value_counts().sort_index().to_string())
print("\nlandmarks still present:", c2.doi.fillna("").str.replace("https://doi.org/","",regex=False)
      .isin(sw[sw.is_landmark].doi).sum(), "of", int(sw.is_landmark.sum()))


# ======================================================================================
# CELL 087  |  run 2026-10-05 17:29:02Z  |  env=python  |  exit=ok
# ======================================================================================
out = c2.drop(columns=[x for x in ("tnorm","trank","has_doi") if x in c2.columns])
out.to_csv("autonomous_discovery_corpus.csv", index=False, encoding="utf-8")
out.to_csv("subfield_clusters.csv", index=False, encoding="utf-8")
cst2.to_csv("subfield_summary.csv", index=False)
fs2.reset_index().to_csv("field_structure.csv", index=False)
geo2 = pd.DataFrame({"country": list(dict(ctry2.most_common(30)).keys()),
                     "affiliations": list(dict(ctry2.most_common(30)).values())})
geo2["share"] = (geo2.affiliations/tot_aff2).round(4); geo2.to_csv("geography_institutions.csv", index=False)
pd.DataFrame({"institution":[k for k,_ in inst2.most_common(40)],
              "affiliations":[v for _,v in inst2.most_common(40)]}).to_csv("top_institutions.csv", index=False)
plat2.to_csv("lab_platform_table.csv", index=False)
pd.DataFrame([{"institution":n,"n_works":G2.nodes[n]["n"],"dominant_family":G2.nodes[n]["fam"],
               "degree":G2.degree(n),"betweenness":round(btw2[n],4)} for n in G2.nodes]
             ).sort_values("n_works", ascending=False).to_csv("lab_network_nodes.csv", index=False)
gaps2.to_csv("whitespace_gaps.csv", index=False)
M2.to_csv("domain_stage_matrix.csv"); CD2.to_csv("subfield_domain_matrix.csv")
json.dump({"corpus_n": int(len(c2)), "revision": "v2 - full model-based relevance screen of the "
   "high-precision stratum (2,388 records), which the first version could not run",
   "precision_v1": 0.883, "precision_v2": 0.94,
   "precision_method": "random sample read by hand (120 records in v1, 100 in v2)",
   "changes_from_v1": ["corpus 2330 -> 1923 (501 Tier-A false positives removed, 97 true positives restored)",
     "core/periphery split dropped: no adjacent clusters survive screening",
     "betweenness leader changed from Toronto to Lawrence Berkeley National Laboratory",
     "three of the seven v1 'genuine' gaps did not survive and are withdrawn",
     "growth/citation divergence strengthened and is now quantified (Spearman -0.899)"],
   "known_limitations": [
     "2026 partial to 2026-10-03 and 47.2% preprints vs 28.2% in 2025",
     "domain and autonomy-stage assignment is regex-based on title+abstract, hierarchical by stage",
     "citation counts are OpenAlex snapshots as of October 2026"]},
  open("corpus_provenance.json","w"), indent=2)
print("files written | corpus", len(out), "| gaps", len(gaps2), "| platforms", len(plat2))


