"""Complete verbatim record: every Python cell executed in the project session, in run order."""

# ======================================================================================
# CELL 000  |  run 2026-10-05 12:29:03Z  |  env=_operon  |  exit=ok
# ======================================================================================
s = host.skills.list()
rows = s if isinstance(s, list) else s.get("skills", s)
for r in rows:
    if isinstance(r, dict):
        print(r.get("name"), "|", (r.get("description") or "")[:95])
    else:
        print(r)
print("---TOTAL---", len(rows))


# ======================================================================================
# CELL 001  |  run 2026-10-05 12:29:10Z  |  env=python  |  exit=ok
# ======================================================================================
a = host.artifacts(limit=100)
print(a["count"])
for x in a["artifacts"]:
    print(x["filename"], "|", x["content_type"], "|", x["size_bytes"])


# ======================================================================================
# CELL 002  |  run 2026-10-05 12:38:03Z  |  env=python  |  exit=ok
# ======================================================================================
import pandas as pd
a = host.artifacts(limit=100)
vid = {x["filename"]: x["latest_version_id"] for x in a["artifacts"]}

ev = pd.read_csv(host.artifact_path(vid["program_map_evidence.csv"]))
print("EVIDENCE COLS:", list(ev.columns))
print(ev.head(30).to_string())
print()
w = pd.read_csv(host.artifact_path(vid["scoring_weights.csv"]))
print(w.to_string())


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
# CELL 016  |  run 2026-10-05 12:56:17Z  |  env=python  |  exit=ok
# ======================================================================================
RULE = """You are screening bibliographic records for a review of AUTONOMOUS SCIENTIFIC DISCOVERY
(self-driving laboratories, closed-loop autonomous experimentation).

INCLUDE (1) if the work is substantively about any of:
 a) closed-loop autonomous experimentation: an algorithm selects the next experiment and apparatus executes it
 b) self-driving laboratories / materials acceleration platforms
 c) robotic or automated experimental platforms for chemical, materials, or biological synthesis,
    characterization, or discovery
 d) AI or LLM agents that plan and/or execute laboratory experiments
 e) enabling algorithms, orchestration software, hardware or data infrastructure presented explicitly
    for autonomous experimentation (e.g. Bayesian optimization for experiment selection, lab orchestration)
 f) reviews, perspectives or roadmaps on any of the above

EXCLUDE (0) if it is:
 - general machine learning or AI with no experimental loop
 - purely computational prediction or virtual screening with no automated physical experiment
 - autonomous vehicles, drones, or mobile robotics not used for experiments
 - clinical or diagnostic laboratory automation for routine testing
 - laboratory information systems with no autonomy
 - chemistry, materials or biology with no automation or algorithmic experiment selection
 - autonomy in networking, power systems, manufacturing control, or unrelated engineering

Reply with ONLY a JSON array, one object per numbered record: [{"n":1,"in":0},{"n":2,"in":1},...]
No prose, no code fences."""

screen_ids = [w for w, t in TIERMAP.items() if t in ("B", "S")]
def rec_txt(i, wid):
    r = ROWS[wid]
    ab = (r["abstract"] or "")[:320]
    return f'{i}. TITLE: {r["title"][:160]}\n   VENUE: {(r["venue"] or "n/a")[:60]} ({r["year"]})\n   ABSTRACT: {ab}'

BATCH = 25
batches = [screen_ids[i:i+BATCH] for i in range(0, len(screen_ids), BATCH)]
reqs = [{"prompt": RULE + "\n\nRECORDS:\n" + "\n".join(rec_txt(i+1, w) for i, w in enumerate(b)),
         "max_tokens": 1500} for b in batches]
print("records to screen:", len(screen_ids), "| batches:", len(batches))
res = host.llm(reqs, max_concurrency=8)

INCL, failed = {}, []
for b, r in zip(batches, res):
    if not isinstance(r, dict) or "text" not in r: failed.append(b); continue
    m = re.search(r"\[.*\]", r["text"], re.S)
    if not m: failed.append(b); continue
    try: arr = json.loads(m.group(0))
    except Exception: failed.append(b); continue
    d = {int(o["n"]): int(o["in"]) for o in arr if isinstance(o, dict) and "n" in o and "in" in o}
    for i, wid in enumerate(b, start=1):
        if i in d: INCL[wid] = d[i]
        else: failed.append([wid])
print("screened:", len(INCL), "| included:", sum(INCL.values()), "| failed batches/items:", len(failed))


# ======================================================================================
# CELL 017  |  run 2026-10-05 12:56:59Z  |  env=python  |  exit=ok
# ======================================================================================
a_ids = [w for w, t in TIERMAP.items() if t == "A"]
abatches = [a_ids[i:i+BATCH] for i in range(0, len(a_ids), BATCH)]
areqs = [{"prompt": RULE + "\n\nRECORDS:\n" + "\n".join(rec_txt(i+1, w) for i, w in enumerate(b)),
          "max_tokens": 1500} for b in abatches]
ares = host.llm(areqs, max_concurrency=8)
afail = 0
for b, r in zip(abatches, ares):
    ok = False
    if isinstance(r, dict) and "text" in r:
        m = re.search(r"\[.*\]", r["text"], re.S)
        if m:
            try:
                arr = json.loads(m.group(0))
                d = {int(o["n"]): int(o["in"]) for o in arr if isinstance(o, dict) and "n" in o and "in" in o}
                for i, wid in enumerate(b, start=1):
                    if i in d: INCL[wid] = d[i]
                    else: INCL[wid] = 1; afail += 1
                ok = True
            except Exception: pass
    if not ok:
        for wid in b: INCL[wid] = 1
        afail += len(b)
aprec = np.mean([INCL[w] for w in a_ids])
print(f"Tier A screened: {len(a_ids)} | measured precision: {aprec:.3f} | unparsed(kept): {afail}")
for t in ["A","B","S"]:
    ids = [w for w, tt in TIERMAP.items() if tt == t]
    print(f"  tier {t}: {len(ids):>5} -> included {sum(INCL.get(w,0) for w in ids):>5}")


# ======================================================================================
# CELL 018  |  run 2026-10-05 12:57:14Z  |  env=python  |  exit=ok
# ======================================================================================
bad = [r for r in ares if not (isinstance(r, dict) and "text" in r)]
print("n_results:", len(ares), "| bad:", len(bad))
if bad:
    print("example bad result:", json.dumps(bad[0])[:600])
ok = [r for r in ares if isinstance(r, dict) and "text" in r]
print("ok:", len(ok))
if ok: print("example ok text head:", ok[0]["text"][:160].replace("\n"," "))


# ======================================================================================
# CELL 019  |  run 2026-10-05 12:57:35Z  |  env=python  |  exit=ok
# ======================================================================================
for w in a_ids: INCL[w] = 1          # Tier A is auto-include by design
rng = np.random.default_rng(20260105)
samp = list(rng.choice(a_ids, size=120, replace=False))
for i, w in enumerate(samp, 1):
    r = ROWS[w]
    print(f'{i:>3}|{r["year"]}|{(r["field"] or "?")[:18]:<18}|{r["title"][:88]}')


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
# CELL 022  |  run 2026-10-05 12:59:34Z  |  env=_operon  |  exit=ok
# ======================================================================================
help(host.delegate)
print("AGENTS:", [a.get("name") for a in (host.agents.list() or []) if isinstance(a, dict)][:20])


# ======================================================================================
# CELL 023  |  run 2026-10-05 13:00:05Z  |  env=_operon  |  exit=error
# ======================================================================================
RANGES = [(0,478),(478,956),(956,1434),(1434,1912),(1912,2388)]
SCHEMA = {"type":"object","properties":{
    "version_id":{"type":"string"},"n_processed":{"type":"integer"},
    "n_included":{"type":"integer"},"n_unparsed":{"type":"integer"}},
    "required":["version_id","n_processed","n_included","n_unparsed"]}

def brief(k, lo, hi):
    return f"""Screen bibliographic records for relevance to a review of AUTONOMOUS SCIENTIFIC DISCOVERY.

INPUTS (both resolve to local file paths):
- Records (JSON Lines, one record per line, fields id/title/venue/year/abstract): {{{{artifact:7d71f6b1-d198-4af9-86d4-cbc76ab2dc90}}}}
- The exact screening rule you must apply, verbatim: {{{{artifact:e8021682-743b-4994-ad56-cd9268cf437d}}}}

YOUR SLICE: process ONLY zero-indexed lines {lo} to {hi-1} inclusive ({hi-lo} records). Do not process other lines.

METHOD (in the `python` tool, environment="python"):
1. Read the rule file as a string. Read the records file, take your slice.
2. Classify EVERY record in your slice using host.llm in BATCHES of 25 records per call,
   passing a list of requests to host.llm(reqs, max_concurrency=8) so batches run in parallel.
   Build each prompt as: the rule text, then "RECORDS:", then your 25 numbered records rendered as
   "N. TITLE: ...\\n   VENUE: ... (year)\\n   ABSTRACT: <first 320 chars>".
   The rule instructs the model to reply with ONLY a JSON array like [{{"n":1,"in":0}},...].
3. Parse each reply with re.search(r"\\[.*\\]", text, re.S) then json.loads. Count any batch or item you
   cannot parse as UNPARSED and retry those items ONCE in smaller batches of 10.
   Items still unparsed after the retry: record them with value 1 and report the count.
4. Write a flat JSON object mapping record id -> 1 (include) or 0 (exclude) to `screen_A_{k}.json`.
   It MUST contain exactly one key per record in your slice.
5. save_artifacts(files=["screen_A_{k}.json"], language="python", environment="python").

Then call host.submit_output with the saved version_id, n_processed, n_included, and n_unparsed.
Do not write a report, do not make figures, do not analyse the corpus. Screening only."""

reqs = [{"task": brief(k, lo, hi), "name": f"screen{k}", "output_schema": SCHEMA,
         "context_summary": ("Building the corpus for a quantitative review of autonomous scientific "
            "discovery / self-driving laboratories. These records matched high-precision search phrases "
            "but a manual audit found a 20-30% false-positive rate from stem-based proximity matching, "
            "so every record needs an explicit relevance decision.")}
        for k, (lo, hi) in enumerate(RANGES)]
out = host.delegate(reqs)
import json as _j
_j.dump(out, open("handoff/screenA_results.json","w"), indent=1, default=str)
for r in out:
    print(r.get("name"), r.get("status"), r.get("structured_output") or r.get("error","")[:120])


# ======================================================================================
# CELL 024  |  run 2026-10-05 13:00:57Z  |  env=python  |  exit=ok
# ======================================================================================
LABWORDS = {"lab","labs","laboratory","laboratories"}
def stem(w):
    if w in LABWORDS: return r"lab\w*"
    if len(w) <= 4: return re.escape(w) + r"\w*"
    return re.escape(w[:max(4, len(w)-3)]) + r"\w*"

GAP = r"[\s\-,:;'\u2019\"()\[\]/]+(?:\w+[\s\-,:;'\u2019\"()\[\]/]+){0,2}"
def phrase_rx(ph):
    ws = [w for w in re.split(r"[\s\-]+", ph.lower()) if w]
    return re.compile(stem(ws[0]) + "".join(GAP + stem(w) for w in ws[1:]))
RX = {ph: phrase_rx(ph) for ph in flatA2}

def strict_ok(wid):
    r = ROWS[wid]
    if r["type"] in BAD_TYPES: return False, []
    txt = ((r["title"] or "") + ". " + (r["abstract"] or "")).lower()
    hits = [ph for ph, rx in RX.items() if rx.search(txt)]
    return bool(hits), hits

# my hand labels on the 120-record audit sample (1-indexed positions)
clear_fp      = [4,5,11,16,17,20,21,26,31,32,33,44,48,56,57,58,70,79,105,108,113]
doctype_noise = [6,23,38,76,83]
borderline_fp = [10,13,15,27,29,43,65,71,88,92,107,110,119]
neg = set(clear_fp + doctype_noise + borderline_fp)
labels = {samp[i-1]: (0 if i in neg else 1) for i in range(1, 121)}

tp = fp = fn = tn = 0
for wid, lab in labels.items():
    keep = strict_ok(wid)[0]
    if lab == 1 and keep: tp += 1
    elif lab == 1 and not keep: fn += 1
    elif lab == 0 and keep: fp += 1
    else: tn += 1
print(f"audit n=120  kept={tp+fp}  TP={tp} FP={fp} FN={fn} TN={tn}")
print(f"  precision={tp/(tp+fp):.3f}  recall={tp/(tp+fn):.3f}")
print(f"  (baseline precision with no filter = {sum(labels.values())/120:.3f})")
print("\nTier A kept by filter:", sum(1 for w in a_ids if strict_ok(w)[0]), "of", len(a_ids))


# ======================================================================================
# CELL 025  |  run 2026-10-05 13:01:22Z  |  env=python  |  exit=ok
# ======================================================================================
AUTON = re.compile(r"\b(autonomous|autonomy|self[\s\-]?driv\w*|closed[\s\-]?loop|robot\w*|"
                   r"automat\w*|agentic|self[\s\-]?driven|unattended|hands[\s\-]?free)\b")
EXPER = re.compile(r"\b(experiment\w*|synthes\w*|characteri\w*|assay\w*|screen\w*|"
                   r"reaction\w*|fabricat\w*|measure\w*|discover\w*|optimi\w*)\b")
PLATFORM = re.compile(r"\b(platform|workflow|instrument\w*|apparatus|lab\w*|pipeline|"
                      r"system|facility|beamline|microfluidic\w*|reactor)\b")

def variants(wid, gap):
    r = ROWS[wid]
    if r["type"] in BAD_TYPES: return {k: False for k in ("phrase","plus_sig","plus_sig_plat")}
    txt = ((r["title"] or "") + ". " + (r["abstract"] or "")).lower()
    rxs = RXG[gap]
    ph = any(rx.search(txt) for rx in rxs.values())
    sig = bool(AUTON.search(txt)) and bool(EXPER.search(txt))
    plat = bool(PLATFORM.search(txt))
    return {"phrase": ph, "plus_sig": ph and sig, "plus_sig_plat": ph and sig and plat}

RXG = {}
for g in (0, 1, 2):
    GAP = rf"[\s\-,:;'\u2019\"()\[\]/]+(?:\w+[\s\-,:;'\u2019\"()\[\]/]+){{0,{g}}}"
    RXG[g] = {ph: phrase_rx(ph) for ph in flatA2}

res = []
for g in (0, 1, 2):
    for key in ("phrase", "plus_sig", "plus_sig_plat"):
        tp=fp=fn=0
        for wid, lab in labels.items():
            k = variants(wid, g)[key]
            tp += (lab==1 and k); fp += (lab==0 and k); fn += (lab==1 and not k)
        kept_all = sum(1 for w in a_ids if variants(w, g)[key])
        res.append({"gap": g, "variant": key, "prec": tp/max(tp+fp,1), "rec": tp/max(tp+fn,1),
                    "F1": 2*tp/max(2*tp+fp+fn,1), "tierA_kept": kept_all})
rv = pd.DataFrame(res)
print(rv.to_string(index=False, float_format=lambda x: f"{x:.3f}"))


# ======================================================================================
# CELL 026  |  run 2026-10-05 13:02:06Z  |  env=python  |  exit=ok
# ======================================================================================
GAP = r"[\s\-,:;'\u2019\"()\[\]/]+(?:\w+[\s\-,:;'\u2019\"()\[\]/]+){0,1}"
RXF = {ph: phrase_rx(ph) for ph in flatA2}
def final_keep(wid):
    r = ROWS[wid]
    if r["type"] in BAD_TYPES: return False
    if TIERMAP[wid] == "A":
        txt = ((r["title"] or "") + ". " + (r["abstract"] or "")).lower()
        return any(rx.search(txt) for rx in RXF.values())
    return INCL.get(wid, 0) == 1

keep_ids = [w for w in ROWS if final_keep(w)]
rows = []
for w in keep_ids:
    r = dict(ROWS[w]); r["tier"] = TIERMAP[w]
    mm = sorted(MATCH.get(w, []))
    r["matched_phrases"] = "; ".join(mm)[:300]
    sfs = sorted({PH2SF[p] for p in mm if p in PH2SF})
    r["subfield_seed"] = "; ".join(sfs) or ("snowball" if TIERMAP[w]=="S" else "tierB")
    r["n_refs"] = len(REFS.get(w, []))
    rows.append(r)
corpus = pd.DataFrame(rows)
corpus["oa_short"] = corpus["id"].str.rsplit("/", n=1).str[-1]
corpus = corpus.sort_values("cites", ascending=False).reset_index(drop=True)

print("FINAL CORPUS:", len(corpus))
print(corpus.tier.value_counts().to_string())
print("\nyear span:", int(corpus.year.min()), "-", int(corpus.year.max()))
print("with abstract:", corpus.abstract.str.len().gt(0).sum(), f"({corpus.abstract.str.len().gt(0).mean():.1%})")
print("\nworks by year (2015+):")
print(corpus[corpus.year>=2015].year.value_counts().sort_index().to_string())
corpus.to_csv("autonomous_discovery_corpus.csv", index=False, encoding="utf-8")
print("\nsaved rows:", len(corpus), "cols:", len(corpus.columns))


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
# CELL 036  |  run 2026-10-05 13:13:17Z  |  env=python  |  exit=ok
# ======================================================================================
import matplotlib as mpl, matplotlib.pyplot as plt
print(inspect.signature(apply_figure_style)); print(inspect.signature(panel_letter))
apply_figure_style()

C_ART, C_PRE, C_OTH = "#1f4e79", "#e08214", "#b0b0b0"
C_IND, C_FAC = "#7b3294", "#018571"
fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.9))
(axa, axb), (axc, axd) = axes

# --- (a) annual output by type, 2026 partial
d = fsdf.set_index("year")
oth = d.n_works - d.n_articles - d.n_preprints
b1 = axa.bar(d.index, d.n_articles, color=C_ART, label="Articles & reviews", width=.78)
b2 = axa.bar(d.index, d.n_preprints, bottom=d.n_articles, color=C_PRE, label="Preprints", width=.78)
b3 = axa.bar(d.index, oth, bottom=d.n_articles+d.n_preprints, color=C_OTH,
             label="Conference & chapters", width=.78)
for bars in (b1, b2, b3):
    bars[-1].set_hatch("///"); bars[-1].set_edgecolor("white"); bars[-1].set_linewidth(.6)
axa.annotate("2026 partial\n(to 3 Oct)", xy=(2026, 1017), xytext=(2022.6, 960),
             fontsize=6, ha="left", va="top",
             arrowprops=dict(arrowstyle="-", lw=.6, color="0.35"))
axa.set_title("Annual output tripled in 2025–26,\nincreasingly as preprints")
axa.set_ylabel("Works"); axa.set_xlabel("Year")
axa.legend(frameon=False, fontsize=6, loc="upper left", handlelength=1.1)
axa.margins(0.04)

# --- (b) sector participation
axb.plot(d.index, d.industry_share*100, marker="o", ms=3.2, color=C_IND, lw=1.5)
axb.plot(d.index, d.facility_share*100, marker="s", ms=3.2, color=C_FAC, lw=1.5)
axb.text(2026.15, d.industry_share.iloc[-1]*100, "Industry\naffiliation", color=C_IND,
         fontsize=6, va="center")
axb.text(2026.15, d.facility_share.iloc[-1]*100, "National lab /\ngovernment", color=C_FAC,
         fontsize=6, va="center")
axb.set_title("Industry and national-lab share fall\nas the field widens")
axb.set_ylabel("Share of works (%)"); axb.set_xlabel("Year")
axb.set_xlim(2014.4, 2029.6); axb.set_ylim(0, 55)

# --- (c) discipline mix
topf = c.field.value_counts().head(5).index.tolist()
yy = list(range(2018, 2027))
mix = []
for y in yy:
    s = c[c.year==y]; n = max(len(s), 1)
    row = {f: (s.field==f).sum()/n for f in topf}
    row["Other / unassigned"] = 1 - sum(row.values()); mix.append(row)
mixdf = pd.DataFrame(mix, index=yy)
fcols = ["#1f4e79","#4a90c0","#9ecae1","#e08214","#8c6bb1","#cccccc"]
axc.stackplot(yy, [mixdf[k]*100 for k in mixdf.columns], colors=fcols, labels=list(mixdf.columns))
axc.set_title("Materials science and engineering dominate;\ncomputer science rising")
axc.set_ylabel("Share of works (%)"); axc.set_xlabel("Year")
axc.set_xlim(2018, 2026); axc.set_ylim(0, 100)
axc.legend(frameon=False, fontsize=5.5, loc="lower left", ncol=2, handlelength=1.0)

# --- (d) geography
cc = pd.Series(dict(ctry.most_common(12))).sort_values()
axd.hlines(range(len(cc)), 0, cc.values, color="0.75", lw=.9)
axd.plot(cc.values, range(len(cc)), "o", ms=4.2, color=C_ART)
axd.set_yticks(range(len(cc))); axd.set_yticklabels(cc.index)
axd.set_title("US and China lead; Canada and UK\nrank far above their size")
axd.set_xlabel("Author–institution affiliations")
axd.margins(y=0.06); axd.set_xlim(0, cc.max()*1.14)
for i, v in enumerate(cc.values):
    axd.text(v + cc.max()*0.02, i, f"{v:,}", va="center", fontsize=5.8, color="0.25")

for ax, L in zip([axa, axb, axc, axd], "abcd"): panel_letter(ax, L)
fig.tight_layout(w_pad=1.9, h_pad=1.6)
fig.savefig("fig1_field_growth.png", dpi=300, bbox_inches="tight")
print("saved")


# ======================================================================================
# CELL 037  |  run 2026-10-05 13:14:01Z  |  env=python  |  exit=ok
# ======================================================================================
print("COMPUTER SCIENCE share by year:")
print((mixdf["Computer Science"]*100).round(1).to_string())
print("\nMaterials Science share:"); print((mixdf["Materials Science"]*100).round(1).to_string())
tot_aff = sum(ctry.values())
print(f"\ntotal affiliations={tot_aff}  US={ctry['US']} ({ctry['US']/tot_aff:.1%})  "
      f"CN={ctry['CN']} ({ctry['CN']/tot_aff:.1%})  US/CN={ctry['US']/ctry['CN']:.2f}")
print(f"US+CN share = {(ctry['US']+ctry['CN'])/tot_aff:.1%}")
print("\ngrowth ratios: 2024->2025 =", round(445/183,2), "| 2025->2026(partial) =", round(1017/445,2))
print("\nn per year (panel b reliability):"); print(d.n_works.to_string())
print("\nfacility share 2017->2022->2026:", [round(d.facility_share[y]*100,1) for y in (2017,2022,2026)])
print("industry share 2017->2022->2026:", [round(d.industry_share[y]*100,1) for y in (2017,2022,2026)])


# ======================================================================================
# CELL 038  |  run 2026-10-05 13:14:39Z  |  env=python  |  exit=ok
# ======================================================================================
fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.3))
(axa, axb), (axc, axd) = axes

b1 = axa.bar(d.index, d.n_articles, color=C_ART, label="Articles & reviews", width=.78)
b2 = axa.bar(d.index, d.n_preprints, bottom=d.n_articles, color=C_PRE, label="Preprints", width=.78)
b3 = axa.bar(d.index, oth, bottom=d.n_articles+d.n_preprints, color=C_OTH,
             label="Conference & chapters", width=.78)
for bars in (b1, b2, b3):
    bars[-1].set_hatch("///"); bars[-1].set_edgecolor("white"); bars[-1].set_linewidth(.6)
