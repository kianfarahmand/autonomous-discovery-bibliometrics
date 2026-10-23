"""
06_analysis_clustering_network_stats.py
TF-IDF + k-means, k sweep, silhouette, ARI, t-SNE, institution network, Spearman / Mann-Whitney

VERBATIM cell sources recovered from the execution log of frame
dab9690f-bbbb-4695-a3e4-9e476b9fd59e (project proj_593d8a44f5b4).
Cells appear in original run order. Nothing has been rewritten, reordered or tidied.
Cells: [39, 40, 41, 43, 46, 47, 50, 51, 75, 76, 78, 79, 102, 103, 104, 105, 111]
"""

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


