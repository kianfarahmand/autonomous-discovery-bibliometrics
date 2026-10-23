"""
02_relevance_screening.py
Relevance screening (model-based) and the v1 deterministic phrase fallback

VERBATIM cell sources recovered from the execution log of frame
dab9690f-bbbb-4695-a3e4-9e476b9fd59e (project proj_593d8a44f5b4).
Cells appear in original run order. Nothing has been rewritten, reordered or tidied.
Cells: [16, 17, 18, 19, 23, 24, 25, 26, 68, 70, 71]
"""

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


