"""
09_manuscript_tables_and_session_admin.py
Remaining executed cells: manuscript/LaTeX assembly, DOI checks, skill authoring, session admin

VERBATIM cell sources recovered from the execution log of frame
dab9690f-bbbb-4695-a3e4-9e476b9fd59e (project proj_593d8a44f5b4).
Cells appear in original run order. Nothing has been rewritten, reordered or tidied.
Cells: [0, 1, 2, 22, 42, 54, 55, 59, 60, 61, 62, 63, 65, 66, 67, 89, 90, 97, 98, 99, 100, 109, 112, 114, 115, 116, 117, 118, 119, 120]
"""

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
# CELL 022  |  run 2026-10-05 12:59:34Z  |  env=_operon  |  exit=ok
# ======================================================================================
help(host.delegate)
print("AGENTS:", [a.get("name") for a in (host.agents.list() or []) if isinstance(a, dict)][:20])


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


