"""
05_precision_audit.py
Precision audit sampling and v1 label scoring

VERBATIM cell sources recovered from the execution log of frame
dab9690f-bbbb-4695-a3e4-9e476b9fd59e (project proj_593d8a44f5b4).
Cells appear in original run order. Nothing has been rewritten, reordered or tidied.
Cells: [19, 24, 74]
"""

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
# CELL 074  |  run 2026-10-05 17:07:05Z  |  env=python  |  exit=ok
# ======================================================================================
rng = np.random.default_rng(7)
samp2 = c2.sort_values("id").sample(100, random_state=7).reset_index(drop=True)
for i, r in samp2.iterrows():
    print(f'{i+1:>3}|{int(r.year)}|{str(r.field)[:16]:<16}|{str(r.title)[:92]}')


