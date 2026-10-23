import pandas as pd, numpy as np
# Reproduces the figures and statistics of the manuscript from the files in ../data.
# Usage: python reproduce.py   (writes figures to ./figures)
import os, pandas as pd
DATA=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data')
REN={'stage_keyword':'stage','stage_implemented':'stage_llm','material_domain':'dom_llm','cluster_id':'cl','tsne_x':'tx','tsne_y':'ty','openalex_field':'field','retrieval_stratum':'tier'}
FILES={'autonomous_discovery_corpus.csv':'corpus_screened_classified.csv','subfield_clusters.csv':'corpus_screened_classified.csv','field_structure.csv':'annual_structure.csv',
'geography_institutions.csv':'affiliations_by_country.csv','domain_stage_matrix.csv':'domain_by_stage.csv','subfield_summary.csv':'subfield_summary.csv','lab_platform_table.csv':'named_platforms.csv'}
_read=pd.read_csv
def read_csv(path,*a,**k):
    base=os.path.basename(path)
    if base in FILES or base.startswith('collaboration_network'):
        df=_read(os.path.join(DATA,FILES.get(base,base)),*a,**k).rename(columns=REN)
        if 'tier' in df: df['tier']=df.tier.map({'high_precision':'A','recall_oriented':'B','citation_snowball':'S'})
        return df
    return _read(path,*a,**k)
pd.read_csv=read_csv
from scipy import stats
def pc(k,n,method='wilson',z=1.959964):
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den; return c-h,c+h
d=pd.read_csv('autonomous_discovery_corpus.csv'); d['year']=d.year.astype(int)
m={'Prediction / simulation only':'Prediction / review only','Algorithmic experiment selection':'Algorithmic selection only','Automated execution':'Automated execution','Closed loop':'Closed loop'}
r=d.stage.map(m); s=d.stage_llm
from sklearn.metrics import cohen_kappa_score
print('kappa4',round(cohen_kappa_score(r,s),3),'agree',round((r==s).mean(),3))
print('kappa CL',round(cohen_kappa_score(r=='Closed loop',s=='Closed loop'),3))
cl=s=='Closed loop'; nm=d.dom_llm=='No material class named'
for name,mask in [('nomat',nm),('mat',~nm),('all',cl==cl)]:
    k=(cl&mask).sum(); n=mask.sum(); lo,hi=pc(k,n,method='wilson'); print(name,k,n,round(k/n*100,1),round(lo*100,1),round(hi*100,1))
ct=pd.crosstab(d.dom_llm,cl); print(ct)
mat=ct.drop('No material class named'); chi=stats.chi2_contingency(mat); print('chi2 domains (material only)',round(chi[0],1),chi[2],chi[1])
for dom,row in mat.iterrows():
    k=row[True]; n=row.sum(); lo,hi=pc(k,n,method='wilson'); print(dom,k,n,round(100*k/n,1),round(lo*100,1),round(hi*100,1))
print(stats.chi2_contingency(pd.crosstab(nm,cl))[:2])
S=pd.read_csv('subfield_summary.csv')
print(stats.spearmanr(S.share_2023on,S.nomat_rate), stats.spearmanr(S.share_2023on,S.closed_rate), stats.spearmanr(S.share_2023on,S.med_cites))
y=d.groupby('year').agg(n=('id','size'),cl=('stage_llm',lambda x:(x=='Closed loop').mean()),nm=('dom_llm',lambda x:(x=='No material class named').mean()))
yy=y[y.n>=25]; print(yy.round(3)); print('trend cl',stats.spearmanr(yy.index,yy.cl),'trend nm',stats.spearmanr(yy.index,yy.nm))
# closed-loop among material-naming works by year
dm=d[~nm]; print(dm.groupby('year').stage_llm.apply(lambda x:(x=='Closed loop').mean()).loc[2018:].round(3), dm.groupby('year').size().loc[2018:])
print(pd.crosstab(d.tier,cl,margins=True)); print(pd.crosstab(d.type,cl,margins=True))
# regex-only composition
ro=(r=='Closed loop')&~cl; print(ro.sum(), s[ro].value_counts())
print('regex precision', round(((r=='Closed loop')&cl).sum()/(r=='Closed loop').sum(),3),'recall',round(((r=='Closed loop')&cl).sum()/cl.sum(),3))
# 2023-24 cohort citations
c=d[d.year.isin([2023,2024])].merge(pd.read_csv('subfield_clusters.csv')[['id','family','cluster_name']],on='id',suffixes=('','_c'))
agent=['LLM agents for chemistry','Agentic research systems','AI scientists','Closed-loop frameworks & orchestration','Self-driving lab perspectives']
ag=c.cluster_name_c.isin(agent)
print('2023-24 cohort, agent/framework clusters n=',ag.sum(),'median',c.cites[ag].median(),'vs',c.cites[~ag].median(),
      'one-sided Mann-Whitney (less) p=',round(stats.mannwhitneyu(c.cites[ag],c.cites[~ag],alternative='less').pvalue,3))
print(c.groupby('cluster_name_c').cites.median().sort_values().tail(3))
print('years',d.year.min(),d.year.max(), (d.year<2015).sum())
print('2026 preprint',(d[d.year==2026].type=='preprint').mean(),(d[d.year==2025].type=='preprint').mean(),(d[d.year==2022].type=='preprint').mean(),(d[d.year==2023].type=='preprint').mean())
print(d.year.value_counts().sort_index().loc[2015:])
bio=d[d.dom_llm=='Biomolecules & proteins'].stage_llm.value_counts(); print(bio)