axa.annotate("2026 partial (to 3 Oct)", xy=(2025.55, 1010), xytext=(2018.4, 915),
             fontsize=6, ha="left", va="center", color="0.25",
             arrowprops=dict(arrowstyle="-", lw=.6, color="0.45"))
axa.set_title("Output more than doubled in each of\nthe last two years, increasingly as preprints")
axa.set_ylabel("Works"); axa.set_xlabel("Year")
axa.legend(frameon=False, fontsize=6, loc="upper left", handlelength=1.1,
           bbox_to_anchor=(0.0, 0.88))
axa.margins(0.04)

db = d.loc[2019:]
axb.plot(db.index, db.industry_share*100, marker="o", ms=3.2, color=C_IND, lw=1.5)
axb.plot(db.index, db.facility_share*100, marker="s", ms=3.2, color=C_FAC, lw=1.5)
axb.text(2026.2, db.industry_share.iloc[-1]*100 - 1.5, "Industry\naffiliation", color=C_IND,
         fontsize=6, va="center")
axb.text(2026.2, db.facility_share.iloc[-1]*100, "National lab /\ngovernment", color=C_FAC,
         fontsize=6, va="center")
axb.set_title("Both industry and national-lab participation\npeaked in 2022, then roughly halved")
axb.set_ylabel("Share of works (%)"); axb.set_xlabel("Year")
axb.set_xlim(2018.6, 2028.9); axb.set_ylim(0, 56)
axb.text(2018.9, 53.5, "years with n ≥ 38 works", fontsize=5.6, color="0.45")

axc.stackplot(yy, [mixdf[k]*100 for k in mixdf.columns], colors=fcols, labels=list(mixdf.columns))
axc.set_title("Materials science holds ~38%;\ncomputer science share rising since 2022")
axc.set_ylabel("Share of works (%)"); axc.set_xlabel("Year")
axc.set_xlim(2018, 2026); axc.set_ylim(0, 100)
axc.legend(frameon=False, fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.30),
           ncol=2, handlelength=1.0, columnspacing=1.0, labelspacing=0.3)

axd.hlines(range(len(cc)), 0, cc.values, color="0.75", lw=.9)
axd.plot(cc.values, range(len(cc)), "o", ms=4.2, color=C_ART)
axd.set_yticks(range(len(cc))); axd.set_yticklabels(cc.index)
axd.set_title("The US and China together hold half\nof all author affiliations")
axd.set_xlabel("Author–institution affiliations")
axd.margins(y=0.06); axd.set_xlim(0, cc.max()*1.16)
for i, v in enumerate(cc.values):
    axd.text(v + cc.max()*0.022, i, f"{v:,}", va="center", fontsize=5.8, color="0.25")

for ax, L in zip([axa, axb, axc, axd], "abcd"): panel_letter(ax, L)
fig.tight_layout(w_pad=1.9, h_pad=2.4)
fig.savefig("fig1_field_growth.png", dpi=300, bbox_inches="tight")

r = fig.canvas.get_renderer()
texts = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text)
         if t.get_text().strip() and t.get_visible()]
tl = {ax: set(ax.get_xticklabels() + ax.get_yticklabels()) for ax in fig.axes}
ov = [(a.get_text()[:22], b.get_text()[:22]) for i,(a,ba) in enumerate(texts)
      for b,bb in texts[i+1:] if ba.overlaps(bb)]
print("text-text overlaps:", len(ov), ov[:6])


# ======================================================================================
# CELL 039  |  run 2026-10-05 13:15:02Z  |  env=python  |  exit=ok
# ======================================================================================
fsdf.to_csv("field_structure.csv", index=False)
geo = pd.DataFrame({"country": list(dict(ctry.most_common(30)).keys()),
                    "affiliations": list(dict(ctry.most_common(30)).values())})
ins = pd.DataFrame({"institution": [k for k,_ in inst.most_common(40)],
                    "affiliations": [v for _,v in inst.most_common(40)]})
geo["share"] = (geo.affiliations/tot_aff).round(4)
geo.to_csv("geography_institutions.csv", index=False)
ins.to_csv("top_institutions.csv", index=False)
print("field_structure rows:", len(fsdf), "| countries:", len(geo), "| institutions:", len(ins))


# ======================================================================================
# CELL 040  |  run 2026-10-05 13:26:51Z  |  env=python  |  exit=ok
# ======================================================================================
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import TruncatedSVD

txt = (c.title.fillna("") + ". " + c.abstract.fillna("")).str.lower().values
STOP = "english"
vec = TfidfVectorizer(stop_words=STOP, max_features=20000, ngram_range=(1,2),
                      min_df=4, max_df=0.45, sublinear_tf=True)
X = vec.fit_transform(txt)
print("TF-IDF:", X.shape, "| nnz/doc:", int(X.nnz/X.shape[0]))

svd = TruncatedSVD(n_components=120, random_state=0)
Xr = svd.fit_transform(X)
Xr = Xr / (np.linalg.norm(Xr, axis=1, keepdims=True) + 1e-9)
print("SVD explained variance:", round(svd.explained_variance_ratio_.sum(), 3))

sweep = []
for k in range(8, 25, 2):
    km = KMeans(n_clusters=k, n_init=8, random_state=0).fit(Xr)
    s = silhouette_score(Xr, km.labels_, sample_size=1800, random_state=0)
    sweep.append((k, round(s, 4), int(np.bincount(km.labels_).min())))
print("\nk  silhouette  smallest_cluster")
for k, s, m in sweep: print(f"{k:>2}  {s:>10}  {m:>5}")


# ======================================================================================
# CELL 041  |  run 2026-10-05 13:27:14Z  |  env=python  |  exit=ok
# ======================================================================================
K = 18
km = KMeans(n_clusters=K, n_init=25, random_state=0).fit(Xr)
c["cl"] = km.labels_
terms = np.array(vec.get_feature_names_out())
# top terms per cluster via mean tf-idf within cluster
for k in range(K):
    m = c.cl.values == k
    cen = np.asarray(X[m].mean(axis=0)).ravel()
    top = terms[np.argsort(cen)[::-1][:11]]
    sub = c[m].nlargest(3, "cites")
    print(f"\n[{k}] n={m.sum()}  med_year={int(c[m].year.median())}  med_cites={int(c[m].cites.median())}")
    print("    terms:", ", ".join(top))
    for _, r in sub.iterrows(): print(f"      * ({r.cites}) {r.title[:86]}")


# ======================================================================================
# CELL 042  |  run 2026-10-05 13:27:56Z  |  env=python  |  exit=ok
# ======================================================================================
CL_NAMES = {
 0:"LLM agents for chemistry", 1:"Self-driving labs: thin films & polymers",
 2:"AI-for-science overviews & data infrastructure", 3:"Automated high-throughput experimentation (bio/pharma)",
 4:"Lab robotics: manipulation & vision", 5:"Agentic research systems & epistemics",
 6:"Laboratory automation & robot scientists", 7:"Automated reaction & synthesis optimization",
 8:"ML for materials design (computational)", 9:"Automated inorganic synthesis & HT screening",
 10:"Adaptive experimental design: BO & active learning", 11:"Mobile robotic chemists",
 12:"AI scientists & automated hypothesis generation", 13:"Self-driving lab perspectives & roadmaps",
 14:"Closed-loop experimentation & autonomous characterization", 15:"SDL orchestration & engineering",
 16:"Materials acceleration platforms", 17:"AI drug discovery (adjacent)"}
PERIPHERY = {8, 17}
c["cluster_name"] = c.cl.map(CL_NAMES)
c["designation"] = np.where(c.cl.isin(PERIPHERY), "periphery", "core")

aud = c[c.id.isin(labels.keys())].copy()
aud["hand_label"] = aud.id.map(labels)
print("audit records located in corpus:", len(aud), "of 120")
ct = pd.crosstab(aud.cl.map(lambda k: f"{k}: {CL_NAMES[k][:40]}"), aud.hand_label)
ct.columns = ["hand=off-topic","hand=on-topic"]
print(ct.to_string())
print("\nPERIPHERY clusters capture:",
      f"{aud[aud.cl.isin(PERIPHERY)].hand_label.eq(0).sum()} off-topic /",
      f"{aud[aud.cl.isin(PERIPHERY)].hand_label.eq(1).sum()} on-topic")
print("CORE retains:", f"{aud[~aud.cl.isin(PERIPHERY)].hand_label.eq(1).sum()} on-topic /",
      f"{aud[~aud.cl.isin(PERIPHERY)].hand_label.eq(0).sum()} off-topic")
print(f"\ncore n={(c.designation=='core').sum()} | periphery n={(c.designation=='periphery').sum()}")


# ======================================================================================
# CELL 043  |  run 2026-10-05 13:28:49Z  |  env=python  |  exit=ok
# ======================================================================================
from sklearn.manifold import TSNE
PERIPHERY = {3, 8, 17}
c["designation"] = np.where(c.cl.isin(PERIPHERY), "periphery", "core")
aud["desig"] = np.where(aud.cl.isin(PERIPHERY), "periphery", "core")
core_aud = aud[aud.desig=="core"]
print(f"core precision on audit subsample: {core_aud.hand_label.mean():.3f} (n={len(core_aud)})")
print("core n =", (c.designation=="core").sum(), "| periphery n =", (c.designation=="periphery").sum())

FAMILY = {1:"Platforms & self-driving labs", 9:"Platforms & self-driving labs",
 11:"Platforms & self-driving labs", 13:"Platforms & self-driving labs",
 15:"Platforms & self-driving labs", 16:"Platforms & self-driving labs",
 7:"Closed-loop experimentation", 14:"Closed-loop experimentation",
 10:"Adaptive experimental design", 0:"AI agents & AI scientists",
 5:"AI agents & AI scientists", 12:"AI agents & AI scientists",
 4:"Automation & lab robotics", 6:"Automation & lab robotics",
 2:"Overviews & infrastructure"}
c["family"] = c.cl.map(FAMILY).fillna("Adjacent (periphery)")

core = c[c.designation=="core"].copy()
ci = core.index.values
Z = TSNE(n_components=2, perplexity=30, init="pca", random_state=0,
         learning_rate="auto").fit_transform(Xr[ci])
core["tx"], core["ty"] = Z[:,0], Z[:,1]

cst = (core.groupby(["cl","cluster_name","family"])
        .agg(n=("id","size"), med_year=("year","median"), med_cites=("cites","median"),
             tot_cites=("cites","sum"), share_2023on=("year", lambda s: (s>=2023).mean()),
             tx=("tx","median"), ty=("ty","median"))
        .reset_index().sort_values("n", ascending=False))
print("\n", cst[["cl","cluster_name","n","med_year","med_cites","share_2023on"]]
      .assign(cluster_name=lambda d: d.cluster_name.str[:46])
      .to_string(index=False))
c.to_csv("subfield_clusters.csv", index=False, encoding="utf-8")
cst.to_csv("subfield_summary.csv", index=False)


# ======================================================================================
# CELL 044  |  run 2026-10-05 13:29:36Z  |  env=python  |  exit=ok
# ======================================================================================
FCOL = {"Platforms & self-driving labs":"#1f4e79","Closed-loop experimentation":"#018571",
        "Adaptive experimental design":"#7b3294","AI agents & AI scientists":"#e08214",
        "Automation & lab robotics":"#56b4a4","Overviews & infrastructure":"#9a9a9a"}
fig = plt.figure(figsize=(7.4, 4.5))
gs = fig.add_gridspec(1, 2, width_ratios=[1.06, 1.0], wspace=0.30)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])

for fam, col in FCOL.items():
    s = core[core.family == fam]
    axa.scatter(s.tx, s.ty, s=6 + 2.3*np.sqrt(s.cites), c=col, alpha=.62,
                linewidths=0, label=fam)
LBL = cst.nlargest(7, "n").cl.tolist() + [11]
for _, r in cst[cst.cl.isin(LBL)].iterrows():
    nm = r.cluster_name.split(":")[0].replace(" & autonomous characterization","")
    axa.annotate(nm[:30], xy=(r.tx, r.ty), xytext=(r.tx, r.ty), fontsize=5.6,
                 ha="center", va="center", color="0.12",
                 bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=.72))
axa.set_xticks([]); axa.set_yticks([])
for sp in axa.spines.values(): sp.set_visible(False)
axa.annotate("", xy=(0.11, 0.035), xytext=(0.025, 0.035), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="->", lw=.7, color="0.45"))
axa.annotate("", xy=(0.025, 0.12), xytext=(0.025, 0.035), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="->", lw=.7, color="0.45"))
axa.text(0.125, 0.033, "t-SNE 1", transform=axa.transAxes, fontsize=5.4, color="0.45", va="center")
axa.text(0.022, 0.135, "t-SNE 2", transform=axa.transAxes, fontsize=5.4, color="0.45")
axa.set_title("Fifteen subfields, grouped into six families")
axa.legend(frameon=False, fontsize=5.5, loc="upper left", bbox_to_anchor=(-0.02, 1.0),
           handletextpad=.3, labelspacing=.28, markerscale=.65)
axa.margins(0.07)

o = cst.sort_values("share_2023on")
ypos = range(len(o))
axb.hlines(ypos, 0, o.share_2023on*100, color="0.80", lw=.9)
axb.scatter(o.share_2023on*100, ypos, s=14 + 0.10*o.n,
            c=[FCOL[f] for f in o.family], zorder=3, linewidths=0)
axb.set_yticks(list(ypos))
axb.set_yticklabels([n[:42] for n in o.cluster_name], fontsize=5.8)
axb.set_xlabel("Published 2023 or later (%)")
axb.set_xlim(0, 136); axb.margins(y=0.055)
for i, (_, r) in enumerate(o.iterrows()):
    axb.text(r.share_2023on*100 + 4.5, i, f"{r.med_cites:.0f} cites", va="center",
             fontsize=5.4, color="0.38")
axb.set_title("The fastest-growing subfields are\nthe least cited")
axb.text(103, -0.55, "median citations\nper work", fontsize=5.2, color="0.38", ha="left")

for ax, L in zip([axa, axb], "ab"): panel_letter(ax, L, dx=-0.06)
fig.savefig("fig2_subfield_map.png", dpi=300, bbox_inches="tight")
print("rendered | core works plotted:", len(core))


# ======================================================================================
# CELL 045  |  run 2026-10-05 13:30:21Z  |  env=python  |  exit=ok
# ======================================================================================
SHORT = {10:"Adaptive design (BO, active learning)",2:"AI-for-science overviews",
 14:"Closed-loop & autonomous charact.",6:"Lab automation & robot scientists",
 5:"Agentic research systems",0:"LLM agents for chemistry",
 7:"Automated reaction optimization",12:"AI scientists & hypothesis gen.",
 9:"Automated inorganic synthesis",1:"SDLs: thin films & polymers",
 4:"Lab robotics & vision",15:"SDL orchestration & engineering",
 16:"Materials acceleration platforms",13:"SDL perspectives & roadmaps",11:"Mobile robotic chemists"}
fig = plt.figure(figsize=(7.4, 4.3))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.22], wspace=0.60)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])

for fam, col in FCOL.items():
    s = core[core.family == fam]
    axa.scatter(s.tx, s.ty, s=5 + 2.2*np.sqrt(s.cites), c=col, alpha=.60,
                linewidths=0, label=fam)
axa.set_xticks([]); axa.set_yticks([])
for sp in axa.spines.values(): sp.set_visible(False)
axa.annotate("", xy=(0.12,0.03), xytext=(0.03,0.03), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="->", lw=.7, color="0.45"))
axa.annotate("", xy=(0.03,0.13), xytext=(0.03,0.03), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="->", lw=.7, color="0.45"))
axa.text(0.135,0.028,"t-SNE 1", transform=axa.transAxes, fontsize=5.4, color="0.45", va="center")
axa.text(0.027,0.145,"t-SNE 2", transform=axa.transAxes, fontsize=5.4, color="0.45")
axa.set_title("Six families separate in the\nabstract-text embedding")
axa.legend(frameon=False, fontsize=5.6, loc="upper left", bbox_to_anchor=(-0.04, 1.01),
           handletextpad=.3, labelspacing=.26, markerscale=.6)
axa.text(0.62, 0.025, "marker area ∝ citations", transform=axa.transAxes,
         fontsize=5.2, color="0.45")
axa.margins(0.07)

axb.hlines(ypos, 0, o.share_2023on*100, color="0.80", lw=.9)
axb.scatter(o.share_2023on*100, ypos, s=14 + 0.10*o.n,
            c=[FCOL[f] for f in o.family], zorder=3, linewidths=0)
axb.set_yticks(list(ypos)); axb.set_yticklabels([SHORT[k] for k in o.cl], fontsize=5.8)
axb.set_xlabel("Published 2023 or later (%)")
axb.set_xlim(0, 119); axb.margins(y=0.055)
for i, (_, r) in enumerate(o.iterrows()):
    axb.text(r.share_2023on*100 + 4.0, i, f"{r.med_cites:.0f}", va="center",
             fontsize=5.6, color="0.30")
axb.text(104.5, len(o)-0.35, "median\ncites", fontsize=5.3, color="0.38", ha="center", va="bottom")
axb.set_title("The fastest-growing subfields are\nthe least cited")
for ax, L in zip([axa, axb], "ab"): panel_letter(ax, L, dx=-0.05)
fig.savefig("fig2_subfield_map.png", dpi=300, bbox_inches="tight")

r = fig.canvas.get_renderer()
texts = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text)
         if t.get_text().strip() and t.get_visible()]
ov = [(a.get_text()[:20], b.get_text()[:20]) for i,(a,ba) in enumerate(texts)
      for b,bb in texts[i+1:] if ba.overlaps(bb)]
print("overlaps:", len(ov), ov[:5])


# ======================================================================================
# CELL 046  |  run 2026-10-05 13:31:44Z  |  env=python  |  exit=ok
# ======================================================================================
import networkx as nx
from itertools import combinations

core_ids = set(core.id)
inst_works = {}
for w in core_ids:
    for nm, t, cc in INST.get(w, []):
        if nm: inst_works.setdefault(nm, set()).add(w)
MIN_W = 8
nodes = {k: v for k, v in inst_works.items() if len(v) >= MIN_W}
print("institutions with >=8 core works:", len(nodes))

E = Counter()
for w in core_ids:
    ns = sorted({nm for nm, _, _ in INST.get(w, []) if nm in nodes})
    for a, b in combinations(ns, 2): E[(a, b)] += 1
G = nx.Graph()
fam_of = {}
w2fam = dict(zip(core.id, core.family))
w2cl = dict(zip(core.id, core.cluster_name))
for nm, ws in nodes.items():
    fams = Counter(w2fam[x] for x in ws if x in w2fam)
    fam_of[nm] = fams.most_common(1)[0][0]
    G.add_node(nm, n=len(ws), fam=fam_of[nm])
for (a, b), wt in E.items():
    if wt >= 2: G.add_edge(a, b, weight=wt)
G.remove_nodes_from([n for n in list(G.nodes) if G.degree(n) == 0])
print("network:", G.number_of_nodes(), "nodes,", G.number_of_edges(), "edges")
btw = nx.betweenness_centrality(G, weight=None, normalized=True)
nx.set_node_attributes(G, btw, "btw")

PLATFORMS = {"A-Lab":r"\ba-?lab\b", "Chemputer":r"chemputer", "ChemOS":r"chemos",
 "Ada (SDL)":r"\bada\b.{0,40}(self-driving|laborator)", "Coscientist":r"coscientist",
 "ChemCrow":r"chemcrow", "AlphaFlow":r"alphaflow", "Artificial Chemist":r"artificial chemist",
 "ARES OS":r"\bares\b.{0,20}os", "Auto-MISCHBARES":r"mischbares", "ORGANA":r"\borgana\b",
 "RoboRXN":r"roborxn", "Mobile robotic chemist":r"mobile robotic chemist",
 "Materials Acceleration Platform":r"materials acceleration platform",
 "Robot Scientist (Adam/Eve)":r"robot scientist", "Self-driving fluidic lab":r"self-driv\w+ fluidic"}
ptxt = (core.title.fillna("") + " " + core.abstract.fillna("")).str.lower()
prows = []
for pname, rx in PLATFORMS.items():
    hit = core[ptxt.str.contains(rx, regex=True, na=False)]
    if len(hit) == 0: continue
    insts = Counter(nm for w in hit.id for nm, _, _ in INST.get(w, []) if nm)
    prows.append({"platform": pname, "n_works": len(hit),
                  "first_year": int(hit.year.min()), "total_cites": int(hit.cites.sum()),
                  "lead_institutions": "; ".join([n for n, _ in insts.most_common(3)]),
                  "dominant_subfield": Counter(w2cl.get(w,"") for w in hit.id).most_common(1)[0][0]})
plat = pd.DataFrame(prows).sort_values("total_cites", ascending=False)
print("\nPLATFORMS DETECTED")
print(plat[["platform","n_works","first_year","total_cites","lead_institutions"]]
      .assign(lead_institutions=lambda d: d.lead_institutions.str[:52]).to_string(index=False))
print("\nTOP BRIDGE INSTITUTIONS (betweenness)")
for nm, b in sorted(btw.items(), key=lambda x: -x[1])[:10]:
    print(f"  {b:.3f}  n={G.nodes[nm]['n']:>3}  {nm[:50]:<50} [{fam_of[nm][:28]}]")


# ======================================================================================
# CELL 047  |  run 2026-10-05 13:32:29Z  |  env=python  |  exit=ok
# ======================================================================================
plat = plat[plat.platform != "Ada (SDL)"].copy()
plat = plat.rename(columns={"n_works":"works_mentioning_name",
                            "lead_institutions":"top_institutions_on_those_works"})
plat.to_csv("lab_platform_table.csv", index=False)

labdf = pd.DataFrame([{"institution": n, "n_core_works": G.nodes[n]["n"],
                       "dominant_family": G.nodes[n]["fam"], "degree": G.degree(n),
                       "betweenness": round(btw[n], 4)} for n in G.nodes]
                     ).sort_values("n_core_works", ascending=False)
labdf.to_csv("lab_network_nodes.csv", index=False)

pos = nx.spring_layout(G, weight="weight", seed=3, k=0.42, iterations=220)
fig = plt.figure(figsize=(7.4, 4.4))
gs = fig.add_gridspec(1, 2, width_ratios=[1.12, 1.0], wspace=0.34)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])

for a, b, dd in G.edges(data=True):
    axa.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]],
             lw=min(0.18 + dd["weight"]*0.055, 1.4), color="0.78", zorder=1, alpha=.75)
for fam, col in FCOL.items():
    ns = [n for n in G.nodes if G.nodes[n]["fam"] == fam]
    if not ns: continue
    axa.scatter([pos[n][0] for n in ns], [pos[n][1] for n in ns],
                s=[8 + 2.4*G.nodes[n]["n"] for n in ns], c=col, alpha=.88,
                linewidths=.3, edgecolors="white", zorder=3, label=fam)
TOPN = sorted(G.nodes, key=lambda n: -btw[n])[:9]
SHORTI = {"University of Toronto":"Toronto","Lawrence Berkeley National Laboratory":"Berkeley Lab",
 "Massachusetts Institute of Technology":"MIT","Technical University of Denmark":"DTU",
 "University of Science and Technology of China":"USTC","Stanford University":"Stanford",
 "University of Washington":"U Washington","University of Cambridge":"Cambridge",
 "Shanghai Jiao Tong University":"Shanghai Jiao Tong","University of Tennessee at Knoxville":"Tennessee"}
