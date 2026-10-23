"""
04_regex_stage_classification.py
Regular-expression stage classification -> 'stage' column (the 919)

VERBATIM cell sources recovered from the execution log of frame
dab9690f-bbbb-4695-a3e4-9e476b9fd59e (project proj_593d8a44f5b4).
Cells appear in original run order. Nothing has been rewritten, reordered or tidied.
Cells: [49, 77]
"""

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


