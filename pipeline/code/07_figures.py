"""
07_figures.py
All four figures

VERBATIM cell sources recovered from the execution log of frame
dab9690f-bbbb-4695-a3e4-9e476b9fd59e (project proj_593d8a44f5b4).
Cells appear in original run order. Nothing has been rewritten, reordered or tidied.
Cells: [36, 37, 38, 44, 45, 48, 52, 53, 80, 81, 82, 83, 84, 85, 86, 106, 107]
"""

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