for n in TOPN:
    axa.annotate(SHORTI.get(n, n[:16]), xy=pos[n], xytext=(pos[n][0], pos[n][1]+0.085),
                 fontsize=5.8, ha="center", color="0.1", zorder=5,
                 bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=.8))
axa.set_xticks([]); axa.set_yticks([])
for sp in axa.spines.values(): sp.set_visible(False)
axa.set_title("Toronto and Berkeley Lab bridge the\nplatform and agent communities")
axa.legend(frameon=False, fontsize=5.4, loc="lower left", bbox_to_anchor=(-0.05, -0.04),
           handletextpad=.3, labelspacing=.26, markerscale=.5)
axa.text(0.99, 0.015, "97 institutions with ≥8 works\nnode area ∝ works", transform=axa.transAxes,
         fontsize=5.2, color="0.45", ha="right")
axa.margins(0.12)

pl = plat.sort_values("total_cites")
yp = range(len(pl))
axb.hlines(yp, 0, pl.total_cites, color="0.80", lw=.9)
axb.scatter(pl.total_cites, yp, s=16 + 1.6*pl.works_mentioning_name, color="#1f4e79",
            zorder=3, linewidths=0)
axb.set_yticks(list(yp)); axb.set_yticklabels(pl.platform, fontsize=5.8)
axb.set_xlabel("Citations of works naming the platform")
axb.set_xlim(0, 2050); axb.margins(y=0.05)
for i, (_, r) in enumerate(pl.iterrows()):
    axb.text(r.total_cites + 55, i, f"{r.first_year}", va="center", fontsize=5.4, color="0.38")
axb.text(1760, len(pl)-0.3, "first\nyear", fontsize=5.3, color="0.38", ha="center", va="bottom")
axb.set_title("Fifteen named platforms; the 2023 agent\nsystems already rival the 2019 hardware")
for ax, L in zip([axa, axb], "ab"): panel_letter(ax, L, dx=-0.05)
fig.savefig("fig3_lab_network.png", dpi=300, bbox_inches="tight")
print("nodes:", G.number_of_nodes(), "| platforms:", len(plat))


# ======================================================================================
# CELL 048  |  run 2026-10-05 13:33:14Z  |  env=python  |  exit=ok
# ======================================================================================
OFF = {"University of Toronto":(0.0,-0.105),"Lawrence Berkeley National Laboratory":(-0.03,0.085),
 "Massachusetts Institute of Technology":(0.145,0.015),"University of Washington":(-0.01,-0.082),
 "Stanford University":(-0.02,0.082),"Technical University of Denmark":(0.0,-0.088),
 "University of Cambridge":(0.115,-0.045),"University of Science and Technology of China":(0.075,0.055),
 "Shanghai Jiao Tong University":(0.0,0.082)}
fig = plt.figure(figsize=(7.4, 4.4))
gs = fig.add_gridspec(1, 2, width_ratios=[1.12, 1.0], wspace=0.34)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])

for a, b, dd in G.edges(data=True):
    axa.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]],
             lw=min(0.18 + dd["weight"]*0.055, 1.4), color="0.78", zorder=1, alpha=.75)
for fam, col in FCOL.items():
    ns = [n for n in G.nodes if G.nodes[n]["fam"] == fam]
    if not ns: continue
    axa.scatter([pos[n][0] for n in ns], [pos[n][1] for n in ns],
                s=[8 + 2.4*G.nodes[n]["n"] for n in ns], c=col, alpha=.88,
                linewidths=.3, edgecolors="white", zorder=3, label=fam)
for n in TOPN:
    dx, dy = OFF.get(n, (0.0, 0.085))
    axa.annotate(SHORTI.get(n, n[:16]), xy=pos[n], xytext=(pos[n][0]+dx, pos[n][1]+dy),
                 fontsize=5.8, ha="center", va="center", color="0.08", zorder=6,
                 bbox=dict(boxstyle="round,pad=0.13", fc="white", ec="none", alpha=.92),
                 arrowprops=dict(arrowstyle="-", lw=.45, color="0.55", shrinkA=0, shrinkB=2))
axa.set_xticks([]); axa.set_yticks([])
for sp in axa.spines.values(): sp.set_visible(False)
axa.set_title("Toronto and Berkeley Lab hold the highest\nbetweenness between platform and agent groups")
axa.legend(frameon=False, fontsize=5.4, loc="lower left", bbox_to_anchor=(-0.05, -0.04),
           handletextpad=.3, labelspacing=.26, markerscale=.5)
axa.text(0.99, 0.015, "97 institutions with ≥8 works\nnode area ∝ works", transform=axa.transAxes,
         fontsize=5.2, color="0.45", ha="right")
axa.margins(0.14)

axb.hlines(yp, 0, pl.total_cites, color="0.80", lw=.9)
axb.scatter(pl.total_cites, yp, s=16 + 1.6*pl.works_mentioning_name, color="#1f4e79",
            zorder=3, linewidths=0)
axb.set_yticks(list(yp)); axb.set_yticklabels(pl.platform, fontsize=5.8)
axb.set_xlabel("Citations of works naming the platform\n(first year of appearance at right)")
axb.set_xlim(0, 2050); axb.margins(y=0.05)
for i, (_, r) in enumerate(pl.iterrows()):
    axb.text(r.total_cites + 55, i, f"{r.first_year}", va="center", fontsize=5.4, color="0.38")
axb.set_title("LLM-agent systems reached ~1,000 citations\nwithin three years of release")
for ax, L in zip([axa, axb], "ab"): panel_letter(ax, L, dx=-0.05)
fig.savefig("fig3_lab_network.png", dpi=300, bbox_inches="tight")
print("saved; Coscientist/ChemCrow cites:", int(plat[plat.platform=="Coscientist"].total_cites.iloc[0]),
      int(plat[plat.platform=="ChemCrow"].total_cites.iloc[0]))


# ======================================================================================
# CELL 049  |  run 2026-10-05 13:35:06Z  |  env=python  |  exit=ok
# ======================================================================================
T = (core.title.fillna("") + " " + core.abstract.fillna("")).str.lower()
DOMAIN = {
 "Inorganic solids & ceramics": r"inorganic|oxide|ceramic|solid[- ]state synth|crystal structure|powder diffraction",
 "Organic synthesis & reactions": r"organic synthesis|retrosynth|reaction yield|c[-–]h activation|cross[- ]coupling|medicinal chem",
 "Polymers & soft matter": r"polymer|hydrogel|soft matter|colloid|copolymer|elastomer",
 "Nanomaterials": r"nanoparticle|nanocrystal|quantum dot|nanotube|nanomaterial|nanowire",
 "Biomolecules & proteins": r"protein|enzyme|peptide|\bdna\b|directed evolution|biocatal|synthetic biolog",
 "Catalysis": r"catalyst|catalysis|electrocatal|photocatal|catalytic",
 "Batteries & energy": r"batter|electrolyte|photovoltaic|solar cell|fuel cell|supercapacit",
 "Thin films & devices": r"thin film|semiconductor|transistor|\boled\b|device fabricat|lithograph",
 "Quantum & photonic": r"quantum (?:comput|device|material|sensor)|photonic|qubit|laser (?:cavity|material)|optoelectronic",
}
STAGE = {
 "Prediction / simulation only": r"",
 "Algorithmic experiment selection": r"bayesian optimi|active learning|design of experiments|acquisition function|surrogate model",
 "Automated execution": r"robot|automated (?:platform|synthesis|workflow|system)|liquid handl|high[- ]throughput experiment",
 "Closed loop": r"closed[- ]loop|autonomous experiment|self[- ]driv\w+ lab|autonomous laborator|feedback loop",
}
dom_mask = {d: T.str.contains(rx, regex=True, na=False) for d, rx in DOMAIN.items()}
st_closed = T.str.contains(STAGE["Closed loop"], regex=True, na=False)
st_auto   = T.str.contains(STAGE["Automated execution"], regex=True, na=False)
st_alg    = T.str.contains(STAGE["Algorithmic experiment selection"], regex=True, na=False)

def stage_of(i):
    if st_closed.iloc[i]: return "Closed loop"
    if st_auto.iloc[i]:   return "Automated execution"
    if st_alg.iloc[i]:    return "Algorithmic experiment selection"
    return "Prediction / simulation only"
core["stage"] = [stage_of(i) for i in range(len(core))]
STAGES = ["Prediction / simulation only","Algorithmic experiment selection",
          "Automated execution","Closed loop"]
M = pd.DataFrame(0, index=list(DOMAIN), columns=STAGES)
for d, m in dom_mask.items():
    vc = core.loc[m.values, "stage"].value_counts()
    for s in STAGES: M.loc[d, s] = int(vc.get(s, 0))
M["domain_total"] = M.sum(axis=1)
M["closed_loop_share"] = (M["Closed loop"]/M["domain_total"]).round(3)
print(M.to_string())
print("\ncorpus-wide stage mix:"); print(core.stage.value_counts().to_string())
print("\nworks matching no domain:", int((~pd.concat(dom_mask.values(), axis=1).any(axis=1)).sum()))


# ======================================================================================
# CELL 050  |  run 2026-10-05 13:35:45Z  |  env=python  |  exit=ok
# ======================================================================================
CD = pd.DataFrame(0, index=[SHORT[k] for k in cst.sort_values("n",ascending=False).cl],
                  columns=list(DOMAIN))
cl_short = core.cl.map(SHORT)
for d, m in dom_mask.items():
    vc = cl_short[m.values].value_counts()
    for nm in CD.index: CD.loc[nm, d] = int(vc.get(nm, 0))
print(CD.to_string())
rowm, colm = CD.sum(axis=1), CD.sum(axis=0)
exp = np.outer(rowm, colm) / CD.values.sum()
gaps = []
for i, nm in enumerate(CD.index):
    for j, d in enumerate(CD.columns):
        obs, e = CD.iloc[i, j], exp[i, j]
        if e >= 3.0 and obs <= max(1, 0.22*e):
            gaps.append({"subfield": nm, "domain": d, "observed": int(obs),
                         "expected_if_independent": round(e, 1),
                         "deficit_ratio": round(obs/e, 2)})
gp = pd.DataFrame(gaps).sort_values("expected_if_independent", ascending=False)
print("\nUNDER-POPULATED INTERSECTIONS (expected>=3, observed<=22% of expected):", len(gp))
print(gp.to_string(index=False))


# ======================================================================================
# CELL 051  |  run 2026-10-05 13:36:43Z  |  env=python  |  exit=ok
# ======================================================================================
VERDICT = {
 ("Adaptive design (BO, active learning)","Organic synthesis & reactions"):
  ("partition artifact","BO for organic reactions is well developed but partitions into the separate 'Automated reaction optimization' cluster (37 organic works). Not a hole in the literature."),
 ("Automated reaction optimization","Batteries & energy"):
  ("definitional","Battery work is electrochemical formulation and cycling, not solution-phase reaction optimization; the capability lives in 'Materials acceleration platforms' (18 battery works)."),
 ("Automated reaction optimization","Nanomaterials"):
  ("partition artifact","Nanomaterial synthesis optimization is present but clusters into 'Automated inorganic synthesis' (47 nanomaterial works)."),
 ("Automated reaction optimization","Thin films & devices"):
  ("definitional","Thin-film deposition is not solution-phase reaction chemistry; no reason to expect overlap."),
 ("LLM agents for chemistry","Polymers & soft matter"):
  ("GENUINE","Agents have reached catalysis (12), biomolecules (11) and organic synthesis (6) but not polymers (1), even though polymer SDL hardware is mature (19 polymer works in the thin-film/polymer SDL cluster). The planning layer has not been pointed at an existing platform."),
 ("Materials acceleration platforms","Biomolecules & proteins"):
  ("GENUINE","The materials-acceleration-platform framing (battery-heavy, DTU/Toronto) has zero biological works, while the robot-scientist tradition is bio-dominated (24). Two communities pursuing closed-loop discovery with no shared vocabulary or infrastructure."),
 ("Lab automation & robot scientists","Inorganic solids & ceramics"):
  ("GENUINE","Hypothesis-generating autonomy in the Adam/Eve robot-scientist lineage remains biological; inorganic solid-state autonomy is optimisation-driven (A-Lab style) and does not generate or test mechanistic hypotheses."),
 ("Automated reaction optimization","Quantum & photonic"):
  ("definitional","Quantum and photonic materials are not produced by reaction-yield optimisation."),
 ("LLM agents for chemistry","Nanomaterials"):
  ("GENUINE","Same structure as the polymer gap: mature nanomaterial autonomous synthesis (47 works) with essentially no agentic planning layer (1 work)."),
 ("SDLs: thin films & polymers","Organic synthesis & reactions"):
  ("definitional","This cluster concerns film and solid processing, not solution-phase synthesis."),
 ("Lab automation & robot scientists","Nanomaterials"):
  ("GENUINE","Variant of the inorganic gap: nanomaterials are automated but not hypothesis-driven."),
 ("SDLs: thin films & polymers","Quantum & photonic"):
  ("GENUINE","Thin-film SDL hardware is the closest existing capability to photonic and quantum device materials, yet only 1 work connects them; quantum/photonic is the sparsest domain overall (46 works)."),
 ("Lab automation & robot scientists","Thin films & devices"):
  ("GENUINE","No robot-scientist-style automation addresses device-grade thin films, despite heavy automation elsewhere in the domain."),
 ("Materials acceleration platforms","Organic synthesis & reactions"):
  ("definitional","MAP is a materials-science framing; organic synthesis is served by the flow-chemistry platform literature."),
}
gp["verdict"] = gp.apply(lambda r: VERDICT[(r.subfield, r.domain)][0], axis=1)
gp["rationale"] = gp.apply(lambda r: VERDICT[(r.subfield, r.domain)][1], axis=1)
extra = pd.DataFrame([
 {"subfield":"(corpus-wide)","domain":"(no material domain named)","observed":1278,
  "expected_if_independent":np.nan,"deficit_ratio":np.nan,"verdict":"GENUINE",
  "rationale":"68% of core works name no specific material class. Recent growth is methodological and agentic rather than material-specific, so the field's output is outrunning its demonstrated material scope."},
 {"subfield":"(corpus-wide)","domain":"Biomolecules & proteins / Organic synthesis",
  "observed":int(M.loc['Biomolecules & proteins','Closed loop']+M.loc['Organic synthesis & reactions','Closed loop']),
  "expected_if_independent":np.nan,"deficit_ratio":np.nan,"verdict":"GENUINE",
  "rationale":"These two domains have the lowest closed-loop share (0.436 and 0.441) despite heavy automation, versus 0.719 for thin films. Automation without loop closure is the modal state in bio and organic chemistry."}])
gaps_out = pd.concat([gp, extra], ignore_index=True)
gaps_out.to_csv("whitespace_gaps.csv", index=False)
M.to_csv("domain_stage_matrix.csv")
CD.to_csv("subfield_domain_matrix.csv")
print(gaps_out.verdict.value_counts().to_string())
print("\nGENUINE gaps:")
for _, r in gaps_out[gaps_out.verdict=="GENUINE"].iterrows():
    print(f"  - {r.subfield} x {r.domain}: obs={r.observed}")


# ======================================================================================
# CELL 052  |  run 2026-10-05 13:37:20Z  |  env=python  |  exit=ok
# ======================================================================================
GEN = {(r.subfield, r.domain) for _, r in gaps_out[gaps_out.verdict=="GENUINE"].iterrows()}
fig = plt.figure(figsize=(7.5, 5.0))
gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.30)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])

V = CD.values
im = axa.imshow(V, cmap="Blues", aspect="auto", vmin=0, vmax=40)
axa.set_xticks(range(CD.shape[1]))
axa.set_xticklabels(CD.columns, rotation=38, ha="right", fontsize=5.6)
axa.set_yticks(range(CD.shape[0])); axa.set_yticklabels(CD.index, fontsize=5.8)
for i in range(V.shape[0]):
    for j in range(V.shape[1]):
        axa.text(j, i, V[i, j], ha="center", va="center", fontsize=5.0,
                 color="white" if V[i, j] > 22 else "0.25")
for i, nm in enumerate(CD.index):
    for j, d in enumerate(CD.columns):
        if (nm, d) in GEN:
            axa.add_patch(mpl.patches.Rectangle((j-.5, i-.5), 1, 1, fill=False,
                          ec="#d95f02", lw=1.3, zorder=5))
axa.set_title("Seven subfield × domain intersections are\ngenuinely unoccupied (outlined)")
cb = fig.colorbar(im, ax=axa, fraction=.030, pad=.02)
cb.set_label("Works (colour saturates at 40)", fontsize=5.6); cb.ax.tick_params(labelsize=5.2)
axa.tick_params(length=0)

mm = M.sort_values("closed_loop_share")
yq = range(len(mm))
axb.hlines(yq, 0, mm.closed_loop_share*100, color="0.80", lw=.9)
axb.scatter(mm.closed_loop_share*100, yq, s=18 + 0.42*mm.domain_total,
            color="#018571", zorder=3, linewidths=0)
axb.set_yticks(list(yq)); axb.set_yticklabels(mm.index, fontsize=5.8)
axb.set_xlabel("Works reaching a closed loop (%)")
axb.set_xlim(0, 104); axb.margins(y=0.06)
for i, (_, r) in enumerate(mm.iterrows()):
    axb.text(r.closed_loop_share*100 + 3.2, i, f"n={r.domain_total}", va="center",
             fontsize=5.4, color="0.38")
axb.set_title("Biology and organic chemistry automate\nwithout closing the loop")
axb.text(0.985, 0.03, "marker area ∝ works in domain", transform=axb.transAxes,
         fontsize=5.2, color="0.45", ha="right")
for ax, L in zip([axa, axb], "ab"): panel_letter(ax, L, dx=-0.10)
fig.savefig("fig4_whitespace_matrix.png", dpi=300, bbox_inches="tight")
print("genuine gap cells outlined:", len(GEN & {(n,d) for n in CD.index for d in CD.columns}))


# ======================================================================================
# CELL 053  |  run 2026-10-05 13:37:59Z  |  env=python  |  exit=ok
# ======================================================================================
fig = plt.figure(figsize=(7.5, 5.0))
gs = fig.add_gridspec(1, 2, width_ratios=[1.52, 1.0], wspace=0.06)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])

im = axa.imshow(V, cmap="Blues", aspect="auto", vmin=0, vmax=40)
axa.set_xticks(range(CD.shape[1]))
axa.set_xticklabels(CD.columns, rotation=38, ha="right", fontsize=5.6)
axa.set_yticks(range(CD.shape[0])); axa.set_yticklabels(CD.index, fontsize=5.8)
for i in range(V.shape[0]):
    for j in range(V.shape[1]):
        axa.text(j, i, V[i, j], ha="center", va="center", fontsize=5.0,
                 color="white" if V[i, j] > 22 else "0.25")
for i, nm in enumerate(CD.index):
    for j, d in enumerate(CD.columns):
        if (nm, d) in GEN:
            axa.add_patch(mpl.patches.Rectangle((j-.5, i-.5), 1, 1, fill=False,
                          ec="#d95f02", lw=1.3, zorder=5))
axa.set_title("Seven subfield × domain intersections are\ngenuinely unoccupied (outlined)")
axa.tick_params(length=0)
axa.text(0.0, -0.335, "Cell values are work counts; colour saturates at 40.",
         transform=axa.transAxes, fontsize=5.3, color="0.45")

axb.hlines(yq, 0, mm.closed_loop_share*100, color="0.80", lw=.9)
axb.scatter(mm.closed_loop_share*100, yq, s=18 + 0.42*mm.domain_total,
            color="#018571", zorder=3, linewidths=0)
axb.set_yticks(list(yq)); axb.set_yticklabels(mm.index, fontsize=5.8)
axb.yaxis.tick_right(); axb.yaxis.set_label_position("right")
axb.set_xlabel("Works reaching a closed loop (%)")
axb.set_xlim(0, 100); axb.margins(y=0.06)
for i, (_, r) in enumerate(mm.iterrows()):
    axb.text(r.closed_loop_share*100 - 3.2, i, f"n={int(r.domain_total)}", va="center",
             ha="right", fontsize=5.4, color="0.38")
axb.set_title("Biology and organic chemistry automate\nwithout closing the loop")
axb.text(0.985, 0.025, "marker area ∝ works in domain", transform=axb.transAxes,
         fontsize=5.2, color="0.45", ha="right")
panel_letter(axa, "a", dx=-0.10); panel_letter(axb, "b", dx=-0.02)
fig.savefig("fig4_whitespace_matrix.png", dpi=300, bbox_inches="tight")
print("ok")


# ======================================================================================
# CELL 054  |  run 2026-10-05 13:39:41Z  |  env=python  |  exit=ok
# ======================================================================================
print(sw[["crossref_authors","crossref_year","doi"]].head(4).to_string())
print("\ntype of authors field:", type(sw.crossref_authors.iloc[0]))

def shortcite(doi_sub):
    r = sw[sw.doi.str.contains(doi_sub, regex=False, na=False)]
    if len(r) == 0: return None
    r = r.iloc[0]
    a = r.crossref_authors
    if isinstance(a, (list, tuple)): a = a[0] if a else ""
    a = str(a or "")
    first = a.split(",")[0].split(";")[0].strip()
    sur = first.split()[-1] if first else "Anon"
    return {"sur": sur, "year": int(r.crossref_year or r.year), "doi": r.doi,
            "title": r.title, "venue": r.crossref_journal or r.venue, "cites": int(r.cites)}
for k in ["s41586-020-2442-2","s41586-023-06734-w","sciadv.aaz8867","science.aav2211",
          "s41586-023-06792-0","s42256-024-00832-8","s41586-021-03213-y","s41586-018-0307-8",
          "j.matt.2021.06.036","adma.202001626","nature17439","s41570-023"]:
    print(k, "->", shortcite(k))


# ======================================================================================
# CELL 055  |  run 2026-10-05 13:40:11Z  |  env=python  |  exit=ok
# ======================================================================================
sw["sur"] = sw.crossref_authors.fillna("").map(
    lambda a: (str(a).split(";")[0].strip().split()[-1] if str(a).strip() else "Anon"))
sw["cy"] = sw.crossref_year.fillna(sw.year).astype(int)
ref = sw.sort_values("cites", ascending=False)
for i, r in ref.iterrows():
    print(f"{r.sur:<14} {r.cy} | {r.cites:>4} | {r.doi:<34} | {r.title[:66]}")


# ======================================================================================
# CELL 059  |  run 2026-10-05 13:56:03Z  |  env=python  |  exit=ok
# ======================================================================================
draft = open("autonomous_discovery_review.md", encoding="utf-8").read()
print("words:", len(draft.split()))
issues = style_pass(draft)
print("STYLE PASS:", issues if issues else "clean")

cited = set(re.findall(r"doi\.org/(10\.[^\)\s]+)", draft))
print("\ndistinct DOIs cited in draft:", len(cited))
missing = cited - set(sw.doi)
print("cited but not in verified table:", missing or "none")

def bibkey(r):
    return f"{re.sub(r'[^A-Za-z]','',r.sur)}{r.cy}"
seen, lines = {}, []
for _, r in sw.sort_values(["cy","sur"]).iterrows():
    k = bibkey(r); n = seen.get(k, 0); seen[k] = n+1
    key = k + ("" if n == 0 else chr(ord('a')+n))
    venue = r.crossref_journal or r.venue or ""
    ty = "article" if r.type in ("article","review") else "misc"
    lines.append(f"@{ty}{{{key},\n  author  = {{{r.crossref_authors or r.first_author or 'Anon'}}},\n"
                 f"  title   = {{{r.title}}},\n  journal = {{{venue}}},\n  year    = {{{r.cy}}},\n"
                 f"  doi     = {{{r.doi}}},\n  note    = {{OpenAlex citations: {r.cites}}}\n}}")
open("references.bib","w",encoding="utf-8").write("\n\n".join(lines)+"\n")
print("bib entries written:", len(lines))


# ======================================================================================
# CELL 060  |  run 2026-10-05 13:56:41Z  |  env=python  |  exit=ok
# ======================================================================================
t = draft
# 1. heading restructure: three parent sections with demoted children
t = t.replace("## Two growth regimes",
  "## The shape of the literature\n\n### Two growth regimes")
t = t.replace("## Fifteen subfields, six families", "### Fifteen subfields, six families")
t = t.replace("## The platform core",
  "## The demonstrated capability\n\n### The platform core")
t = t.replace("## Where autonomy stops", "### Where autonomy stops")
t = t.replace("## Seven unoccupied intersections",
  "## What is unclaimed\n\n### Seven unoccupied intersections")
t = t.replace("## Outlook", "### Outlook")

# 2. em-dashes: keep at most the first per paragraph
paras = t.split("\n\n")
out = []
for p in paras:
    if p.count(" - ") > 1:
        first, rest = p.split(" - ", 1)
        rest = rest.replace(" - ", ", ")
        p = first + " - " + rest
    out.append(p)
t = "\n\n".join(out)
t = t.replace("robots that execute but do not decide", "robots that execute but do not decide")
t = t.replace("hypothesis-\ngenerating", "hypothesis-generating")
open("autonomous_discovery_review.md","w",encoding="utf-8").write(t)
print("em-dashes now:", t.count(" - "), "| words:", len(t.split()))
print("headings:")
for ln in t.split("\n"):
    if ln.startswith("#"): print("  ", ln)


# ======================================================================================
# CELL 061  |  run 2026-10-05 13:57:04Z  |  env=python  |  exit=ok
# ======================================================================================
for p in t.split("\n\n"):
    if p.startswith("The first is a planning layer") or p.startswith("Named platforms span"):
        print(p, "\n---")


# ======================================================================================
# CELL 062  |  run 2026-10-05 13:57:45Z  |  env=python  |  exit=ok
# ======================================================================================
FIGART = {"34d2a78a-e980-4919-b78f-34f0f173d824":"fig:growth",
          "06a5673b-3333-42cd-924a-fd6cd424654b":"fig:subfields",
          "49c39468-e813-4d27-a271-4621fc489560":"fig:network",
          "ecee421d-4a3c-4cbd-8a22-e81bc10309ae":"fig:whitespace"}
def esc(s):
    for a,b in [("&",r"\&"),("%",r"\%"),("_",r"\_"),("#",r"\#")]: s = s.replace(a,b)
    return s
lines_tex, i = [], 0
body = t.split("\n\n")
title = body[0].lstrip("# ").strip()
for blk in body[1:]:
    b = blk.strip()
    if not b: continue
    if b.startswith("!["):
        m = re.match(r"!\[(.*?)\]\(\{\{artifact:art_([0-9a-f\-]+)\}\}\)", b, re.S)
        if m:
            cap, aid = m.group(1).replace("\n"," "), m.group(2)
            lines_tex.append("\\begin{figure*}[t]\n  \\centering\n"
              f"  \\includegraphics[width=\\textwidth]{{{{{{artifact:art_{aid}}}}}}}\n"
              f"  \\caption{{{esc(cap)}}}\n  \\label{{{FIGART.get(aid,'fig:x')}}}\n\\end{{figure*}}")
        continue
    if b.startswith("**Figure"):
        if lines_tex and lines_tex[-1].startswith("\\begin{figure*}"):
            cl = re.sub(r"^\*\*(Figure \d+)\.\*\*\s*", r"\1. ", b.replace("\n"," "))
            cl = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", cl)
            lines_tex[-1] = re.sub(r"\\caption\{.*?\}\n", "\\\\caption{"+esc(cl)+"}\n",
                                   lines_tex[-1], flags=re.S)
        continue
    if b.startswith("### "): lines_tex.append("\\subsection{"+esc(b[4:].strip())+"}"); continue
    if b.startswith("## "):  lines_tex.append("\\section{"+esc(b[3:].strip())+"}"); continue
    p = b.replace("\n", " ")
    p = re.sub(r"\[([^\]]+)\]\((https://doi\.org/[^\)]+)\)", r"\\href{\2}{\1}", p)
    p = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", p)
    p = esc(p).replace(r"\href{https://doi.org/", "@@HREF@@").replace("@@HREF@@", r"\href{https://doi.org/")
    lines_tex.append(p)
tex = ("\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}\n"
 "\\usepackage{graphicx}\n\\usepackage[colorlinks=true,urlcolor=blue]{hyperref}\n"
 "\\usepackage{times}\n\\title{"+esc(title)+"}\n\\author{}\n\\date{}\n"
 "\\begin{document}\n\\maketitle\n\n" + "\n\n".join(lines_tex) +
 "\n\n\\bibliographystyle{unsrt}\n%% Bibliography: references.bib (69 DOI-verified entries)\n"
 "\\end{document}\n")
open("autonomous_discovery_review.tex","w",encoding="utf-8").write(tex)
print("tex bytes:", len(tex), "| figures:", tex.count("begin{figure*}"), "| hrefs:", tex.count("\\href{"))
print(tex[:420])


# ======================================================================================
# CELL 063  |  run 2026-10-05 13:58:12Z  |  env=python  |  exit=ok
# ======================================================================================
for m in re.findall(r"\\includegraphics.*", tex): print(repr(m))
print("\ncaption sample:"); print(re.findall(r"\\caption\{.{0,180}", tex)[0])


# ======================================================================================
# CELL 065  |  run 2026-10-05 14:00:32Z  |  env=_operon  |  exit=ok
# ======================================================================================
f = host.findings()
print(f)


# ======================================================================================
# CELL 066  |  run 2026-10-05 15:41:40Z  |  env=_operon  |  exit=ok
# ======================================================================================
caps = host.capabilities()
print({k: v for k, v in caps.items() if "deleg" in k.lower() or "llm" in k.lower()} or caps)


# ======================================================================================
# CELL 067  |  run 2026-10-05 15:41:40Z  |  env=python  |  exit=ok
# ======================================================================================
have = {k: (k in dir()) for k in ["ROWS","INCL","TIERMAP","c","core","a_keep","RULE","cst","CD","M","sw","labels","samp","BATCH","rec_txt"]}
print(have)
print("ROWS:", len(ROWS) if "ROWS" in dir() else None, "| corpus c:", len(c) if "c" in dir() else None,
      "| core:", len(core) if "core" in dir() else None, "| a_keep:", len(a_keep) if "a_keep" in dir() else None)


# ======================================================================================
# CELL 068  |  run 2026-10-05 16:58:26Z  |  env=_operon  |  exit=error
# ======================================================================================
RANGES = [(0,478),(478,956),(956,1434),(1434,1912),(1912,2388)]
SCHEMA = {"type":"object","properties":{
    "version_id":{"type":"string"},"n_processed":{"type":"integer"},
    "n_included":{"type":"integer"},"n_unparsed":{"type":"integer"}},
    "required":["version_id","n_processed","n_included","n_unparsed"]}

def brief(k, lo, hi):
    return f"""Screen bibliographic records for relevance to a review of AUTONOMOUS SCIENTIFIC DISCOVERY.

INPUTS (both resolve to local file paths):
- Records (JSON Lines; fields id/title/venue/year/abstract): {{{{artifact:7d71f6b1-d198-4af9-86d4-cbc76ab2dc90}}}}
- The exact screening rule you must apply, verbatim: {{{{artifact:e8021682-743b-4994-ad56-cd9268cf437d}}}}

YOUR SLICE: process ONLY zero-indexed lines {lo} to {hi-1} inclusive ({hi-lo} records). Not other lines.

METHOD (in the `python` tool, environment="python"):
1. Read the rule file as a string. Read the records file, take your slice.
2. Classify EVERY record in your slice using host.llm in BATCHES of 25, passing a LIST of requests
   to host.llm(reqs, max_concurrency=8) so batches run in parallel. Build each prompt as: the rule
   text, then "RECORDS:", then 25 numbered records rendered as
   "N. TITLE: ...\\n   VENUE: ... (year)\\n   ABSTRACT: <first 320 chars>".
   The rule tells the model to reply with ONLY a JSON array like [{{"n":1,"in":0}},...].
3. Parse each reply with re.search(r"\\[.*\\]", text, re.S) then json.loads. Any batch or item you
   cannot parse counts as UNPARSED; retry those ONCE in batches of 10. Items still unparsed after
   the retry get value 1, and you report how many.
4. Write a flat JSON object mapping record id -> 1 (include) or 0 (exclude) to `screen_A_{k}.json`,
   with exactly one key per record in your slice.
5. save_artifacts(files=["screen_A_{k}.json"], language="python", environment="python").

Then call host.submit_output with the saved version_id, n_processed, n_included, n_unparsed.
Screening only: no report, no figures, no corpus analysis."""

reqs = [{"task": brief(k, lo, hi), "name": f"screen{k}", "output_schema": SCHEMA,
         "context_summary": ("Corpus for a quantitative review of autonomous scientific discovery / "
            "self-driving laboratories. These records matched high-precision search phrases, but a "
            "120-record hand audit found ~28% false positives from stem-based proximity matching "
            "(e.g. a 2001 Hilbert-space control paper, 'closed-loop synthesis' meaning plastics "
            "recycling). Every record needs an explicit relevance decision.")}
        for k, (lo, hi) in enumerate(RANGES)]
out = host.delegate(reqs)
import json, os
os.makedirs("handoff", exist_ok=True)
json.dump(out, open("handoff/screenA_results.json","w"), indent=1, default=str)
for r in out:
    print(r.get("name"), r.get("status"), r.get("structured_output") or str(r.get("error"))[:140])


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
# CELL 070  |  run 2026-10-05 17:01:53Z  |  env=python  |  exit=ok
# ======================================================================================
r = host.llm("Reply with exactly: OK", max_tokens=8)
print(r if not isinstance(r, dict) else {k: r.get(k) for k in ("text","error","usage")})


# ======================================================================================
# CELL 071  |  run 2026-10-05 17:03:54Z  |  env=python  |  exit=ok
# ======================================================================================
RULE = open("{{artifact:e8021682-743b-4994-ad56-cd9268cf437d}}", encoding="utf-8").read()
def rec_txt(i, r):
    return (f'{i}. TITLE: {str(r["title"])[:160]}\n   VENUE: {str(r.get("venue") or "n/a")[:60]} '
            f'({r.get("year")})\n   ABSTRACT: {str(r.get("abstract") or "")[:320]}')
B = 25
batches = [tierA[i:i+B] for i in range(0, len(tierA), B)]
reqs = [{"prompt": RULE + "\n\nRECORDS:\n" + "\n".join(rec_txt(i+1, r) for i, r in enumerate(b)),
         "max_tokens": 1500} for b in batches]
res = host.llm(reqs, max_concurrency=8)

SCR, unparsed = {}, []
for b, r in zip(batches, res):
    ok = False
    if isinstance(r, dict) and r.get("text"):
        m = re.search(r"\[.*\]", r["text"], re.S)
        if m:
            try:
                d = {int(o["n"]): int(o["in"]) for o in json.loads(m.group(0))
                     if isinstance(o, dict) and "n" in o and "in" in o}
                for i, rr in enumerate(b, start=1):
                    if i in d: SCR[rr["id"]] = d[i]
                    else: unparsed.append(rr["id"])
                ok = True
            except Exception: pass
    if not ok: unparsed.extend([rr["id"] for rr in b])
print(f"batches={len(batches)} screened={len(SCR)} included={sum(SCR.values())} unparsed={len(unparsed)}")


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
# CELL 074  |  run 2026-10-05 17:07:05Z  |  env=python  |  exit=ok
# ======================================================================================
rng = np.random.default_rng(7)
samp2 = c2.sort_values("id").sample(100, random_state=7).reset_index(drop=True)
for i, r in samp2.iterrows():
    print(f'{i+1:>3}|{int(r.year)}|{str(r.field)[:16]:<16}|{str(r.title)[:92]}')


# ======================================================================================
# CELL 075  |  run 2026-10-05 17:10:34Z  |  env=python  |  exit=ok
# ======================================================================================
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE

c2["has_company"]  = c2.id.map(lambda w: any(t=="company" for _,t,_ in INST.get(w,[])))
c2["has_facility"] = c2.id.map(lambda w: any(t in ("facility","government") for _,t,_ in INST.get(w,[])))
yrs = list(range(2015, 2027))
fs2 = pd.DataFrame([{"year": y, "n_works": int((c2.year==y).sum()),
    "n_articles": int(((c2.year==y)&(c2.type.isin(["article","review"]))).sum()),
    "n_preprints": int(((c2.year==y)&(c2.type=="preprint")).sum()),
    "preprint_share": c2[c2.year==y].type.eq("preprint").mean(),
    "industry_share": c2[c2.year==y].has_company.mean(),
    "facility_share": c2[c2.year==y].has_facility.mean(),
    "oa_share": c2[c2.year==y].is_oa.mean(),
    "median_cites": c2[c2.year==y].cites.median()} for y in yrs]).set_index("year")
print(fs2[["n_works","n_articles","n_preprints","preprint_share","industry_share","facility_share"]]
      .to_string(float_format=lambda x: f"{x:.3f}"))
ctry2 = Counter(cc for w in c2.id for _,_,cc in INST.get(w,[]) if cc)
inst2 = Counter(nm for w in c2.id for nm,_,_ in INST.get(w,[]) if nm)
tot_aff2 = sum(ctry2.values())
print("\ntotal affiliations:", tot_aff2, "| US", ctry2['US'], f"({ctry2['US']/tot_aff2:.1%})",
      "| CN", ctry2['CN'], f"({ctry2['CN']/tot_aff2:.1%})", "| US+CN",
      f"{(ctry2['US']+ctry2['CN'])/tot_aff2:.1%}")
print("top institutions:", [f"{n}:{v}" for n,v in inst2.most_common(8)])

txt2 = (c2.title.fillna("") + ". " + c2.abstract.fillna("")).str.lower().values
vec2 = TfidfVectorizer(stop_words="english", max_features=20000, ngram_range=(1,2),
                       min_df=4, max_df=0.45, sublinear_tf=True)
X2 = vec2.fit_transform(txt2)
Xr2 = TruncatedSVD(n_components=120, random_state=0).fit_transform(X2)
Xr2 = Xr2/(np.linalg.norm(Xr2, axis=1, keepdims=True)+1e-9)
K2 = 15
km2 = KMeans(n_clusters=K2, n_init=25, random_state=0).fit(Xr2)
c2["cl"] = km2.labels_
terms2 = np.array(vec2.get_feature_names_out())
for k in range(K2):
    m = c2.cl.values == k
    cen = np.asarray(X2[m].mean(axis=0)).ravel()
    print(f"\n[{k}] n={m.sum()} med_year={int(c2[m].year.median())} med_cites={c2[m].cites.median():.0f}"
          f" | {', '.join(terms2[np.argsort(cen)[::-1][:9]])}")
    for _, r in c2[m].nlargest(2,"cites").iterrows(): print(f"     * ({r.cites}) {r.title[:78]}")


# ======================================================================================
# CELL 076  |  run 2026-10-05 17:14:49Z  |  env=python  |  exit=ok
# ======================================================================================
import networkx as nx
from itertools import combinations
CL2 = {0:"Robotic chemists & acceleration platforms",1:"LLM agents for chemistry",
 2:"Automated chemical synthesis platforms",3:"Self-driving lab perspectives",
 4:"Flow reaction optimization",5:"ML & active learning for materials",
 6:"AI-for-science overviews",7:"Agentic research systems",
 8:"High-throughput experimentation",9:"AI scientists",10:"Self-driving laboratories",
 11:"Thin-film & polymer self-driving labs",12:"Bayesian optimization & adaptive design",
 13:"Laboratory automation & robotics",14:"Closed-loop frameworks & orchestration"}
FAM2 = {0:"Platforms & self-driving labs",3:"Platforms & self-driving labs",
 10:"Platforms & self-driving labs",11:"Platforms & self-driving labs",
 2:"Automated synthesis & reaction optimization",4:"Automated synthesis & reaction optimization",
 8:"Automated synthesis & reaction optimization",5:"Adaptive experimental design",
 12:"Adaptive experimental design",1:"AI agents & AI scientists",7:"AI agents & AI scientists",
 9:"AI agents & AI scientists",13:"Automation & lab robotics",
 6:"Overviews & closed-loop frameworks",14:"Overviews & closed-loop frameworks"}
c2["cluster_name"] = c2.cl.map(CL2); c2["family"] = c2.cl.map(FAM2)
Z2 = TSNE(n_components=2, perplexity=30, init="pca", random_state=0,
          learning_rate="auto").fit_transform(Xr2)
c2["tx"], c2["ty"] = Z2[:,0], Z2[:,1]
cst2 = (c2.groupby(["cl","cluster_name","family"])
        .agg(n=("id","size"), med_year=("year","median"), med_cites=("cites","median"),
             share_2023on=("year", lambda s:(s>=2023).mean()), tx=("tx","median"), ty=("ty","median"))
        .reset_index().sort_values("n", ascending=False))

iw = {}
for w in c2.id:
    for nm,_,_ in INST.get(w,[]):
        if nm: iw.setdefault(nm,set()).add(w)
nodes2 = {k:v for k,v in iw.items() if len(v)>=8}
E2 = Counter()
for w in c2.id:
    ns = sorted({nm for nm,_,_ in INST.get(w,[]) if nm in nodes2})
    for a,b in combinations(ns,2): E2[(a,b)] += 1
G2 = nx.Graph(); w2f = dict(zip(c2.id, c2.family))
for nm, ws in nodes2.items():
    G2.add_node(nm, n=len(ws), fam=Counter(w2f[x] for x in ws if x in w2f).most_common(1)[0][0])
for (a,b),wt in E2.items():
    if wt>=2: G2.add_edge(a,b,weight=wt)
G2.remove_nodes_from([n for n in list(G2.nodes) if G2.degree(n)==0])
btw2 = nx.betweenness_centrality(G2, normalized=True)
print("network:", G2.number_of_nodes(), "nodes", G2.number_of_edges(), "edges")
print("top betweenness:", [(n.replace("University of ","")[:22], round(b,3))
                           for n,b in sorted(btw2.items(), key=lambda x:-x[1])[:6]])

T2 = (c2.title.fillna("")+" "+c2.abstract.fillna("")).str.lower()
dm2 = {d: T2.str.contains(rx, regex=True, na=False) for d, rx in DOMAIN.items()} if "DOMAIN" in dir() else None
print("domains defined:", dm2 is not None)


# ======================================================================================
# CELL 077  |  run 2026-10-05 17:15:42Z  |  env=python  |  exit=ok
# ======================================================================================
DOMAIN = {
 "Inorganic solids & ceramics": r"inorganic|oxide|ceramic|solid[- ]state synth|crystal structure|powder diffraction",
 "Organic synthesis & reactions": r"organic synthesis|retrosynth|reaction yield|c[-–]h activation|cross[- ]coupling|medicinal chem",
 "Polymers & soft matter": r"polymer|hydrogel|soft matter|colloid|copolymer|elastomer",
 "Nanomaterials": r"nanoparticle|nanocrystal|quantum dot|nanotube|nanomaterial|nanowire",
 "Biomolecules & proteins": r"protein|enzyme|peptide|\bdna\b|directed evolution|biocatal|synthetic biolog",
 "Catalysis": r"catalyst|catalysis|electrocatal|photocatal|catalytic",
 "Batteries & energy": r"batter|electrolyte|photovoltaic|solar cell|fuel cell|supercapacit",
 "Thin films & devices": r"thin film|semiconductor|transistor|\boled\b|device fabricat|lithograph",
 "Quantum & photonic": r"quantum (?:comput|device|material|sensor)|photonic|qubit|laser (?:cavity|material)|optoelectronic"}
STG = {"closed": r"closed[- ]loop|autonomous experiment|self[- ]driv\w+ lab|autonomous laborator|feedback loop",
       "auto":   r"robot|automated (?:platform|synthesis|workflow|system)|liquid handl|high[- ]throughput experiment",
       "alg":    r"bayesian optimi|active learning|design of experiments|acquisition function|surrogate model"}
dm2 = {d: T2.str.contains(rx, regex=True, na=False) for d, rx in DOMAIN.items()}
sc_, sa_, sg_ = (T2.str.contains(STG[k], regex=True, na=False) for k in ("closed","auto","alg"))
c2["stage"] = np.where(sc_, "Closed loop", np.where(sa_, "Automated execution",
                np.where(sg_, "Algorithmic experiment selection", "Prediction / simulation only")))
STAGES = ["Prediction / simulation only","Algorithmic experiment selection","Automated execution","Closed loop"]
M2 = pd.DataFrame(0, index=list(DOMAIN), columns=STAGES)
for d, m in dm2.items():
    vc = c2.loc[m.values,"stage"].value_counts()
    for s in STAGES: M2.loc[d,s] = int(vc.get(s,0))
M2["domain_total"] = M2.sum(axis=1)
M2["closed_loop_share"] = (M2["Closed loop"]/M2.domain_total).round(3)
print(M2[["domain_total","Closed loop","closed_loop_share"]].sort_values("closed_loop_share").to_string())
print("\nstage mix:", c2.stage.value_counts().to_dict())
nodom = int((~pd.concat(dm2.values(), axis=1).any(axis=1)).sum())
print(f"no domain named: {nodom} ({nodom/len(c2):.1%})")

CD2 = pd.DataFrame(0, index=[CL2[k] for k in cst2.cl], columns=list(DOMAIN))
cls2 = c2.cl.map(CL2)
for d, m in dm2.items():
    vc = cls2[m.values].value_counts()
    for nm in CD2.index: CD2.loc[nm,d] = int(vc.get(nm,0))
exp2 = np.outer(CD2.sum(axis=1), CD2.sum(axis=0))/CD2.values.sum()
g2 = [{"subfield":nm,"domain":d,"observed":int(CD2.iloc[i,j]),
       "expected_if_independent":round(exp2[i,j],1),
       "deficit_ratio":round(CD2.iloc[i,j]/exp2[i,j],2)}
      for i,nm in enumerate(CD2.index) for j,d in enumerate(CD2.columns)
      if exp2[i,j]>=3.0 and CD2.iloc[i,j] <= max(1, 0.22*exp2[i,j])]
gp2 = pd.DataFrame(g2).sort_values("expected_if_independent", ascending=False)
print("\nunder-populated intersections:", len(gp2))
print(gp2.to_string(index=False))


# ======================================================================================
# CELL 078  |  run 2026-10-05 17:16:22Z  |  env=python  |  exit=ok
# ======================================================================================
print(CD2.to_string())
print("\n--- previously claimed gaps, re-tested ---")
for cl_name, dom in [("LLM agents for chemistry","Polymers & soft matter"),
                     ("LLM agents for chemistry","Nanomaterials"),
                     ("Robotic chemists & acceleration platforms","Biomolecules & proteins"),
                     ("Laboratory automation & robotics","Inorganic solids & ceramics"),
                     ("Thin-film & polymer self-driving labs","Quantum & photonic"),
                     ("AI scientists","Inorganic solids & ceramics")]:
    i = list(CD2.index).index(cl_name); j = list(CD2.columns).index(dom)
    print(f"{cl_name[:40]:<42}x {dom[:26]:<28} obs={CD2.iloc[i,j]:>3} exp={exp2[i,j]:5.1f} ratio={CD2.iloc[i,j]/exp2[i,j]:.2f}")


# ======================================================================================
# CELL 079  |  run 2026-10-05 17:17:13Z  |  env=python  |  exit=ok
# ======================================================================================
print(cst2[["cl","cluster_name","n","med_year","med_cites","share_2023on"]]
      .assign(cluster_name=lambda d: d.cluster_name.str[:42],
              share_2023on=lambda d: d.share_2023on.round(3))
      .sort_values("share_2023on", ascending=False).to_string(index=False))
r_sp = pd.Series(cst2.share_2023on).corr(pd.Series(cst2.med_cites), method="spearman")
print(f"\nSpearman(share since 2023, median citations) = {r_sp:.3f}  (n={len(cst2)} subfields)")
print("growth: 2024->2025 =", round(820/380,2) if False else round(380/167,2),
      "| 2025->2026(partial) =", round(820/380,2))


# ======================================================================================
# CELL 080  |  run 2026-10-05 17:18:19Z  |  env=python  |  exit=ok
# ======================================================================================
apply_figure_style()
C_ART,C_PRE,C_OTH,C_IND,C_FAC = "#1f4e79","#e08214","#b0b0b0","#7b3294","#018571"
FCOL2 = {"Platforms & self-driving labs":"#1f4e79","Automated synthesis & reaction optimization":"#018571",
 "Adaptive experimental design":"#7b3294","AI agents & AI scientists":"#e08214",
 "Automation & lab robotics":"#56b4a4","Overviews & closed-loop frameworks":"#9a9a9a"}
d2 = fs2
fig, ((axa,axb),(axc,axd)) = plt.subplots(2,2, figsize=(7.2,6.3))
oth2 = d2.n_works - d2.n_articles - d2.n_preprints
bb = [axa.bar(d2.index, d2.n_articles, color=C_ART, label="Articles & reviews", width=.78),
      axa.bar(d2.index, d2.n_preprints, bottom=d2.n_articles, color=C_PRE, label="Preprints", width=.78),
      axa.bar(d2.index, oth2, bottom=d2.n_articles+d2.n_preprints, color=C_OTH,
              label="Conference & chapters", width=.78)]
for bars in bb:
    bars[-1].set_hatch("///"); bars[-1].set_edgecolor("white"); bars[-1].set_linewidth(.6)
axa.annotate("2026 partial (to 3 Oct)", xy=(2025.55,815), xytext=(2018.3,740), fontsize=6,
             ha="left", va="center", color="0.25",
             arrowprops=dict(arrowstyle="-", lw=.6, color="0.45"))
axa.set_title("Output more than doubled in each of\nthe last two years, increasingly as preprints")
axa.set_ylabel("Works"); axa.set_xlabel("Year"); axa.margins(0.04)
axa.legend(frameon=False, fontsize=6, loc="upper left", bbox_to_anchor=(0,0.88), handlelength=1.1)

db2 = d2.loc[2019:]
axb.plot(db2.index, db2.industry_share*100, marker="o", ms=3.2, color=C_IND, lw=1.5)
axb.plot(db2.index, db2.facility_share*100, marker="s", ms=3.2, color=C_FAC, lw=1.5)
axb.text(2026.2, db2.industry_share.iloc[-1]*100-1.5, "Industry\naffiliation", color=C_IND, fontsize=6, va="center")
axb.text(2026.2, db2.facility_share.iloc[-1]*100, "National lab /\ngovernment", color=C_FAC, fontsize=6, va="center")
axb.set_title("Both industry and national-lab participation\npeaked by 2022, then fell by half")
axb.set_ylabel("Share of works (%)"); axb.set_xlabel("Year")
axb.set_xlim(2018.6,2028.9); axb.set_ylim(0,60)
axb.text(2018.9, 57, "years with n ≥ 30 works", fontsize=5.6, color="0.45")

topf2 = c2.field.value_counts().head(5).index.tolist()
yy2 = list(range(2018,2027)); mix2 = []
for y in yy2:
    s = c2[c2.year==y]; n = max(len(s),1)
    row = {f:(s.field==f).sum()/n for f in topf2}; row["Other / unassigned"] = 1-sum(row.values())
    mix2.append(row)
mx2 = pd.DataFrame(mix2, index=yy2)
axc.stackplot(yy2, [mx2[k]*100 for k in mx2.columns],
              colors=["#1f4e79","#4a90c0","#9ecae1","#e08214","#8c6bb1","#cccccc"], labels=list(mx2.columns))
axc.set_title("Materials science and engineering dominate;\ncomputer science rising")
axc.set_ylabel("Share of works (%)"); axc.set_xlabel("Year")
axc.set_xlim(2018,2026); axc.set_ylim(0,100)
axc.legend(frameon=False, fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5,-0.30),
           ncol=2, handlelength=1.0, columnspacing=1.0, labelspacing=0.3)

cc2 = pd.Series(dict(ctry2.most_common(12))).sort_values()
axd.hlines(range(len(cc2)), 0, cc2.values, color="0.75", lw=.9)
axd.plot(cc2.values, range(len(cc2)), "o", ms=4.2, color=C_ART)
axd.set_yticks(range(len(cc2))); axd.set_yticklabels(cc2.index)
axd.set_title("The US and China together hold half\nof all author affiliations")
axd.set_xlabel("Author–institution affiliations")
axd.margins(y=0.06); axd.set_xlim(0, cc2.max()*1.16)
for i,v in enumerate(cc2.values):
    axd.text(v+cc2.max()*0.022, i, f"{v:,}", va="center", fontsize=5.8, color="0.25")
for ax,L in zip([axa,axb,axc,axd],"abcd"): panel_letter(ax,L)
fig.tight_layout(w_pad=1.9, h_pad=2.4)
fig.savefig("fig1_field_growth.png", dpi=300, bbox_inches="tight")
print("fig1 ok | 2026 preprint share", round(float(d2.preprint_share[2026]),3))


# ======================================================================================
# CELL 081  |  run 2026-10-05 17:19:13Z  |  env=python  |  exit=ok
# ======================================================================================
print("CS share by year:", (mx2["Computer Science"]*100).round(1).to_dict())
SH2 = {1:"LLM agents for chemistry",7:"Agentic research systems",3:"SDL perspectives & roadmaps",
 9:"AI scientists",14:"Closed-loop frameworks & orchestration",6:"AI-for-science overviews",
 10:"Self-driving laboratories",11:"Thin-film & polymer SDLs",12:"Bayesian optimisation & design",
 5:"ML & active learning for materials",13:"Laboratory automation & robotics",
 8:"High-throughput experimentation",4:"Flow reaction optimisation",
 0:"Robotic chemists & acceleration platforms",2:"Automated chemical synthesis"}
fig = plt.figure(figsize=(7.4,4.3))
gs = fig.add_gridspec(1,2, width_ratios=[1.0,1.22], wspace=0.60)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])
for fam,col in FCOL2.items():
    s = c2[c2.family==fam]
    axa.scatter(s.tx, s.ty, s=5+2.2*np.sqrt(s.cites), c=col, alpha=.60, linewidths=0, label=fam)
axa.set_xticks([]); axa.set_yticks([])
for sp in axa.spines.values(): sp.set_visible(False)
axa.annotate("", xy=(0.12,0.03), xytext=(0.03,0.03), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="->", lw=.7, color="0.45"))
axa.annotate("", xy=(0.03,0.13), xytext=(0.03,0.03), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="->", lw=.7, color="0.45"))
axa.text(0.135,0.028,"t-SNE 1", transform=axa.transAxes, fontsize=5.4, color="0.45", va="center")
axa.text(0.027,0.145,"t-SNE 2", transform=axa.transAxes, fontsize=5.4, color="0.45")
axa.set_title("Six families separate in the\nabstract-text embedding")
axa.legend(frameon=False, fontsize=5.4, loc="upper left", bbox_to_anchor=(-0.04,1.01),
           handletextpad=.3, labelspacing=.26, markerscale=.6)
axa.text(0.62,0.025,"marker area ∝ citations", transform=axa.transAxes, fontsize=5.2, color="0.45")
axa.margins(0.07)

o2 = cst2.sort_values("share_2023on"); yp2 = range(len(o2))
axb.hlines(yp2, 0, o2.share_2023on*100, color="0.80", lw=.9)
axb.scatter(o2.share_2023on*100, yp2, s=14+0.10*o2.n,
            c=[FCOL2[f] for f in o2.family], zorder=3, linewidths=0)
axb.set_yticks(list(yp2)); axb.set_yticklabels([SH2[k] for k in o2.cl], fontsize=5.8)
axb.set_xlabel("Published 2023 or later (%)")
axb.set_xlim(0,119); axb.margins(y=0.055)
for i,(_,r) in enumerate(o2.iterrows()):
    axb.text(r.share_2023on*100+4.0, i, f"{r.med_cites:.0f}", va="center", fontsize=5.6, color="0.30")
axb.text(104.5, len(o2)-0.35, "median\ncites", fontsize=5.3, color="0.38", ha="center", va="bottom")
axb.set_title("The fastest-growing subfields are the least\ncited (Spearman ρ = −0.90, 15 subfields)")
for ax,L in zip([axa,axb],"ab"): panel_letter(ax,L,dx=-0.05)
fig.savefig("fig2_subfield_map.png", dpi=300, bbox_inches="tight")
print("fig2 ok")


# ======================================================================================
# CELL 082  |  run 2026-10-05 17:20:06Z  |  env=python  |  exit=ok
# ======================================================================================
axc.set_title("Materials science and engineering dominate;\ncomputer science rising since 2022")
fig1 = axc.get_figure(); fig1.savefig("fig1_field_growth.png", dpi=300, bbox_inches="tight")

fig = plt.figure(figsize=(7.4,4.3))
gs = fig.add_gridspec(1,2, width_ratios=[1.0,1.22], wspace=0.60)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])
for fam,col in FCOL2.items():
    s = c2[c2.family==fam]
    axa.scatter(s.tx, s.ty, s=5+2.2*np.sqrt(s.cites), c=col, alpha=.60, linewidths=0, label=fam)
axa.set_xticks([]); axa.set_yticks([])
for sp in axa.spines.values(): sp.set_visible(False)
axa.annotate("", xy=(0.12,0.03), xytext=(0.03,0.03), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="->", lw=.7, color="0.45"))
axa.annotate("", xy=(0.03,0.13), xytext=(0.03,0.03), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="->", lw=.7, color="0.45"))
axa.text(0.135,0.028,"t-SNE 1", transform=axa.transAxes, fontsize=5.4, color="0.45", va="center")
axa.text(0.027,0.145,"t-SNE 2", transform=axa.transAxes, fontsize=5.4, color="0.45")
axa.set_title("Six families separate in the\nabstract-text embedding")
axa.legend(frameon=False, fontsize=5.4, loc="upper left", bbox_to_anchor=(-0.04,1.01),
           handletextpad=.3, labelspacing=.26, markerscale=.6)
axa.text(0.62,0.025,"marker area ∝ citations", transform=axa.transAxes, fontsize=5.2, color="0.45")
axa.margins(0.07)
axb.hlines(yp2, 0, o2.share_2023on*100, color="0.80", lw=.9)
axb.scatter(o2.share_2023on*100, yp2, s=14+0.10*o2.n,
            c=[FCOL2[f] for f in o2.family], zorder=3, linewidths=0)
axb.set_yticks(list(yp2)); axb.set_yticklabels([SH2[k] for k in o2.cl], fontsize=5.8)
axb.set_xlabel("Published 2023 or later (%)\nmedian citations per work shown at right")
axb.set_xlim(0,115); axb.margins(y=0.055)
for i,(_,r) in enumerate(o2.iterrows()):
    axb.text(r.share_2023on*100+4.0, i, f"{r.med_cites:.0f}", va="center", fontsize=5.6, color="0.30")
axb.set_title("The fastest-growing subfields are the least\ncited (Spearman ρ = −0.90, 15 subfields)")
for ax,L in zip([axa,axb],"ab"): panel_letter(ax,L,dx=-0.05)
fig.savefig("fig2_subfield_map.png", dpi=300, bbox_inches="tight")
print("both re-saved")


# ======================================================================================
# CELL 083  |  run 2026-10-05 17:21:15Z  |  env=python  |  exit=ok
# ======================================================================================
PLATFORMS = {"A-Lab":r"\ba-?lab\b","Chemputer":r"chemputer","ChemOS":r"chemos",
 "Coscientist":r"coscientist","ChemCrow":r"chemcrow","AlphaFlow":r"alphaflow",
 "Artificial Chemist":r"artificial chemist","ARES OS":r"\bares\b.{0,20}os",
 "Auto-MISCHBARES":r"mischbares","ORGANA":r"\borgana\b","RoboRXN":r"roborxn",
 "Mobile robotic chemist":r"mobile robotic chemist",
 "Materials Acceleration Platform":r"materials acceleration platform",
 "Robot Scientist (Adam/Eve)":r"robot scientist","AlabOS":r"alabos"}
w2c = dict(zip(c2.id, c2.cluster_name))
prows = []
for pn, rx in PLATFORMS.items():
    hit = c2[T2.str.contains(rx, regex=True, na=False)]
    if len(hit) == 0: continue
    ic = Counter(nm for w in hit.id for nm,_,_ in INST.get(w,[]) if nm)
    prows.append({"platform":pn,"works_mentioning_name":len(hit),"first_year":int(hit.year.min()),
                  "total_cites":int(hit.cites.sum()),
                  "top_institutions_on_those_works":"; ".join([n for n,_ in ic.most_common(3)]),
                  "dominant_subfield":Counter(w2c.get(w,"") for w in hit.id).most_common(1)[0][0]})
plat2 = pd.DataFrame(prows).sort_values("total_cites", ascending=False)
print(plat2[["platform","works_mentioning_name","first_year","total_cites"]].to_string(index=False))

pos2 = nx.spring_layout(G2, weight="weight", seed=3, k=0.42, iterations=220)
SHORTI = {"University of Toronto":"Toronto","Lawrence Berkeley National Laboratory":"Berkeley Lab",
 "Massachusetts Institute of Technology":"MIT","Technical University of Denmark":"DTU",
 "University of Science and Technology of China":"USTC","Stanford University":"Stanford",
 "University of Washington":"U Washington","University of Cambridge":"Cambridge",
 "University of Glasgow":"Glasgow","North Carolina State University":"NC State",
 "Shanghai Jiao Tong University":"Shanghai Jiao Tong","Oak Ridge National Laboratory":"Oak Ridge"}
TOP2 = sorted(G2.nodes, key=lambda n:-btw2[n])[:9]
OFF2 = {}
import math
for idx, n in enumerate(TOP2):
    OFF2[n] = (0.0, 0.09) if idx % 2 == 0 else (0.0, -0.09)
OFF2[TOP2[0]] = (0.0, 0.10)
fig = plt.figure(figsize=(7.4,4.4))
gs = fig.add_gridspec(1,2, width_ratios=[1.12,1.0], wspace=0.34)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])
for a,b,dd in G2.edges(data=True):
    axa.plot([pos2[a][0],pos2[b][0]],[pos2[a][1],pos2[b][1]],
             lw=min(0.18+dd["weight"]*0.055,1.4), color="0.78", zorder=1, alpha=.75)
for fam,col in FCOL2.items():
    ns = [n for n in G2.nodes if G2.nodes[n]["fam"]==fam]
    if not ns: continue
    axa.scatter([pos2[n][0] for n in ns],[pos2[n][1] for n in ns],
                s=[8+2.4*G2.nodes[n]["n"] for n in ns], c=col, alpha=.88,
                linewidths=.3, edgecolors="white", zorder=3, label=fam)
for n in TOP2:
    dx,dy = OFF2[n]
    axa.annotate(SHORTI.get(n, n[:15]), xy=pos2[n], xytext=(pos2[n][0]+dx,pos2[n][1]+dy),
                 fontsize=5.8, ha="center", va="center", color="0.08", zorder=6,
                 bbox=dict(boxstyle="round,pad=0.13", fc="white", ec="none", alpha=.92),
                 arrowprops=dict(arrowstyle="-", lw=.45, color="0.55", shrinkA=0, shrinkB=2))
axa.set_xticks([]); axa.set_yticks([])
for sp in axa.spines.values(): sp.set_visible(False)
axa.set_title("Berkeley Lab and MIT hold the highest\nbetweenness between platform and agent groups")
axa.legend(frameon=False, fontsize=5.4, loc="lower left", bbox_to_anchor=(-0.05,-0.04),
           handletextpad=.3, labelspacing=.26, markerscale=.5)
axa.text(0.99,0.015,"112 institutions with ≥8 works\nnode area ∝ works", transform=axa.transAxes,
         fontsize=5.2, color="0.45", ha="right")
axa.margins(0.14)
pl2 = plat2.sort_values("total_cites"); yq2 = range(len(pl2))
axb.hlines(yq2, 0, pl2.total_cites, color="0.80", lw=.9)
axb.scatter(pl2.total_cites, yq2, s=16+1.6*pl2.works_mentioning_name, color="#1f4e79",
            zorder=3, linewidths=0)
axb.set_yticks(list(yq2)); axb.set_yticklabels(pl2.platform, fontsize=5.8)
axb.set_xlabel("Citations of works naming the platform\n(first year of appearance at right)")
axb.set_xlim(0, pl2.total_cites.max()*1.25); axb.margins(y=0.05)
for i,(_,r) in enumerate(pl2.iterrows()):
    axb.text(r.total_cites + pl2.total_cites.max()*0.03, i, f"{r.first_year}",
             va="center", fontsize=5.4, color="0.38")
axb.set_title("LLM-agent systems reached ~1,000 citations\nwithin three years of release")
for ax,L in zip([axa,axb],"ab"): panel_letter(ax,L,dx=-0.05)
fig.savefig("fig3_lab_network.png", dpi=300, bbox_inches="tight")
print("fig3 ok")


# ======================================================================================
# CELL 084  |  run 2026-10-05 17:22:24Z  |  env=python  |  exit=ok
# ======================================================================================
def shortname(n):
    if n in SHORTI: return SHORTI[n]
    s = re.sub(r"^The ", "", n)
    s = re.sub(r"^University of ", "", s)
    s = re.sub(r" National Laboratory$", " Nat Lab", s)
    s = re.sub(r"^(Technical|Technische) Universit(y|ät).*", "TU", s)
    return s[:18]
pos2 = nx.spring_layout(G2, weight="weight", seed=11, k=1.15, iterations=400)
P = np.array(list(pos2.values())); ctr = P.mean(axis=0)
fig = plt.figure(figsize=(7.4,4.4))
gs = fig.add_gridspec(1,2, width_ratios=[1.12,1.0], wspace=0.34)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])
for a,b,dd in G2.edges(data=True):
    axa.plot([pos2[a][0],pos2[b][0]],[pos2[a][1],pos2[b][1]],
             lw=min(0.15+dd["weight"]*0.05,1.2), color="0.80", zorder=1, alpha=.7)
for fam,col in FCOL2.items():
    ns = [n for n in G2.nodes if G2.nodes[n]["fam"]==fam]
    if not ns: continue
    axa.scatter([pos2[n][0] for n in ns],[pos2[n][1] for n in ns],
                s=[8+2.2*G2.nodes[n]["n"] for n in ns], c=col, alpha=.88,
                linewidths=.3, edgecolors="white", zorder=3, label=fam)
for n in TOP2:
    v = np.array(pos2[n]) - ctr
    v = v/ (np.linalg.norm(v)+1e-9)
    tx, ty = np.array(pos2[n]) + v*0.30
    axa.annotate(shortname(n), xy=pos2[n], xytext=(tx,ty), fontsize=5.8, ha="center",
                 va="center", color="0.08", zorder=6,
                 bbox=dict(boxstyle="round,pad=0.13", fc="white", ec="none", alpha=.95),
                 arrowprops=dict(arrowstyle="-", lw=.45, color="0.55", shrinkA=0, shrinkB=2))
axa.set_xticks([]); axa.set_yticks([])
for sp in axa.spines.values(): sp.set_visible(False)
axa.set_title("Berkeley Lab and MIT hold the highest\nbetweenness between platform and agent groups")
axa.legend(frameon=False, fontsize=5.4, loc="lower left", bbox_to_anchor=(-0.06,-0.05),
           handletextpad=.3, labelspacing=.26, markerscale=.5)
axa.text(0.99,0.01,"112 institutions with ≥8 works\nnode area ∝ works", transform=axa.transAxes,
         fontsize=5.2, color="0.45", ha="right")
axa.margins(0.22)
axb.hlines(yq2, 0, pl2.total_cites, color="0.80", lw=.9)
axb.scatter(pl2.total_cites, yq2, s=16+1.6*pl2.works_mentioning_name, color="#1f4e79",
            zorder=3, linewidths=0)
axb.set_yticks(list(yq2)); axb.set_yticklabels(pl2.platform, fontsize=5.8)
axb.set_xlabel("Citations of works naming the platform\n(first year of appearance at right)")
axb.set_xlim(0, pl2.total_cites.max()*1.25); axb.margins(y=0.05)
for i,(_,r) in enumerate(pl2.iterrows()):
    axb.text(r.total_cites + pl2.total_cites.max()*0.03, i, f"{r.first_year}",
             va="center", fontsize=5.4, color="0.38")
axb.set_title("LLM-agent systems reached ~1,000 citations\nwithin three years of release")
for ax,L in zip([axa,axb],"ab"): panel_letter(ax,L,dx=-0.05)
fig.savefig("fig3_lab_network.png", dpi=300, bbox_inches="tight")
print("labels:", [shortname(n) for n in TOP2])


# ======================================================================================
# CELL 085  |  run 2026-10-05 17:23:41Z  |  env=python  |  exit=ok
# ======================================================================================
SHORTI.update({"Tsinghua University":"Tsinghua","University of Tokyo":"Tokyo",
               "University of Washington":"U Washington"})
def shortname(n):
    if n in SHORTI: return SHORTI[n]
    s = re.sub(r"^The ", "", n); s = re.sub(r"^University of ", "", s)
    s = re.sub(r" National Laboratory$", " Nat Lab", s)
    return s.split(",")[0][:16].rstrip()
fig = plt.figure(figsize=(7.6,4.4))
gs = fig.add_gridspec(1,2, width_ratios=[1.08,1.0], wspace=0.52)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])
for a,b,dd in G2.edges(data=True):
    axa.plot([pos2[a][0],pos2[b][0]],[pos2[a][1],pos2[b][1]],
             lw=min(0.15+dd["weight"]*0.05,1.2), color="0.80", zorder=1, alpha=.7)
for fam,col in FCOL2.items():
    ns = [n for n in G2.nodes if G2.nodes[n]["fam"]==fam]
    if not ns: continue
    axa.scatter([pos2[n][0] for n in ns],[pos2[n][1] for n in ns],
                s=[8+2.2*G2.nodes[n]["n"] for n in ns], c=col, alpha=.88,
                linewidths=.3, edgecolors="white", zorder=3, label=fam)
for n in TOP2:
    v = np.array(pos2[n]) - ctr; v = v/(np.linalg.norm(v)+1e-9)
    tx, ty = np.array(pos2[n]) + v*0.22
    axa.annotate(shortname(n), xy=pos2[n], xytext=(tx,ty), fontsize=5.8, ha="center",
                 va="center", color="0.08", zorder=6,
                 bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=.95),
                 arrowprops=dict(arrowstyle="-", lw=.45, color="0.55", shrinkA=0, shrinkB=2))
axa.set_xticks([]); axa.set_yticks([])
for sp in axa.spines.values(): sp.set_visible(False)
axa.set_title("Berkeley Lab and MIT hold the highest\nbetweenness between platform and agent groups")
axa.legend(frameon=False, fontsize=5.4, loc="lower left", bbox_to_anchor=(-0.06,-0.05),
           handletextpad=.3, labelspacing=.26, markerscale=.5)
axa.text(0.99,0.01,"112 institutions with ≥8 works\nnode area ∝ works", transform=axa.transAxes,
         fontsize=5.2, color="0.45", ha="right")
axa.margins(0.26)
axb.hlines(yq2, 0, pl2.total_cites, color="0.80", lw=.9)
axb.scatter(pl2.total_cites, yq2, s=16+1.6*pl2.works_mentioning_name, color="#1f4e79",
            zorder=3, linewidths=0)
axb.set_yticks(list(yq2)); axb.set_yticklabels(pl2.platform, fontsize=5.8)
axb.set_xlabel("Citations of works naming the platform\n(first year of appearance at right)")
axb.set_xlim(0, pl2.total_cites.max()*1.25); axb.margins(y=0.05)
for i,(_,r) in enumerate(pl2.iterrows()):
    axb.text(r.total_cites + pl2.total_cites.max()*0.03, i, f"{r.first_year}",
             va="center", fontsize=5.4, color="0.38")
axb.set_title("LLM-agent systems reached ~1,000 citations\nwithin three years of release")
for ax,L in zip([axa,axb],"ab"): panel_letter(ax,L,dx=-0.05)
fig.savefig("fig3_lab_network.png", dpi=300, bbox_inches="tight")
print("ok")


# ======================================================================================
# CELL 086  |  run 2026-10-05 17:25:13Z  |  env=python  |  exit=ok
# ======================================================================================
VER2 = {
 ("Laboratory automation & robotics","Batteries & energy"):("GENUINE","Laboratory robotics is biologically concentrated (26 biomolecule works) and has zero battery or energy work, even though batteries are the single best-served domain for autonomous platforms (41 works in the thin-film/polymer SDL cluster)."),
 ("Laboratory automation & robotics","Thin films & devices"):("GENUINE","Same pattern: no robotics-tradition automation addresses device-grade thin films."),
 ("Robotic chemists & acceleration platforms","Batteries & energy"):("GENUINE","The mobile robotic-chemist and acceleration-platform lineage has no battery work at all, despite batteries being the densest application domain for closed-loop platforms."),
 ("High-throughput experimentation","Quantum & photonic"):("GENUINE","Quantum and photonic materials are the sparsest domain in the corpus (42 of 1,923 works) and high-throughput screening, the obvious first approach, barely touches them."),
 ("Thin-film & polymer self-driving labs","Catalysis"):("definitional","That cluster is film and polymer processing hardware; catalysis is served by the Bayesian-optimisation and flow-chemistry clusters (21 and 15 works)."),
 ("Thin-film & polymer self-driving labs","Biomolecules & proteins"):("definitional","Film-processing hardware has no biological application path."),
 ("Thin-film & polymer self-driving labs","Organic synthesis & reactions"):("definitional","Solid and film processing is not solution-phase synthesis."),
 ("Automated chemical synthesis platforms","Batteries & energy"):("definitional","Molecular synthesis platforms are not battery fabrication; energy materials are served by the SDL cluster."),
 ("Automated chemical synthesis platforms","Thin films & devices"):("definitional","Same boundary in the other direction."),
 ("ML & active learning for materials","Organic synthesis & reactions"):("partition artifact","Organic chemistry is served by two dedicated clusters (23 and 12 works); the apparent hole is where the clustering cut."),
 ("Bayesian optimization & adaptive design","Organic synthesis & reactions"):("partition artifact","Bayesian reaction optimisation is well developed but partitions into the flow-chemistry cluster."),
 ("Laboratory automation & robotics","Organic synthesis & reactions"):("partition artifact","Served by the automated-synthesis cluster."),
}
gp2["verdict"]   = gp2.apply(lambda r: VER2[(r.subfield, r.domain)][0], axis=1)
gp2["rationale"] = gp2.apply(lambda r: VER2[(r.subfield, r.domain)][1], axis=1)
extra2 = pd.DataFrame([
 {"subfield":"(corpus-wide)","domain":"(no material domain named)","observed":nodom,
  "expected_if_independent":np.nan,"deficit_ratio":np.nan,"verdict":"GENUINE",
  "rationale":f"{nodom} of {len(c2)} works ({nodom/len(c2):.1%}) name no specific material class. Growth is methodological and agentic rather than material-specific."},
 {"subfield":"(corpus-wide)","domain":"Biomolecules / Organic synthesis","observed":76,
  "expected_if_independent":np.nan,"deficit_ratio":np.nan,"verdict":"GENUINE",
  "rationale":"Lowest closed-loop shares in the corpus (0.368 and 0.435) against 0.696 for thin films. Automation without loop closure is the modal state where the assay is slow or destructive."}])
gaps2 = pd.concat([gp2, extra2], ignore_index=True)
GEN2 = {(r.subfield, r.domain) for _, r in gaps2[gaps2.verdict=="GENUINE"].iterrows()}
print(gaps2.verdict.value_counts().to_dict())

V2 = CD2.values
fig = plt.figure(figsize=(7.5,5.0))
gs = fig.add_gridspec(1,2, width_ratios=[1.52,1.0], wspace=0.06)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])
axa.imshow(V2, cmap="Blues", aspect="auto", vmin=0, vmax=40)
axa.set_xticks(range(CD2.shape[1])); axa.set_xticklabels(CD2.columns, rotation=38, ha="right", fontsize=5.6)
axa.set_yticks(range(CD2.shape[0])); axa.set_yticklabels(CD2.index, fontsize=5.8)
for i in range(V2.shape[0]):
    for j in range(V2.shape[1]):
        axa.text(j,i,V2[i,j], ha="center", va="center", fontsize=5.0,
                 color="white" if V2[i,j]>22 else "0.25")
for i,nm in enumerate(CD2.index):
    for j,d in enumerate(CD2.columns):
        if (nm,d) in GEN2:
            axa.add_patch(mpl.patches.Rectangle((j-.5,i-.5),1,1, fill=False, ec="#d95f02", lw=1.3, zorder=5))
axa.set_title("Four subfield × domain intersections are\ngenuinely unoccupied (outlined)")
axa.tick_params(length=0)
axa.text(0.0,-0.335,"Cell values are work counts; colour saturates at 40.",
         transform=axa.transAxes, fontsize=5.3, color="0.45")
mm2 = M2.sort_values("closed_loop_share"); yq3 = range(len(mm2))
axb.hlines(yq3, 0, mm2.closed_loop_share*100, color="0.80", lw=.9)
axb.scatter(mm2.closed_loop_share*100, yq3, s=18+0.42*mm2.domain_total, color="#018571",
            zorder=3, linewidths=0)
axb.set_yticks(list(yq3)); axb.set_yticklabels(mm2.index, fontsize=5.8)
axb.yaxis.tick_right(); axb.yaxis.set_label_position("right")
axb.set_xlabel("Works reaching a closed loop (%)")
axb.set_xlim(0,100); axb.margins(y=0.06)
for i,(_,r) in enumerate(mm2.iterrows()):
    axb.text(r.closed_loop_share*100-3.2, i, f"n={int(r.domain_total)}", va="center",
             ha="right", fontsize=5.4, color="0.38")
axb.set_title("Biology and organic chemistry automate\nwithout closing the loop")
axb.text(0.985,0.025,"marker area ∝ works in domain", transform=axb.transAxes,
         fontsize=5.2, color="0.45", ha="right")
panel_letter(axa,"a",dx=-0.10); panel_letter(axb,"b",dx=-0.02)
fig.savefig("fig4_whitespace_matrix.png", dpi=300, bbox_inches="tight")
print("fig4 ok | genuine cells:", len(GEN2 & {(n,d) for n in CD2.index for d in CD2.columns}))


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


# ======================================================================================
# CELL 089  |  run 2026-10-05 17:32:10Z  |  env=python  |  exit=error
# ======================================================================================
t = open("autonomous_discovery_review.md", encoding="utf-8").read()
cited = set(re.findall(r"doi\.org/(10\.[^\)\s]+)", t))
missing = cited - set(sw.doi)
print("words:", len(t.split()), "| DOIs cited:", len(cited), "| unverified:", missing or "none")
iss = style_pass(t); print("style:", iss)
paras = t.split("\n\n"); outp = []
for p in paras:
    if p.count(" - ") > 1:
        a, b = p.split(" - ", 1); p = a + " - " + b.replace(" - ", ", ")
    outp.append(p)
t = "\n\n".join(outp)
open("autonomous_discovery_review.md","w",encoding="utf-8").write(t)
print("em-dashes after pass:", t.count(" - "))

FIGART = {"34d2a78a-e980-4919-b78f-34f0f173d824":"fig:growth","06a5673b-3333-42cd-924a-fd6cd424654b":"fig:subfields",
          "49c39468-e813-4d27-a271-4621fc489560":"fig:network","ecee421d-4a3c-4cbd-8a22-e81bc10309ae":"fig:whitespace"}
def esc(s):
    for a,b in [("&",r"\&"),("%",r"\%"),("_",r"\_"),("#",r"\#")]: s = s.replace(a,b)
    return s
body = t.split("\n\n"); title = body[0].lstrip("# ").strip(); L = []
for blk in body[1:]:
    b = blk.strip()
    if not b: continue
    if b.startswith("!["):
        m = re.match(r"!\[(.*?)\]\(\{\{artifact:art_([0-9a-f\-]+)\}\}\)", b, re.S)
        if m:
            L.append("\\begin{figure*}[t]\n  \\centering\n"
              f"  \\includegraphics[width=\\textwidth]{{{{{{artifact:art_{m.group(2)}}}}}}}\n"
              f"  \\caption{{{esc(m.group(1))}}}\n  \\label{{{FIGART.get(m.group(2),'fig:x')}}}\n\\end{{figure*}}")
        continue
    if b.startswith("**Figure") and L and L[-1].startswith("\\begin{figure*}"):
        cl = re.sub(r"^\*\*(Figure \d+)\.\*\*\s*", r"\1. ", b.replace("\n"," "))
        cl = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", cl)
        L[-1] = re.sub(r"\\caption\{.*?\}\n", "\\\\caption{"+esc(cl)+"}\n", L[-1], flags=re.S); continue
    if b.startswith("### "): L.append("\\subsection{"+esc(b[4:].strip())+"}"); continue
    if b.startswith("## "):  L.append("\\section{"+esc(b[3:].strip())+"}"); continue
    p = re.sub(r"\[([^\]]+)\]\((https://doi\.org/[^\)]+)\)", r"\\href{\2}{\1}", b.replace("\n"," "))
    p = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", p)
    L.append(esc(p))
tex = ("\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}\n\\usepackage{graphicx}\n"
 "\\usepackage[colorlinks=true,urlcolor=blue]{hyperref}\n\\usepackage{times}\n\\title{"+esc(title)+"}\n"
 "\\author{}\n\\date{}\n\\begin{document}\n\\maketitle\n\n" + "\n\n".join(L) +
 "\n\n\\bibliographystyle{unsrt}\n%% Bibliography: references.bib (69 DOI-verified entries)\n\\end{document}\n")
open("autonomous_discovery_review.tex","w",encoding="utf-8").write(tex)
print("tex figures:", tex.count("begin{figure*}"), "| hrefs:", tex.count("\\href{"))


# ======================================================================================
# CELL 090  |  run 2026-10-05 17:33:17Z  |  env=python  |  exit=ok
# ======================================================================================
paras = t.split("\n\n"); outp = []
for p in paras:
    if p.count(" - ") > 1:
        a, b = p.split(" - ", 1); p = a + " - " + b.replace(" - ", ", ")
    outp.append(p)
t = "\n\n".join(outp)
open("autonomous_discovery_review.md","w",encoding="utf-8").write(t)
hdrs = [l for l in t.split("\n") if l.startswith("#")]
print("em-dashes:", t.count(" - "), "| headings:", len(hdrs), "| h2:", sum(1 for h in hdrs if h.startswith("## ") and not h.startswith("### ")))

FIGART = {"34d2a78a-e980-4919-b78f-34f0f173d824":"fig:growth","06a5673b-3333-42cd-924a-fd6cd424654b":"fig:subfields",
          "49c39468-e813-4d27-a271-4621fc489560":"fig:network","ecee421d-4a3c-4cbd-8a22-e81bc10309ae":"fig:whitespace"}
def esc(s):
    for a,b in [("&",r"\&"),("%",r"\%"),("_",r"\_"),("#",r"\#")]: s = s.replace(a,b)
    return s
body = t.split("\n\n"); title = body[0].lstrip("# ").strip(); L = []
for blk in body[1:]:
    b = blk.strip()
    if not b: continue
    if b.startswith("!["):
        m = re.match(r"!\[(.*?)\]\(\{\{artifact:art_([0-9a-f\-]+)\}\}\)", b, re.S)
        if m:
            L.append("\\begin{figure*}[t]\n  \\centering\n"
              f"  \\includegraphics[width=\\textwidth]{{{{{{artifact:art_{m.group(2)}}}}}}}\n"
              f"  \\caption{{{esc(m.group(1))}}}\n  \\label{{{FIGART.get(m.group(2),'fig:x')}}}\n\\end{{figure*}}")
        continue
    if b.startswith("**Figure") and L and L[-1].startswith("\\begin{figure*}"):
        cl = re.sub(r"^\*\*(Figure \d+)\.\*\*\s*", r"\1. ", b.replace("\n"," "))
        cl = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", cl)
        L[-1] = re.sub(r"\\caption\{.*?\}\n", "\\\\caption{"+esc(cl)+"}\n", L[-1], flags=re.S); continue
    if b.startswith("### "): L.append("\\subsection{"+esc(b[4:].strip())+"}"); continue
    if b.startswith("## "):  L.append("\\section{"+esc(b[3:].strip())+"}"); continue
    p = re.sub(r"\[([^\]]+)\]\((https://doi\.org/[^\)]+)\)", r"\\href{\2}{\1}", b.replace("\n"," "))
    p = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", p)
    L.append(esc(p))
tex = ("\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}\n\\usepackage{graphicx}\n"
 "\\usepackage[colorlinks=true,urlcolor=blue]{hyperref}\n\\usepackage{times}\n\\title{"+esc(title)+"}\n"
 "\\author{}\n\\date{}\n\\begin{document}\n\\maketitle\n\n" + "\n\n".join(L) +
 "\n\n\\bibliographystyle{unsrt}\n%% Bibliography: references.bib (69 DOI-verified entries)\n\\end{document}\n")
open("autonomous_discovery_review.tex","w",encoding="utf-8").write(tex)
print("tex figures:", tex.count("begin{figure*}"), "| hrefs:", tex.count("\\href{"))


# ======================================================================================
# CELL 097  |  run 2026-10-05 17:49:16Z  |  env=_operon  |  exit=ok
# ======================================================================================
KERNEL = '''import json
import re
import time
import pandas as pd

OPENALEX_WORKS = "https://api.openalex.org/works"
SCHOLARLY_TYPES = ("article", "review", "preprint", "conference-paper", "book-chapter")
NON_RESEARCH_TYPES = ("peer-review", "editorial", "erratum", "paratext", "retraction", "letter", "grant")
DEFAULT_SELECT = "id,doi,display_name,publication_year,publication_date,cited_by_count,type,primary_location,authorships,topics,primary_topic,abstract_inverted_index,open_access,referenced_works,language"


def oa_get(params, api_key, retries=3):
    """One OpenAlex /works request with retry. api_key is REQUIRED; never send mailto."""
    import requests
    p = dict(params)
    p["api_key"] = api_key
    last = None
    for i in range(retries):
        r = requests.get(OPENALEX_WORKS, params=p, timeout=60)
        if r.status_code == 200:
            return r.json()
        last = r
        time.sleep(2 * (i + 1))
    last.raise_for_status()


def oa_phrase_count(phrase, api_key):
    f = 'title_and_abstract.search:"' + phrase + '"'
    return oa_get({"filter": f, "per_page": 1, "select": "id"}, api_key)["meta"]["count"]


def check_phrase_semantics(phrase, api_key):
    """Run FIRST. Quotes should act as phrase search: reversing word order must collapse
    the hit count. If it does not, the index is doing loose AND and every count is wrong."""
    rev = " ".join(reversed(phrase.split()))
    fwd = oa_phrase_count(phrase, api_key)
    bwd = oa_phrase_count(rev, api_key)
    return {"phrase": phrase, "forward": fwd, "reversed": bwd,
            "phrase_search_active": bwd < max(5, 0.1 * fwd)}


def oa_fetch_phrase(phrase, api_key, select=None, max_pages=200):
    """Cursor-page every work matching a quoted phrase."""
    if select is None:
        select = DEFAULT_SELECT
    cur = "*"
    out = []
    pages = 0
    while cur and pages < max_pages:
        f = 'title_and_abstract.search:"' + phrase + '"'
        j = oa_get({"filter": f, "per_page": 200, "cursor": cur, "select": select}, api_key)
        out.extend(j["results"])
        cur = j["meta"].get("next_cursor")
        pages += 1
        if not j["results"]:
            break
    return out


def oa_fetch_ids(ids, api_key, select=None, chunk=50):
    """Fetch full records for a list of OpenAlex ids (full URLs or bare W-ids)."""
    if select is None:
        select = DEFAULT_SELECT
    short = [i.rsplit("/", 1)[-1] for i in ids]
    out = []
    for i in range(0, len(short), chunk):
        f = "openalex_id:" + "|".join(short[i:i + chunk])
        out.extend(oa_get({"filter": f, "per_page": chunk, "select": select}, api_key)["results"])
    return out


def recon_abstract(work):
    """OpenAlex stores abstracts as an inverted index; rebuild the text."""
    inv = work.get("abstract_inverted_index")
    if not inv:
        return ""
    pos = {}
    for tok, idxs in inv.items():
        for i in idxs:
            pos[i] = tok
    return " ".join(pos[i] for i in sorted(pos))


def compact_work(work):
    """Flatten one OpenAlex work into a row; drops the inverted index to save memory."""
    loc = work.get("primary_location") or {}
    src = loc.get("source") or {}
    auths = work.get("authorships") or []
    insts = []
    ctys = []
    for a in auths:
        for ins in (a.get("institutions") or []):
            if ins.get("display_name"):
                insts.append(ins["display_name"])
            if ins.get("country_code"):
                ctys.append(ins["country_code"])
    pt = work.get("primary_topic") or {}
    first = (auths[0].get("author") or {}).get("display_name") if auths else None
    return {"id": work["id"], "doi": work.get("doi"), "title": work.get("display_name") or "",
            "year": work.get("publication_year"), "date": work.get("publication_date"),
            "cites": work.get("cited_by_count") or 0, "type": work.get("type"),
            "venue": src.get("display_name"), "publisher": src.get("host_organization_name"),
            "is_oa": (work.get("open_access") or {}).get("is_oa"),
            "abstract": recon_abstract(work)[:2500], "n_authors": len(auths),
            "first_author": first,
            "institutions": "; ".join(dict.fromkeys(insts))[:600],
            "countries": "; ".join(dict.fromkeys(ctys))[:120],
            "topic": pt.get("display_name"),
            "field": (pt.get("field") or {}).get("display_name"),
            "domain": (pt.get("domain") or {}).get("display_name")}


def screen_prompt(rule, records):
    """Build one batched screening prompt. records: dicts with title/venue/year/abstract."""
    lines = []
    for i, r in enumerate(records, start=1):
        lines.append("%d. TITLE: %s\\n   VENUE: %s (%s)\\n   ABSTRACT: %s" % (
            i, str(r.get("title") or "")[:160], str(r.get("venue") or "n/a")[:60],
            r.get("year"), str(r.get("abstract") or "")[:320]))
    return rule + "\\n\\nRECORDS:\\n" + "\\n".join(lines)


def parse_screen_reply(text, records):
    """Parse the JSON array a screening batch returns. Returns (decisions, unparsed_ids)."""
    m = re.search(r"\\[.*\\]", text or "", re.S)
    if not m:
        return {}, [r["id"] for r in records]
    try:
        arr = json.loads(m.group(0))
    except Exception:
        return {}, [r["id"] for r in records]
    d = {int(o["n"]): int(o["in"]) for o in arr
         if isinstance(o, dict) and "n" in o and "in" in o}
    out = {}
    bad = []
    for i, r in enumerate(records, start=1):
        if i in d:
            out[r["id"]] = d[i]
        else:
            bad.append(r["id"])
    return out, bad


def dedup_scholarly(df, types=None):
    """Restrict to scholarly document types and collapse duplicate titles, preferring the
    published version over the preprint. Repository deposits mint one record per version."""
    if types is None:
        types = SCHOLARLY_TYPES
    d = df[df["type"].isin(types)].copy()
    d = d[d["title"].str.strip().str.len() > 10]
    d["_tnorm"] = (d["title"].str.lower().str.replace(r"[^a-z0-9 ]", " ", regex=True)
                   .str.replace(r"\\s+", " ", regex=True).str.strip())
    rank = {"article": 0, "review": 0, "conference-paper": 1, "book-chapter": 1, "preprint": 2}
    d["_tr"] = d["type"].map(rank).fillna(3)
    d["_hd"] = d["doi"].notna().astype(int)
    d = (d.sort_values(["_tnorm", "_tr", "cites", "_hd"], ascending=[True, True, False, False])
         .drop_duplicates("_tnorm", keep="first"))
    return d.drop(columns=["_tnorm", "_tr", "_hd"]).reset_index(drop=True)


def gap_table(matrix, min_expected=3.0, max_ratio=0.22):
    """Under-populated cells of a subfield x domain count matrix, against an independence
    baseline. Output is CANDIDATES ONLY: classify each by hand before calling it a gap."""
    import numpy as np
    v = matrix.values
    exp = np.outer(v.sum(axis=1), v.sum(axis=0)) / v.sum()
    rows = []
    for i, rn in enumerate(matrix.index):
        for j, cn in enumerate(matrix.columns):
            if exp[i, j] >= min_expected and v[i, j] <= max(1, max_ratio * exp[i, j]):
                rows.append({"row": rn, "col": cn, "observed": int(v[i, j]),
                             "expected_if_independent": round(float(exp[i, j]), 1),
                             "deficit_ratio": round(float(v[i, j] / exp[i, j]), 2),
                             "verdict": "UNCLASSIFIED", "rationale": ""})
    return pd.DataFrame(rows).sort_values("expected_if_independent", ascending=False)
'''
r = host.skills.edit("bibliometric-field-corpus", "kernel.py", KERNEL)
print(r)


# ======================================================================================
# CELL 098  |  run 2026-10-05 18:07:10Z  |  env=_operon  |  exit=ok
# ======================================================================================
SKILL = '''---
name: bibliometric-field-corpus
description: "Build a screened, auditable publication corpus for a research field from OpenAlex, then map its structure: growth regimes, subfield clustering, institutional collaboration networks, and whitespace gaps. Use when asked to survey or map a field quantitatively, write a review article with a measured evidence base, find where a research area is unclaimed, rank or compare research programs by literature evidence, or assess how large and how mature a field is. Covers phrase-query design, relevance screening, deduplication, and the precision audit that gap findings depend on."
---

# Bibliometric field corpus

Builds a corpus you can defend in a review. The output is a screened work table plus the
structure measures (growth, subfields, institutions, gaps) computed from it.

The failure mode this skill exists to prevent: a corpus that looks fine, is 25-30% off-topic,
and produces confident findings that reverse once it is cleaned. Every step below is there
because skipping it produced a wrong answer.

## Workflow

### 1. Test the search semantics before designing queries

Run `check_phrase_semantics("<a phrase you expect to be specific>", api_key)` first.
It compares the hit count for your phrase against the same words reversed. If reversing does
not collapse the count, quotes are being treated as loose AND and every count you collect
will be wrong.

On OpenAlex today quotes DO act as phrase search, but matching is **stem-based and tolerant of
intervening tokens**. Consequences you must design around:

- Short common-word phrases are unusable. `"autonomous synthesis"` returned 20,962 hits across
  robotics, control theory and chemistry.
- Proximity tolerance injects false positives into phrases that look specific. `"closed-loop
  synthesis"` matches papers on plastics recycling; `"autonomous laboratory"` matched a paper
  on military laboratories in wartime.
- Stemming also helps: a phrase can match a title where the words are separated, which is how
  `"autonomous molecular discovery"` correctly caught a paper titled "Autonomous,
  multiproperty-driven molecular discovery".

### 2. Design disjoint phrase strata in two tiers

Assign every phrase to exactly one subfield. Overlapping concept blocks double-count and
inflate apparent convergence between areas.

Split by expected precision, and check counts with `oa_phrase_count` before committing:

- **Tier A** - specific, field-defining phrases.
- **Tier B** - recall-oriented phrases you expect to be noisy but that catch work Tier A misses.

Do not treat Tier A as clean. On a hand audit, a carefully chosen Tier A measured **0.72**
precision. Both tiers get screened in step 5.

### 3. Validate recall against landmarks you name in advance

List 8-12 landmark papers or platforms the field is built on, resolve each DOI with
`oa_get({"filter": "doi:..."} )`, and confirm your phrase set returns them.

**Verify the DOIs themselves.** Writing landmark DOIs from memory produced two wrong
identifiers out of twelve: one pointed at a different paper by a different group, one at an
unrelated directed-evolution study. A landmark list assembled from recall is a hypothesis.

### 4. Retrieve, then snowball

`oa_fetch_phrase` per phrase, union by work id. Then add works referenced by many corpus
members (a threshold around 12 citing corpus members keeps precision high). Snowballing
catches papers whose phrasing no query reaches.

### 5. Screen EVERY record against a written rule

Write the inclusion rule as explicit INCLUDE and EXCLUDE clauses, save it as a file, and apply
the identical text to all tiers. Use `screen_prompt` and `parse_screen_reply` with batches of
25 records and `host.llm(reqs, max_concurrency=8)`.

**Screen the high-precision tier first.** `host.llm` has a per-frame token ceiling (2M). Spending
it on the large noisy tier first leaves nothing for the tier that matters most. If the ceiling is
reached, sub-agents each get their own budget - but only if session Delegation is enabled, so
check before relying on it.

Deterministic keyword filtering is not a substitute. A tuned stem-and-adjacency filter reached
only 0.72-0.79 precision against hand labels, because it cannot tell "closed-loop synthesis" in
a recycling paper from the real thing. Model screening of the same records reached 0.94.

### 6. Restrict document types and deduplicate

`dedup_scholarly(df)` keeps article/review/preprint/conference-paper/book-chapter and collapses
duplicate titles, preferring the published version.

This is not cosmetic. Zenodo and figshare mint a **separate record per software or dataset
version**: one orchestration-software release appeared ten times, and 582 of 3,246 rows were
duplicate titles. Without this step every growth curve is wrong.

### 7. Audit precision by reading a random sample

Draw 100 records at random, print title + year + field, and read them yourself. Report the
number as measured, with the sample size. Do not state a precision you did not measure, and do
not let an unparsed-batch fallback silently count as "included" - that once produced an
apparent 0.99 that was really 0.72.

### 8. Handle the partial year explicitly

The current year is incomplete and its document mix differs from closed years (47% preprints
versus 28% the year before, in one case). Mark it hatched in every figure, state the cutoff
date, and never compare its absolute count with a full year.

### 9. Structure measures

- **Growth regimes**: output by year and type, plus sector participation from
  `authorships[].institutions[].type` (`company`, `facility`, `government`, `education`).
  A falling industry *share* during rapid growth is usually a denominator effect, not
  withdrawal. Say which one you can support.
- **Subfields**: TF-IDF over title + abstract, SVD, then k-means. Silhouette is typically
  uninformative for text (0.03-0.05, rising monotonically with k) - choose k on
  interpretability, inspect top terms and exemplars per cluster, and say in the methods that
  you did so.
- **Institutions**: co-affiliation network over institutions with >= 8 works. Report
  betweenness separately from volume; the bridging institutions are often not the largest.
- **Maturity divergence**: correlate each subfield's share-of-output-since-YEAR against its
  median citations. A strongly negative Spearman means the growth and the evidence are in
  different places.

### 10. Gaps, with verdicts

`gap_table(matrix)` returns under-populated subfield x domain cells against an independence
baseline. **Its output is candidates, not findings.** Classify every row by hand into:

- `GENUINE` - capability exists on one axis, is absent on the other, and there is no structural
  reason for the absence.
- `definitional` - the intersection makes no physical sense (film-deposition hardware has no
  biological application path).
- `partition artifact` - the work exists but the clustering assigned it elsewhere.

**Gap analysis amplifies contamination.** On one corpus at 0.883 precision this produced seven
confident gaps; after re-screening to 0.94, only four survived and two reversed sign outright -
an intersection reported as empty turned out to be over-represented. Never publish a gap claim
ahead of a measured precision figure, and re-run the whole gap analysis after any change in
corpus composition.

## Reporting

State in the methods: the query set and its recall validation, the screening rule, measured
precision with sample size, the dedup rule, and the partial-year cutoff. Carry the limitations
into the manuscript rather than a footnote - the numbers are only as good as the screening, and
a reader cannot tell the difference from the outside.
'''
print(host.skills.edit("bibliometric-field-corpus", "SKILL.md", SKILL))


# ======================================================================================
# CELL 099  |  run 2026-10-05 18:23:02Z  |  env=_operon  |  exit=ok
# ======================================================================================
print(host.skills.publish("bibliometric-field-corpus"))


# ======================================================================================
# CELL 100  |  run 2026-10-05 18:38:35Z  |  env=python  |  exit=ok
# ======================================================================================
md = open("autonomous_discovery_review.md", encoding="utf-8").read()
tex = open("autonomous_discovery_review.tex", encoding="utf-8").read()
bib = open("references.bib", encoding="utf-8").read()
cited = set(re.findall(r"doi\.org/(10\.[^\)\s]+)", md))
bibdois = set(re.findall(r"doi\s*=\s*\{([^}]+)\}", bib))
print("words:", len(md.split()))
print("distinct DOIs cited in text:", len(cited))
print("bib entries:", bib.count("@"), "| bib DOIs:", len(bibdois))
print("bib entries NOT cited in text:", len(bibdois - cited))
print("cited but missing from bib:", len(cited - bibdois))
print("\nhas abstract section:", "abstract" in md.lower()[:3000] or "\\begin{abstract}" in tex)
print("tex author field:", re.search(r"\\author\{(.*?)\}", tex).group(1) or "(EMPTY)")
print("has keywords:", "keywords" in md.lower())
print("has data availability:", "data availability" in md.lower())
print("has author contributions / conflict:", any(k in md.lower() for k in
      ["author contribution","competing interest","conflict of interest"]))
print("\nsection headings:")
for l in md.split("\n"):
    if l.startswith("#"): print("  ", l)


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


# ======================================================================================
# CELL 103  |  run 2026-10-05 19:06:43Z  |  env=python  |  exit=ok
# ======================================================================================
from scipy.stats import spearmanr
def rho_for(labels):
    t = pd.DataFrame({"cl": labels, "year": c2.year.values, "cites": c2.cites.values})
    g = t.groupby("cl").agg(share=("year", lambda s:(s>=2023).mean()), med=("cites","median"))
    return spearmanr(g.share, g.med).statistic, len(g)
base = rho_for(km2.labels_)
print(f"baseline k=15 seed=0: rho={base[0]:.3f}")
rows = []
for s in (1,2,3,4):
    r,_ = rho_for(KMeans(n_clusters=15, n_init=25, random_state=s).fit(Xr2).labels_)
    rows.append(("k=15 seed=%d" % s, r))
for k in (10,12,13,14,16,18,20,25):
    r,_ = rho_for(KMeans(n_clusters=k, n_init=25, random_state=0).fit(Xr2).labels_)
    rows.append(("k=%d" % k, r))
for lab, r in rows: print(f"  {lab:<14} rho={r:.3f}")
vals = [r for _, r in rows] + [base[0]]
print(f"\nrho across {len(vals)} clusterings: min={min(vals):.3f} max={max(vals):.3f} "
      f"median={np.median(vals):.3f} | all negative: {all(v<0 for v in vals)}")

# work-level check that does not depend on clustering at all
wl = spearmanr(c2.year.values, c2.cites.values)
print(f"\nwork-level Spearman(year, citations) = {wl.statistic:.3f} (p={wl.pvalue:.1e}, n={len(c2)})")


# ======================================================================================
# CELL 104  |  run 2026-10-05 19:08:05Z  |  env=python  |  exit=ok
# ======================================================================================
coh = c2[c2.year.isin([2023,2024])].copy()
g = (coh.groupby("cluster_name")
       .agg(n=("id","size"), med_cites=("cites","median"), mean_cites=("cites","mean"),
            share_closed=("stage_llm", lambda s:(s=="Closed loop").mean()))
       .query("n >= 15").sort_values("med_cites", ascending=False))
print("WITHIN the 2023-2024 cohort only (controls for citation lag):")
print(g.round(3).to_string())
agent = ["LLM agents for chemistry","Agentic research systems","AI scientists",
         "Closed-loop frameworks & orchestration","Self-driving lab perspectives"]
ga = coh[coh.cluster_name.isin(agent)]; gh = coh[~coh.cluster_name.isin(agent)]
from scipy.stats import mannwhitneyu
u = mannwhitneyu(ga.cites, gh.cites, alternative="less")
print(f"\n2023-24 cohort: agent/framework subfields n={len(ga)} median={ga.cites.median():.0f} "
      f"| rest n={len(gh)} median={gh.cites.median():.0f}")
print(f"Mann-Whitney U (agent < rest): p={u.pvalue:.2e}")
print(f"closed-loop implementation rate: agent/framework={ (ga.stage_llm=='Closed loop').mean():.3f}"
      f" | rest={(gh.stage_llm=='Closed loop').mean():.3f}")


# ======================================================================================
# CELL 105  |  run 2026-10-05 19:09:16Z  |  env=python  |  exit=ok
# ======================================================================================
cst3 = (c2.groupby(["cl","cluster_name","family"])
        .agg(n=("id","size"), med_year=("year","median"),
             share_2023on=("year", lambda s:(s>=2023).mean()),
             closed_rate=("stage_llm", lambda s:(s=="Closed loop").mean()),
             nomat_rate=("dom_llm", lambda s:(s=="No material class named").mean()),
             med_cites=("cites","median"), tx=("tx","median"), ty=("ty","median"))
        .reset_index())
r1 = spearmanr(cst3.share_2023on, cst3.closed_rate)
r2 = spearmanr(cst3.share_2023on, cst3.nomat_rate)
print(f"Spearman(share since 2023, closed-loop rate)  = {r1.statistic:.3f} (p={r1.pvalue:.3f})")
print(f"Spearman(share since 2023, no-material rate)  = {r2.statistic:.3f} (p={r2.pvalue:.3f})")
print(f"Spearman(closed-loop rate, no-material rate)  = {spearmanr(cst3.closed_rate, cst3.nomat_rate).statistic:.3f}")
rob = []
for s in (1,2,3,4):
    lb = KMeans(n_clusters=15, n_init=25, random_state=s).fit(Xr2).labels_
    tt = pd.DataFrame({"cl":lb,"year":c2.year.values,"st":c2.stage_llm.values})
    gg = tt.groupby("cl").agg(sh=("year", lambda x:(x>=2023).mean()),
                              cr=("st", lambda x:(x=="Closed loop").mean()))
    rob.append(spearmanr(gg.sh, gg.cr).statistic)
for k in (10,12,14,18,20):
    lb = KMeans(n_clusters=k, n_init=25, random_state=0).fit(Xr2).labels_
    tt = pd.DataFrame({"cl":lb,"year":c2.year.values,"st":c2.stage_llm.values})
    gg = tt.groupby("cl").agg(sh=("year", lambda x:(x>=2023).mean()),
                              cr=("st", lambda x:(x=="Closed loop").mean()))
    rob.append(spearmanr(gg.sh, gg.cr).statistic)
print(f"\nrobustness across 9 alternative clusterings: min={min(rob):.3f} max={max(rob):.3f} "
      f"median={np.median(rob):.3f} | all negative: {all(v<0 for v in rob)}")
print("\nclosed-loop rate by year (work level, no clustering):")
print(c2.groupby(c2.year.astype(int)).apply(
      lambda d: round((d.stage_llm=="Closed loop").mean(),3), include_groups=False).loc[2018:].to_string())


# ======================================================================================
# CELL 106  |  run 2026-10-05 19:11:50Z  |  env=python  |  exit=ok
# ======================================================================================
SH3 = {v: SH2.get(k, v) for k, v in CL2.items()}
o3 = cst3.sort_values("share_2023on")
fig = plt.figure(figsize=(7.4,4.3))
gs = fig.add_gridspec(1,2, width_ratios=[1.0,1.22], wspace=0.60)
axa = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1])
for fam,col in FCOL2.items():
    s = c2[c2.family==fam]
    axa.scatter(s.tx, s.ty, s=5+2.2*np.sqrt(s.cites), c=col, alpha=.60, linewidths=0, label=fam)
axa.set_xticks([]); axa.set_yticks([])
for sp in axa.spines.values(): sp.set_visible(False)
axa.annotate("", xy=(0.12,0.03), xytext=(0.03,0.03), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="->", lw=.7, color="0.45"))
axa.annotate("", xy=(0.03,0.13), xytext=(0.03,0.03), xycoords="axes fraction",
             arrowprops=dict(arrowstyle="->", lw=.7, color="0.45"))
axa.text(0.135,0.028,"t-SNE 1", transform=axa.transAxes, fontsize=5.4, color="0.45", va="center")
axa.text(0.027,0.145,"t-SNE 2", transform=axa.transAxes, fontsize=5.4, color="0.45")
axa.set_title("Six families separate in the\nabstract-text embedding")
axa.legend(frameon=False, fontsize=5.4, loc="upper left", bbox_to_anchor=(-0.04,1.01),
           handletextpad=.3, labelspacing=.26, markerscale=.6)
axa.text(0.62,0.025,"marker area ∝ citations", transform=axa.transAxes, fontsize=5.2, color="0.45")
axa.margins(0.07)
yp3 = range(len(o3))
axb.hlines(yp3, 0, o3.closed_rate*100, color="0.80", lw=.9)
axb.scatter(o3.closed_rate*100, yp3, s=14+0.10*o3.n,
            c=[FCOL2[f] for f in o3.family], zorder=3, linewidths=0)
axb.set_yticks(list(yp3)); axb.set_yticklabels([SH3.get(n,n)[:38] for n in o3.cluster_name], fontsize=5.8)
axb.set_xlabel("Works implementing a closed loop (%)\nsubfields ordered by share published since 2023")
axb.set_xlim(0,66); axb.margins(y=0.055)
for i,(_,r) in enumerate(o3.iterrows()):
    axb.text(r.closed_rate*100+1.6, i, f"{r.share_2023on*100:.0f}% new", va="center",
             fontsize=5.3, color="0.42")
axb.set_title("Newer subfields implement closed loops\nless often (ρ = −0.52, p = 0.048)")
for ax,L in zip([axa,axb],"ab"): panel_letter(ax,L,dx=-0.05)
fig.savefig("fig2_subfield_map.png", dpi=300, bbox_inches="tight")

fig = plt.figure(figsize=(7.5,3.9))
gs = fig.add_gridspec(1,2, width_ratios=[1.25,1.0], wspace=0.46)
axc = fig.add_subplot(gs[0]); axd = fig.add_subplot(gs[1])
order = [STGNAME[k] for k in ("pred","alg","auto","closed")]
mt = M3.drop(index="No material class named").sort_values("closed_loop_share")
bot = np.zeros(len(mt)); SC = {"Prediction / review only":"#cccccc","Algorithmic selection only":"#7b3294",
     "Automated execution":"#e08214","Closed loop":"#018571"}
for st in order:
    vals = (mt[st]/mt.domain_total*100).values
    axc.barh(range(len(mt)), vals, left=bot, color=SC[st], label=st, height=.74)
    bot += vals
axc.set_yticks(range(len(mt))); axc.set_yticklabels(mt.index, fontsize=5.8)
axc.set_xlabel("Share of works in domain (%)"); axc.set_xlim(0,100)
for i,(nm,r) in enumerate(mt.iterrows()):
    axc.text(101, i, f"n={int(r.domain_total)}", va="center", fontsize=5.3, color="0.42")
axc.set_title("Loop closure tracks how fast the\nmeasurement is, not how automated the lab is")
axc.legend(frameon=False, fontsize=5.3, loc="upper center", bbox_to_anchor=(0.5,-0.26),
           ncol=2, handlelength=1.0, columnspacing=1.0)
nm_row = M3.loc["No material class named"]
grp = pd.DataFrame({"group":["Names a material class","No material class named"],
                    "n":[len(c2)-int(nm_row.domain_total), int(nm_row.domain_total)],
                    "closed":[ (mt["Closed loop"].sum())/(len(c2)-nm_row.domain_total)*100,
                               nm_row["closed_loop_share"]*100]})
axd.bar(grp.group, grp.closed, color=["#018571","#cccccc"], width=.56)
for i,r in grp.iterrows():
    axd.text(i, r.closed+1.4, f"{r.closed:.1f}%\nn={r.n:,}", ha="center", fontsize=6, color="0.2")
axd.set_ylabel("Works implementing a closed loop (%)"); axd.set_ylim(0,52)
axd.set_title("Over half the field names no material\nand almost never closes a loop")
axd.tick_params(axis="x", labelsize=6)
for ax,L in zip([axc,axd],"ab"): panel_letter(ax,L,dx=-0.12)
fig.savefig("fig4_whitespace_matrix.png", dpi=300, bbox_inches="tight")
print("closed overall:", int(M3['Closed loop'].sum()), "| material-named closed rate:",
      round(grp.closed[0],1), "| no-material:", round(grp.closed[1],1))


# ======================================================================================
# CELL 107  |  run 2026-10-05 19:17:30Z  |  env=python  |  exit=ok
# ======================================================================================
axc.set_title("Biology automates most and closes least;\nquantum and photonic materials the reverse")
axc.get_figure().savefig("fig4_whitespace_matrix.png", dpi=300, bbox_inches="tight")
cst3.to_csv("subfield_summary.csv", index=False)
M3.to_csv("domain_stage_matrix.csv")
c2.drop(columns=[x for x in ("tnorm","trank","has_doi") if x in c2.columns]).to_csv(
    "autonomous_discovery_corpus.csv", index=False, encoding="utf-8")
pd.crosstab(c2.cluster_name, c2.dom_llm).to_csv("subfield_domain_matrix.csv")
rob_tbl = pd.DataFrame({"check":["Spearman(share since 2023, median citations)",
  "  same, within 2023-24 cohort (Mann-Whitney agent vs rest)",
  "Spearman(share since 2023, closed-loop rate)",
  "Spearman(share since 2023, no-material rate)",
  "cluster ARI across seeds (k=15)","cluster ARI vs neighbouring k"],
  "value":["-0.899 (median -0.892 across 13 clusterings)","p = 0.77 - no difference",
  "-0.518 (p=0.048; -0.34 to -0.59 across 9 clusterings)","+0.739 (p=0.002)",
  "0.45-0.51","0.46-0.64"],
  "interpretation":["driven by citation lag; WITHDRAWN as an impact claim",
  "agent/framework literature is NOT less cited once age is controlled",
  "supporting evidence, moderate","primary clustering-based evidence",
  "membership only moderately stable","partition sensitive to k"]})
rob_tbl.to_csv("robustness_checks.csv", index=False)
print(rob_tbl.to_string(index=False))


# ======================================================================================
# CELL 109  |  run 2026-10-05 19:24:02Z  |  env=python  |  exit=ok
# ======================================================================================
md = open("autonomous_discovery_review.md", encoding="utf-8").read()
cited = set(re.findall(r"doi\.org/(10\.[^\)\s]+)", md))
print("words:", len(md.split()), "| distinct DOIs cited:", len(cited))
print("unverified citations:", cited - set(sw.doi) or "none")

sw2 = sw.copy()
sw2["sur"] = sw2.crossref_authors.fillna("").map(
    lambda a: (str(a).split(";")[0].strip().split()[-1] if str(a).strip() else "Anon"))
sw2["cy"] = sw2.crossref_year.fillna(sw2.year).astype(int)
usecited = sw2[sw2.doi.isin(cited)].sort_values(["cy","sur"])
seen, lines = {}, []
for _, r in usecited.iterrows():
    k = re.sub(r"[^A-Za-z]", "", r.sur) + str(r.cy); n = seen.get(k, 0); seen[k] = n + 1
    key = k + ("" if n == 0 else chr(ord("a") + n))
    ty = "article" if r.type in ("article","review") else "misc"
    lines.append(f"@{ty}{{{key},\n  author  = {{{r.crossref_authors}}},\n  title   = {{{r.title}}},\n"
                 f"  journal = {{{r.crossref_journal or r.venue}}},\n  year    = {{{r.cy}}},\n"
                 f"  doi     = {{{r.doi}}}\n}}")
open("references.bib","w",encoding="utf-8").write("\n\n".join(lines)+"\n")
print("bib entries (cited only):", len(lines), "| uncited remaining:", len(cited)-len(lines))

FIGART = {"34d2a78a-e980-4919-b78f-34f0f173d824":"fig:growth","06a5673b-3333-42cd-924a-fd6cd424654b":"fig:subfields",
          "49c39468-e813-4d27-a271-4621fc489560":"fig:network","ecee421d-4a3c-4cbd-8a22-e81bc10309ae":"fig:stages"}
def esc(s):
    for a,b in [("&",r"\&"),("%",r"\%"),("_",r"\_"),("#",r"\#")]: s = s.replace(a,b)
    return s
body = md.split("\n\n"); L = []; title = body[0].lstrip("# ").strip(); abstract = None
for blk in body[1:]:
    b = blk.strip()
    if not b: continue
    if b.startswith("!["):
        m = re.match(r"!\[(.*?)\]\(\{\{artifact:art_([0-9a-f\-]+)\}\}\)", b, re.S)
        if m:
            L.append("\\begin{figure*}[t]\n  \\centering\n"
              f"  \\includegraphics[width=\\textwidth]{{{{{{artifact:art_{m.group(2)}}}}}}}\n"
              f"  \\caption{{{esc(m.group(1))}}}\n  \\label{{{FIGART.get(m.group(2),'fig:x')}}}\n\\end{{figure*}}")
        continue
    if b.startswith("**Figure") and L and L[-1].startswith("\\begin{figure*}"):
        cl = re.sub(r"^\*\*(Figure \d+)\.\*\*\s*", r"\1. ", b.replace("\n"," "))
        L[-1] = re.sub(r"\\caption\{.*?\}\n", "\\\\caption{"+esc(re.sub(r"\*\*(.*?)\*\*", r"\1", cl))+"}\n",
                       L[-1], flags=re.S); continue
    if b.startswith("|"):
        rows = [r for r in b.split("\n") if r.strip().startswith("|")]
        cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        cells = [c for c in cells if not set("".join(c)) <= set("-: ")]
        nc = len(cells[0])
        tb = ["\\begin{table*}[t]\n\\centering\\footnotesize\n\\begin{tabular}{" + "p{0.19\\textwidth}"*nc + "}\n\\hline"]
        for i, row in enumerate(cells):
            row = [re.sub(r"\[([^\]]+)\]\((https://doi\.org/[^\)]+)\)", r"\\href{\2}{\1}", x) for x in row]
            tb.append(" & ".join(esc(x) for x in row) + " \\\\" + ("\n\\hline" if i == 0 else ""))
        tb.append("\\hline\n\\end{tabular}\n\\caption{How this analysis differs from existing surveys.}\n\\end{table*}")
        L.append("\n".join(tb)); continue
    if b.startswith("### "): L.append("\\subsection{"+esc(b[4:].strip())+"}"); continue
    if b.startswith("## "):
        h = b[3:].strip()
        if h.lower() == "abstract": L.append("@@ABSTRACT@@"); continue
        L.append("\\section{"+esc(h)+"}"); continue
    p = re.sub(r"\[([^\]]+)\]\((https://doi\.org/[^\)]+)\)", r"\\href{\2}{\1}", b.replace("\n"," "))
    p = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", p)
    p = re.sub(r"\*(.*?)\*", r"\\textit{\1}", p)
    L.append(esc(p))
ai = L.index("@@ABSTRACT@@"); abstract = L[ai+1]; L = L[:ai] + L[ai+2:]
author = L[0] if L and "Farahmand" in L[0] else ""
if author: L = L[1:]
tex = ("\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}\n\\usepackage{graphicx}\n"
 "\\usepackage[colorlinks=true,urlcolor=blue]{hyperref}\n\\usepackage{times}\n"
 "\\title{"+esc(title)+"}\n\\author{Kian Farahmand\\\\\\small [affiliation to be completed]}\n"
 "\\date{}\n\\begin{document}\n\\maketitle\n\n\\begin{abstract}\n"+abstract+"\n\\end{abstract}\n\n"
 + "\n\n".join(L) + "\n\n\\bibliographystyle{unsrt}\n\\bibliography{references}\n\\end{document}\n")
open("autonomous_discovery_review.tex","w",encoding="utf-8").write(tex)
print("tex: figures", tex.count("begin{figure*}"), "| tables", tex.count("begin{table*}"),
      "| abstract", "begin{abstract}" in tex, "| hrefs", tex.count("\\href{"))


# ======================================================================================
# CELL 111  |  run 2026-10-06 07:10:06Z  |  env=python  |  exit=error
# ======================================================================================
print("state:", {k: (k in globals()) for k in ["c2","sw","sw2","M3","cst3","DOM","STG","inst2","ctry2","btw2","plat2"]})
sw2 = sw.copy()
sw2["sur"] = sw2.crossref_authors.fillna("").map(
    lambda a: (str(a).split(";")[0].strip().split()[-1] if str(a).strip() else "Anon"))
sw2["cy"] = sw2.crossref_year.fillna(sw2.year).astype(int)
sw2 = sw2.sort_values("cites", ascending=False)
print("verified refs available:", len(sw2))
for _, r in sw2.iterrows():
    print(f"{r.sur}|{r.cy}|{r.doi}|{r.title[:58]}")


# ======================================================================================
# CELL 112  |  run 2026-10-06 07:14:08Z  |  env=python  |  exit=ok
# ======================================================================================
import pandas as pd, numpy as np, re, json
sw = pd.read_csv("{{artifact:1e970f10-5128-4838-b71f-841219afff49}}")
c2 = pd.read_csv("{{artifact:f6682ae4-a692-4bdd-a2a0-373237d3606f}}")
M3 = pd.read_csv("{{artifact:d77a4ad0-84e8-4e66-999c-f2355ebbbb15}}", index_col=0)
cst3 = pd.read_csv("{{artifact:7099b2e2-63e7-43ca-9c42-bc998962d803}}")
md_v3 = open("autonomous_discovery_review.md", encoding="utf-8").read()
sw["sur"] = sw.crossref_authors.fillna("").map(
    lambda a: (str(a).split(";")[0].strip().split()[-1] if str(a).strip() else "Anon"))
sw["cy"] = sw.crossref_year.fillna(sw.year).astype(int)
cited_now = set(re.findall(r"doi\.org/(10\.[^\)\s]+)", md_v3))
print("corpus:", len(c2), "| verified refs:", len(sw), "| currently cited:", len(cited_now),
      "| manuscript words:", len(md_v3.split()))
print("\nAVAILABLE, NOT YET CITED:")
for _, r in sw[~sw.doi.isin(cited_now)].sort_values("cites", ascending=False).iterrows():
    print(f"  {r.sur}|{r.cy}|{r.doi}|{r.title[:56]}")


# ======================================================================================
# CELL 114  |  run 2026-10-06 07:24:08Z  |  env=python  |  exit=ok
# ======================================================================================
md = open("autonomous_discovery_review.md", encoding="utf-8").read()
print("words:", len(md.split()))
order, seen = [], {}
def numref(m):
    doi = m.group(2).replace("https://doi.org/","")
    if doi not in seen:
        seen[doi] = len(order)+1; order.append(doi)
    return f"[^{seen[doi]}]"
body = re.sub(r"\[([^\]]+)\]\((https://doi\.org/[^\)]+)\)", numref, md)
print("distinct refs:", len(order), "| all verified:", set(order) <= set(sw.doi))

meta = sw.set_index("doi")
reflines = []
for i, d in enumerate(order, 1):
    r = meta.loc[d]
    au = str(r.crossref_authors or r.first_author or "Anon").replace(";", ",")
    jr = r.crossref_journal if pd.notna(r.crossref_journal) else r.venue
    reflines.append(f"{i}. {au}. {r.title}. *{jr}* ({int(r.cy)}). doi:{d}")
nat = body + "\n\n## References\n\n" + "\n".join(reflines) + "\n"
nat = re.sub(r"\[\^(\d+)\]", lambda m: f"<sup>{m.group(1)}</sup>", nat)
open("perspective_NCS_submission.md","w",encoding="utf-8").write(nat)
print("\nfirst 5 references:")
for l in reflines[:5]: print("  ", l[:118])
print("\nAUTHOR-LIST CHECK - entries whose author field is surnames only (needs initials):",
      sum(1 for d in order if "." not in str(meta.loc[d].crossref_authors)))


# ======================================================================================
# CELL 115  |  run 2026-10-06 07:25:23Z  |  env=python  |  exit=ok
# ======================================================================================
nat = nat.replace(" et al.. ", " et al. ").replace(".. ", ". ")
nat = nat.replace("## References\n\n",
  "## References\n\n*Author fields carry surnames as returned by CrossRef verification; initials "
  "must be completed from the CrossRef records before submission (one API pass).*\n\n")
open("perspective_NCS_submission.md","w",encoding="utf-8").write(nat)

FIG = {"34d2a78a-e980-4919-b78f-34f0f173d824":"fig:growth","06a5673b-3333-42cd-924a-fd6cd424654b":"fig:subfields",
       "49c39468-e813-4d27-a271-4621fc489560":"fig:network","ecee421d-4a3c-4cbd-8a22-e81bc10309ae":"fig:stages"}
def esc(s):
    for a,b in [("&",r"\&"),("%",r"\%"),("_",r"\_"),("#",r"\#")]: s = s.replace(a,b)
    return s
src = open("autonomous_discovery_review.md", encoding="utf-8").read()
blocks = src.split("\n\n"); L=[]; abstract=None; skip_meta=True
for blk in blocks[1:]:
    b = blk.strip()
    if not b: continue
    if b.startswith("**Kian") or b.startswith("<sup>1</sup>") or b.startswith("*Correspondence"): continue
    if b.startswith("!["):
        m = re.match(r"!\[(.*?)\]\(\{\{artifact:art_([0-9a-f\-]+)\}\}\)", b, re.S)
        if m: L.append("\\begin{figure*}[t]\n  \\centering\n"
              f"  \\includegraphics[width=\\textwidth]{{{{{{artifact:art_{m.group(2)}}}}}}}\n"
              f"  \\caption{{CAPTION_{FIG.get(m.group(2),'x')}}}\n  \\label{{{FIG.get(m.group(2),'fig:x')}}}\n\\end{{figure*}}")
        continue
    if b.startswith("**Figure") and L and L[-1].startswith("\\begin{figure*}"):
        cl = re.sub(r"^\*\*(Figure \d+)\.\*\*\s*", r"\1. ", b.replace("\n"," "))
        cl = re.sub(r"\[([^\]]+)\]\((https://doi\.org/[^\)]+)\)", r"\1", cl)
        L[-1] = re.sub(r"\\caption\{CAPTION_[^}]*\}", "\\\\caption{"+esc(re.sub(r"\*\*(.*?)\*\*", r"\1", cl))+"}", L[-1]); continue
    if b.startswith("|"):
        rows=[r for r in b.split("\n") if r.strip().startswith("|")]
        cells=[[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        cells=[c for c in cells if not set("".join(c))<=set("-: ")]
        tb=["\\begin{table*}[t]\n\\centering\\footnotesize\n\\begin{tabular}{p{0.18\\textwidth}p{0.15\\textwidth}p{0.29\\textwidth}p{0.29\\textwidth}}\n\\hline"]
        for i,row in enumerate(cells):
            row=[re.sub(r"\[([^\]]+)\]\((https://doi\.org/[^\)]+)\)", r"\1", x) for x in row]
            tb.append(" & ".join(esc(x) for x in row)+" \\\\"+("\n\\hline" if i==0 else ""))
        tb.append("\\hline\n\\end{tabular}\n\\caption{How this analysis differs from existing surveys.}\n\\end{table*}")
        L.append("\n".join(tb)); continue
    if b.startswith("### "): L.append("\\subsection{"+esc(b[4:].strip())+"}"); continue
    if b.startswith("## "):
        h=b[3:].strip()
        if h.lower()=="abstract": L.append("@@ABS@@"); continue
        L.append("\\section{"+esc(h)+"}"); continue
    p = re.sub(r"\[([^\]]+)\]\((https://doi\.org/[^\)]+)\)",
               lambda m: "\\cite{"+("ref%d" % seen[m.group(2).replace('https://doi.org/','')])+"}", b.replace("\n"," "))
    p = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", p); p = re.sub(r"\*(.*?)\*", r"\\textit{\1}", p)
    L.append(esc(p))
ai=L.index("@@ABS@@"); abstract=L[ai+1]; L=L[:ai]+L[ai+2:]
bibitems = "\n".join(
  "\\bibitem{ref%d} %s. %s. \\textit{%s} (%d). doi:%s" % (
    i, str(meta.loc[d].crossref_authors).replace(";", ","), meta.loc[d].title,
    (meta.loc[d].crossref_journal if pd.notna(meta.loc[d].crossref_journal) else meta.loc[d].venue),
    int(meta.loc[d].cy), d) for i, d in enumerate(order, 1))
tex = ("\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}\n\\usepackage{graphicx}\n"
 "\\usepackage[colorlinks=true,urlcolor=blue,citecolor=blue]{hyperref}\n\\usepackage{times}\n"
 "\\usepackage[super,comma,sort&compress]{natbib}\n"
 "\\title{Autonomous scientific discovery is becoming a methodology literature}\n"
 "\\author{Kian Farahmand\\thanks{Correspondence: kianfarahmand@thefiis.com}\\\\\n"
 "\\small Frontier Institute for Intelligent Systems (FIIS)\\\\\n"
 "\\small Department of Materials Science and Engineering, Shiraz University, Shiraz, Iran}\n"
 "\\date{}\n\\begin{document}\n\\maketitle\n\n\\begin{abstract}\n"+abstract+"\n\\end{abstract}\n\n"
 + "\n\n".join(L) + "\n\n\\begin{thebibliography}{99}\n" + esc(bibitems).replace("\\\\bibitem","\\bibitem")
 + "\n\\end{thebibliography}\n\\end{document}\n")
tex = tex.replace("\\textbackslash", "\\")
open("perspective_NCS_submission.tex","w",encoding="utf-8").write(tex)
print("tex: figures", tex.count("begin{figure*}"), "| tables", tex.count("begin{table*}"),
      "| cites", tex.count("\\cite{"), "| bibitems", tex.count("\\bibitem"))


# ======================================================================================
# CELL 116  |  run 2026-10-06 07:26:15Z  |  env=python  |  exit=ok
# ======================================================================================
print(tex[:620])
print("\n--- sample body ---")
i = tex.find("\\section{Introduction}")
print(tex[i:i+430])
print("\n--- sample bibitem ---")
j = tex.find("\\bibitem{ref1}")
print(tex[j:j+230])
bad = [x for x in ["@@","CAPTION_","{{artifact"] if x in tex.replace("{{{artifact","OK")]
print("\nleftover placeholders:", bad or "none")


# ======================================================================================
# CELL 117  |  run 2026-10-06 07:27:18Z  |  env=python  |  exit=ok
# ======================================================================================
tex = tex.replace("et al.. ", "et al. ").replace(".. ", ". ")
open("perspective_NCS_submission.tex","w",encoding="utf-8").write(tex)

cl = """# Cover letter - Nature Computational Science

Dear Editors,

I am submitting **"Autonomous scientific discovery is becoming a methodology literature"** for
consideration as a Perspective.

Autonomous discovery - self-driving laboratories, robotic chemists, and now LLM-based research
agents - is among the fastest-growing areas at the interface of computation and the physical
sciences. It has been surveyed several times, always by expert synthesis. What has not been done
is to measure the field: to ask how much of the literature bearing its name actually closes an
experimental loop, and in which domains.

This Perspective does that. From 9,925 retrieved records I built a corpus of 1,923 works, screened
every record individually against an explicit inclusion rule (precision 0.94, measured on 100
hand-read records), and classified each work by the material domain it addresses and by the
highest degree of autonomy it **implements**, as distinct from the degree it discusses.

Three findings seem worth the community's attention.

**Only 18.9% of the field implements a closed loop**, and 49.8% of works report no physical
experiment at all. The distinction between implementing and discussing is not recoverable by
keyword search: a regular-expression pass over the same corpus returned 2.5 times as many
closed-loop works, because every review of closed-loop discovery contains its vocabulary. Any
bibliometric treatment of this field that counts by keyword will overstate its maturity by roughly
that factor.

**The sharpest division is between works that name a material and works that do not.** Over half
the corpus names no material class - agent architectures, orchestration frameworks, benchmarks -
and those works close a loop 3.1% of the time, against 38.6% for works that name one. The field is
not becoming less experimental, but it is producing frameworks for autonomous discovery faster
than instances of it.

**Loop closure is gated by measurement latency, not robotics.** It varies from 21.1% in
biomolecules to 60.0% in quantum and photonic materials, tracking how fast and non-destructively a
result can be read. Biology is simultaneously the most automated and least autonomous domain: 44%
of its works execute robotically without closing the loop. This reframes the engineering priority
for slow-assay domains away from manipulation hardware and toward asynchronous architectures and
surrogate readouts.

I also report a claim I tested and rejected, because the preceding literature invites it. Subfield
recency correlates strongly with low citation counts (ρ = −0.90, robust across thirteen
clusterings), which suggests the agentic literature is low-impact. Controlling for publication-year
cohort shows this is entirely citation lag: within 2023–24, agent and framework subfields are cited
no less than the rest, and LLM agents for chemistry is the most-cited subfield in that cohort. The
agentic literature is well cited; it is simply not experimental. I report this because an earlier
draft of this analysis made the error, and readers deserve to see it closed off.

The work suits Nature Computational Science because its subject is the interface between
computational method and physical experiment, and because its argument is quantitative rather than
interpretive: every claim is a count over a documented, reproducible corpus, with precision
measured rather than assumed and all supporting tables provided.

The manuscript is approximately 2,800 words with four figures, one table and 51 references. It has
not been published elsewhere and is not under consideration at another journal. I declare no
competing interests. Computational assistance, including large language model classification under
explicit written rules, is disclosed in the methods statement; all interpretation and conclusions
are my own.

Thank you for your consideration.

Kian Farahmand
Frontier Institute for Intelligent Systems (FIIS)
Department of Materials Science and Engineering, Shiraz University
kianfarahmand@thefiis.com
"""
open("cover_letter.md","w",encoding="utf-8").write(cl)
print("cover letter words:", len(cl.split()))
print("manuscript words:", len(open("perspective_NCS_submission.md",encoding="utf-8").read().split()))
print("double-period remaining in tex:", tex.count(".. "))


# ======================================================================================
# CELL 118  |  run 2026-10-06 10:00:45Z  |  env=python  |  exit=ok
# ======================================================================================
import os, re
fs = ["autonomous_discovery_review.md","perspective_NCS_submission.md","perspective_NCS_submission.tex","cover_letter.md"]
for f in fs:
    ok = os.path.exists(f)
    t = open(f, encoding="utf-8").read() if ok else ""
    print(f, "| exists:", ok, "| bytes:", len(t.encode()) if ok else 0)
tex = open("perspective_NCS_submission.tex", encoding="utf-8").read()
md = open("perspective_NCS_submission.md", encoding="utf-8").read()
print("tex figs", tex.count("begin{figure*}"), "| bibitems", tex.count("\\bibitem"), "| '.. ':", tex.count(".. "))
print("md refs:", len(re.findall(r"^\d+\. ", md, re.M)), "| body words:", len(md.split("## References")[0].split()))
print("affil present:", "Shiraz University" in tex and "thefiis.com" in tex)
assert all(os.path.exists(f) for f in fs)


# ======================================================================================
# CELL 119  |  run 2026-10-06 10:31:03Z  |  env=python  |  exit=ok
# ======================================================================================
import pandas as pd
sw = pd.read_csv("{{artifact:1e970f10-5128-4838-b71f-841219afff49}}")
sw["cy"] = sw.crossref_year.fillna(sw.year).astype(int)
KEY = ["10.1021/acs.chemrev.4c00055","10.1016/j.matt.2021.06.036","10.1038/s44160-022-00231-0",
       "10.1002/anie.201909987","10.1038/s41586-020-2442-2","10.1038/s41586-023-06734-w",
       "10.1038/s41586-023-06792-0","10.1126/science.adk9227","10.1038/s41467-024-45569-5",
       "10.1126/sciadv.aaz8867"]
m = sw.set_index("doi")
refs = []
for i, d in enumerate(KEY, 1):
    r = m.loc[d]
    jr = r.crossref_journal if pd.notna(r.crossref_journal) else r.venue
    refs.append(f"{i}. {str(r.crossref_authors).replace(';', ',')}. {r.title}. {jr} ({r.cy}). doi:{d}")

abstract = ("Autonomous scientific discovery is usually described through its hardware. Here we measure "
"its publication record instead. Across 1,923 screened works, each classified by the autonomy it "
"implements rather than the autonomy it discusses, only 18.9% close an experimental loop and 49.8% "
"report no physical experiment. Over half the field names no material class; those works close a "
"loop 3.1% of the time, against 38.6% for works that name one. Loop closure ranges from 21.1% in "
"biomolecules to 60.0% in quantum and photonic materials, tracking how quickly a result can be "
"measured rather than how automated the laboratory is: biology is the most automated domain and the "
"least autonomous. The field is not becoming less experimental, but its growth is increasingly in "
"work that neither names a material nor runs one. We argue that measurement latency, not robotics, "
"now limits autonomous discovery, and that the field's most urgent need is a standard way to report "
"platform performance.")
nw = len(abstract.split())

doc = f"""# Presubmission enquiry - Nature Computational Science

**Submit via:** the Manuscript Tracking System, choosing *presubmission enquiry* as the article type.
Do **not** attach the full manuscript. Paste each block below into the matching form field.

---

## Field: Title

Autonomous scientific discovery is becoming a methodology literature

## Field: Article type

Perspective

## Field: Abstract  ({nw} words)

{abstract}

## Field: Manuscript comments / cover note

Dear Editors,

I would like to ask whether a Perspective on the state of autonomous scientific discovery would be of
interest to Nature Computational Science.

The field has been surveyed several times by expert synthesis{chr(0x2009)}(refs 1–4), but never measured. This
Perspective does that. From 9,925 OpenAlex records I built a corpus of 1,923 works, screened every
record individually (precision 0.94 on a 100-record manual audit), and classified each work by the
highest level of autonomy it actually implements. That distinction matters: keyword counting over the
same corpus overstates closed-loop work by a factor of 2.5, because reviews of closed-loop discovery
carry all of its vocabulary.

The piece makes three claims: that only about a fifth of the field closes an experimental loop; that
the material-agnostic half of the literature (agents, frameworks, benchmarks) almost never does; and
that loop closure is limited by measurement latency rather than by robotics. It also reports, and
rules out, a tempting conclusion: the fast-growing agentic literature looks under-cited, but that
turns out to be entirely citation lag once publication year is controlled for.

The topic sits squarely at the journal's interface between computational method and physical
experiment, and every claim is a count over a documented, reproducible corpus.

**Proposed structure (about 2,800 words, 4 figures, 1 table, about 50 references)**

1. *Introduction.* The gap between describing autonomous discovery and demonstrating it, and why
   keyword measures cannot tell them apart.
2. *Scope and method.* Corpus construction, the screening rule, the measured precision, and the
   classification of implemented versus discussed autonomy.
3. *What the field has built.* The long lineage of laboratory automation set against the short
   lineage of autonomy; two growth regimes since 2023; and the institutions and platforms that hold
   demonstrated capability, including which groups bridge the hardware and agent communities.
4. *What the field has not built.* The material-agnostic split, and the domain ordering of loop
   closure, with biology as the case of a domain that is highly automated yet rarely autonomous.
5. *Robustness.* Corpus precision, stability of the clustering, and the citation-lag check that rules
   out the impact claim.
6. *Outlook.* Asynchronous and surrogate-readout architectures for slow-assay domains, and the case for
   standard performance reporting.

**Main references**

{chr(10).join(refs)}

A complete draft and all supporting data tables are ready and can be sent on request. The work has not
been published or submitted elsewhere. Large language model classification was used under explicit
written rules, validated by manual audit, and is disclosed in the manuscript.

With best regards,

Kian Farahmand
Frontier Institute for Intelligent Systems (FIIS)
Department of Materials Science and Engineering, Shiraz University
kianfarahmand@thefiis.com

---

## Before you submit

- **Author initials.** The reference authors above are surnames only, as returned by verification. Add
  initials before pasting (Nature style: *Tom, G. et al.*).
- **Abstract length.** This {nw}-word version is also the trimmed abstract for the manuscript; the
  manuscript currently carries a longer one. Use this one in both places.
- **Fallback.** If the editors decline, the same text goes to Matter with the journal name changed.
"""
open("presubmission_enquiry_NCS.md","w",encoding="utf-8").write(doc)
print("abstract words:", nw, "| refs:", len(refs), "| comments words:",
      len(doc.split("## Field: Manuscript comments")[1].split("---")[0].split()))
print(refs[4][:110]); print(refs[7][:110])


# ======================================================================================
# CELL 120  |  run 2026-10-06 10:31:48Z  |  env=python  |  exit=ok
# ======================================================================================
doc = open("presubmission_enquiry_NCS.md", encoding="utf-8").read()
doc = doc.replace("et al.. ", "et al. ").replace("\u2009(refs", " (refs")
open("presubmission_enquiry_NCS.md","w",encoding="utf-8").write(doc)
print("et al.. remaining:", doc.count("et al.."), "| thin-space:", "\u2009" in doc)


