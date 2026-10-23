import pandas as pd, numpy as np, matplotlib
# Reproduces the figures and statistics of the manuscript from the files in ../data.
# Usage: python reproduce.py   (writes figures to ./figures)
import os, pandas as pd
DATA=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data')
os.makedirs('figures',exist_ok=True)
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
matplotlib.use('Agg')
import matplotlib.pyplot as plt, networkx as nx
from matplotlib.patches import Patch
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,
 'axes.titlesize':8,'axes.labelsize':8,'legend.fontsize':7,'xtick.labelsize':7,'ytick.labelsize':7,'hatch.linewidth':0.8})
S=''
d=pd.read_csv(S+'autonomous_discovery_corpus.csv'); d['year']=d.year.astype(int)
sc=pd.read_csv(S+'subfield_clusters.csv')
STAGES=['Prediction / review only','Algorithmic selection only','Automated execution','Closed loop']
STAGE_LBL=['Prediction or review only','Algorithmic selection only','Automated execution','Closed loop']
SC=['#c8c8c8','#7b3294','#e08214','#018571']
BLUE='#1f4e79'
def wil(k,n,z=1.959964):
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den; return c-h,c+h
def letter(ax,t,x=-0.12,y=1.04): ax.text(x,y,t,transform=ax.transAxes,fontsize=10,fontweight='bold',va='bottom')
def save(fig,name):
    fig.savefig(f'figures/{name}.png',dpi=300,bbox_inches='tight',facecolor='white')
    fig.savefig(f'figures/{name}.tif',dpi=300,bbox_inches='tight',facecolor='white',pil_kwargs={'compression':'tiff_lzw'})
    plt.close(fig)

# ---------- Figure 1
fig,axs=plt.subplots(2,2,figsize=(7.0,5.8)); fig.subplots_adjust(hspace=0.55,wspace=0.38)
ax=axs[0,0]; yrs=range(2015,2027)
grp=d.type.map({'article':'Articles and reviews','review':'Articles and reviews','preprint':'Preprints','conference-paper':'Conference papers and chapters','book-chapter':'Conference papers and chapters'})
t=pd.crosstab(d.year,grp).reindex(yrs).fillna(0)
cols={'Articles and reviews':BLUE,'Preprints':'#e08214','Conference papers and chapters':'#a6a6a6'}
bot=np.zeros(len(t))
for k,c in cols.items():
    v=t[k].values
    bars=ax.bar(t.index,v,bottom=bot,color=c,label=k,width=0.75,edgecolor='white',linewidth=0.3)
    bars[-1].set_hatch('///'); bot+=v
ax.set_xlabel('Publication year'); ax.set_ylabel('Works'); ax.legend(frameon=False,loc='upper left')
ax.set_xticks([2015,2017,2019,2021,2023,2025]); letter(ax,'a')
ax=axs[0,1]; f=pd.read_csv(S+'field_structure.csv'); f=f[f.n_works>=30]
ax.plot(f.year,f.facility_share*100,'-s',color='#018571',ms=4,label='National laboratory or government')
ax.plot(f.year,f.industry_share*100,'-o',color='#7b3294',ms=4,label='Industry')
ax.set_ylim(0,80); ax.set_xlim(2018.6,2026.4); ax.set_xlabel('Publication year'); ax.set_ylabel('Share of works with affiliation (%)')
ax.legend(frameon=False,loc='upper left'); ax.text(0.02,0.02,'Years with at least 30 works',transform=ax.transAxes,fontsize=6.5,color='0.35'); letter(ax,'b')
ax=axs[1,0]; top=['Materials Science','Engineering','Computer Science','Decision Sciences','Biochemistry, Genetics and Molecular Biology']
ff=d.field.where(d.field.isin(top),'Other or unassigned')
x=pd.crosstab(d.year,ff,normalize='index').loc[2018:2026][top+['Other or unassigned']]*100
pal=[BLUE,'#4a90c2','#9ecae1','#e08214','#8c6bb1','#d9d9d9']
ax.stackplot(x.index,x.T.values,colors=pal,labels=[l.replace('Biochemistry, Genetics and Molecular Biology','Biochemistry, genetics, mol. biology') for l in x.columns],lw=0)
ax.set_xlim(2018,2026); ax.set_ylim(0,100); ax.set_xlabel('Publication year'); ax.set_ylabel('Share of works (%)')
ax.legend(frameon=False,fontsize=6.3,ncol=2,loc='upper center',bbox_to_anchor=(0.5,-0.22)); letter(ax,'c')
ax=axs[1,1]; g=pd.read_csv(S+'geography_institutions.csv').head(12).iloc[::-1]
ax.hlines(range(len(g)),0,g.affiliations,color='0.8',lw=1); ax.plot(g.affiliations,range(len(g)),'o',color=BLUE,ms=4.5)
for i,v in enumerate(g.affiliations): ax.text(v+170,i,f'{v:,}',va='center',fontsize=6.5)
ax.set_yticks(range(len(g))); ax.set_yticklabels(g.country); ax.set_xlim(0,5600)
ax.set_xlabel('Author affiliations (count)'); letter(ax,'d')
save(fig,'Figure1')

# ---------- Figure 2: keyword versus implemented classification
m={'Prediction / simulation only':STAGES[0],'Algorithmic experiment selection':STAGES[1],'Automated execution':STAGES[2],'Closed loop':STAGES[3]}
d['stage_kw']=d.stage.map(m)
fig,axs=plt.subplots(1,2,figsize=(7.0,2.9),gridspec_kw={'width_ratios':[1.35,1]}); fig.subplots_adjust(wspace=0.75)
ax=axs[0]; ct=pd.crosstab(d.stage_kw,d.stage_llm).reindex(index=STAGES,columns=STAGES)
left=np.zeros(4)
for j,s in enumerate(STAGES):
    v=ct[s].values; ax.barh(range(4),v,left=left,color=SC[j],label=STAGE_LBL[j],edgecolor='white',linewidth=0.4)
    for i in range(4):
        if v[i]>=60: ax.text(left[i]+v[i]/2,i,str(v[i]),ha='center',va='center',fontsize=6.3,color='white' if j>0 else 'black')
    left+=v
for i,tot in enumerate(left): ax.text(tot+15,i,f'n = {int(tot)}',va='center',fontsize=6.5)
ax.set_yticks(range(4)); ax.set_yticklabels(STAGE_LBL); ax.set_xlim(0,1080)
ax.set_xlabel('Works'); ax.set_ylabel('Keyword (regular-expression) stage')
ax.legend(title='Model-assigned implemented stage',title_fontsize=6.8,frameon=False,ncol=2,loc='upper center',bbox_to_anchor=(0.4,-0.2)); letter(ax,'a',x=-0.5)
ax=axs[1]; cl=d.stage_llm=='Closed loop'
rows=[('High-precision phrase stratum',d.tier=='A'),('Recall-oriented stratum',d.tier=='B'),('Citation snowball',d.tier=='S'),
      ('Journal articles',d.type=='article'),('Preprints',d.type=='preprint'),('Conference papers',d.type=='conference-paper'),('Reviews and chapters',d.type.isin(['review','book-chapter']))]
for i,(lab,mask) in enumerate(rows):
    k=(cl&mask).sum(); n=mask.sum(); lo,hi=wil(k,n)
    y=len(rows)-1-i-(0.6 if i>=3 else 0)
    ax.errorbar(100*k/n,y,xerr=[[100*(k/n-lo)],[100*(hi-k/n)]],fmt='o',color=BLUE,ms=4,capsize=2,lw=0.8)
    ax.text(101,y,f'n = {n:,}',va='center',fontsize=6.5)
ys=[len(rows)-1-i-(0.6 if i>=3 else 0) for i in range(len(rows))]
ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows]); ax.set_xlim(0,100)
ax.axvline(100*cl.mean(),color='0.6',lw=0.7,ls=':'); ax.set_xlabel('Works implementing a closed loop (%)'); letter(ax,'b',x=-0.75)
save(fig,'Figure2')

# ---------- Figure 3: domain by stage and trend
fig,axs=plt.subplots(1,2,figsize=(7.0,3.3),gridspec_kw={'width_ratios':[1.4,1]}); fig.subplots_adjust(wspace=0.35)
ax=axs[0]; ds=pd.read_csv(S+'domain_stage_matrix.csv')
mat=ds[ds.dom_llm!='No material class named'].sort_values('closed_loop_share'); nm=ds[ds.dom_llm=='No material class named']
ds2=pd.concat([nm,mat])
for i,(_,r) in enumerate(ds2.iterrows()):
    y=i+(0.6 if i>0 else 0); left=0
    for j,s in enumerate(STAGES):
        w=100*r[s]/r.domain_total; ax.barh(y,w,left=left,color=SC[j],edgecolor='white',linewidth=0.4,label=STAGE_LBL[j] if i==0 else None); left+=w
    ax.text(101,y,f'n = {int(r.domain_total):,}',va='center',fontsize=6.3)
lbl=[s.replace('&','and') for s in ds2.dom_llm]
ax.set_yticks([i+(0.6 if i>0 else 0) for i in range(len(ds2))]); ax.set_yticklabels(lbl); ax.set_xlim(0,100)
ax.set_xlabel('Share of works in domain (%)'); ax.legend(frameon=False,ncol=2,loc='upper center',bbox_to_anchor=(0.45,-0.16)); letter(ax,'a',x=-0.45)
ax=axs[1]; yy=d.groupby('year').agg(n=('id','size'),cl=('stage_llm',lambda x:(x=='Closed loop').mean()),nm=('dom_llm',lambda x:(x=='No material class named').mean()))
named=d[d.dom_llm!='No material class named'].groupby('year').stage_llm.apply(lambda x:(x=='Closed loop').mean())
yy=yy[yy.n>=25]
ax.plot(yy.index,yy.nm*100,'-s',color='0.45',ms=3.5,label='Share naming no material class')
ax.plot(yy.index,named.loc[yy.index]*100,'-o',color='#018571',ms=3.5,label='Closed loop, works naming a material')
ax.plot(yy.index,yy.cl*100,'-^',color=BLUE,ms=3.5,label='Closed loop, all works')
ax.set_ylim(0,80); ax.set_xlabel('Publication year'); ax.set_ylabel('Share of works (%)')
ax.legend(frameon=False,loc='upper center',bbox_to_anchor=(0.5,-0.18),fontsize=6.5)
ax.text(0.02,0.97,'Years with at least 25 works;\n2026 partial',transform=ax.transAxes,fontsize=6.3,color='0.35',va='top'); letter(ax,'b')
save(fig,'Figure3')

# ---------- Figure 4: subfields
famcol={'Platforms & self-driving labs':BLUE,'Automated synthesis & reaction optimization':'#018571','Adaptive experimental design':'#7b3294',
'AI agents & AI scientists':'#e08214','Automation & lab robotics':'#80cdc1','Overviews & closed-loop frameworks':'#a6a6a6'}
fig=plt.figure(figsize=(7.0,7.4)); axs=[fig.add_axes([0.06,0.56,0.46,0.40]),fig.add_axes([0.42,0.06,0.50,0.40])]
ax=axs[0]
for fam,c in famcol.items():
    s=sc[sc.family==fam]; ax.scatter(s.tx,s.ty,s=4+np.sqrt(s.cites)*1.2,color=c,alpha=0.65,lw=0,label=fam.replace('&','and'))
ax.set_xticks([]); ax.set_yticks([]); ax.spines['left'].set_visible(False); ax.spines['bottom'].set_visible(False)
ax.set_xlabel('t-SNE dimension 1'); ax.set_ylabel('t-SNE dimension 2')
ax.legend(frameon=False,fontsize=6.8,markerscale=2.2,loc='center left',bbox_to_anchor=(1.03,0.5),ncol=1,title='Subfield family',title_fontsize=7); letter(ax,'a',x=-0.08)
ax=axs[1]; ss=pd.read_csv(S+'subfield_summary.csv').sort_values('share_2023on')
for i,(_,r) in enumerate(ss.iterrows()):
    ax.hlines(i,0,r.closed_rate*100,color='0.85',lw=1); ax.plot(r.closed_rate*100,i,'o',color=famcol[r.family],ms=4.5)
    ax.text(r.closed_rate*100+1.5,i,f'{r.share_2023on*100:.0f}% since 2023',va='center',fontsize=6,color='0.35')
ax.set_yticks(range(len(ss))); ax.set_yticklabels([s.replace('&','and') for s in ss.cluster_name]); ax.set_xlim(0,75)
ax.set_xlabel('Works implementing a closed loop (%)'); letter(ax,'b',x=-0.72)
save(fig,'Figure4')

# ---------- Figure 5: network and platforms
nodes=pd.read_csv('collaboration_network_nodes.csv'); edges=pd.read_csv('collaboration_network_edges.csv')
G=nx.Graph(); G.add_nodes_from(nodes.institution); G.add_weighted_edges_from(edges.values)
G=G.subgraph(max(nx.connected_components(G),key=len)).copy(); nodes=nodes[nodes.institution.isin(G.nodes)]
pos=nx.kamada_kawai_layout(G)
fig,axs=plt.subplots(1,2,figsize=(7.0,3.8),gridspec_kw={'width_ratios':[1.1,1]}); fig.subplots_adjust(wspace=0.55)
ax=axs[0]; nx.draw_networkx_edges(G,pos,ax=ax,width=0.3,edge_color='0.75',alpha=0.8)
col=[famcol.get(f,'0.6') for f in nodes.dominant_family]
nx.draw_networkx_nodes(G,pos,nodelist=list(nodes.institution),node_size=nodes.n_works*2.2,node_color=col,ax=ax,linewidths=0.3,edgecolors='white')
short={'Lawrence Berkeley National Laboratory':'Berkeley Lab','University of Toronto':'Toronto','Stanford University':'Stanford','Massachusetts Institute of Technology':'MIT',
'University of Science and Technology of China':'USTC','University of Washington':'U Washington'}
offs={'Lawrence Berkeley National Laboratory':(14,-14),'University of Toronto':(-40,12),'Stanford University':(10,10),'Massachusetts Institute of Technology':(-30,-14),'University of Science and Technology of China':(8,6),'University of Washington':(8,-10)}
for k,v in short.items():
    x,y=pos[k]; ax.annotate(v,(x,y),xytext=offs[k],arrowprops=dict(arrowstyle='-',lw=0.5,color='0.3'),textcoords='offset points',fontsize=6.5,bbox=dict(boxstyle='round,pad=0.15',fc='white',ec='none',alpha=0.8))
ax.set_axis_off(); letter(ax,'a',x=0.0)
ax.legend(handles=[Patch(color=c,label=f.replace('&','and')) for f,c in famcol.items()],frameon=False,fontsize=6,loc='upper center',bbox_to_anchor=(0.5,0.0),ncol=1)
ax=axs[1]; p=pd.read_csv(S+'lab_platform_table.csv').sort_values('total_cites')
ax.hlines(range(len(p)),0,p.total_cites,color='0.85',lw=1); ax.plot(p.total_cites,range(len(p)),'o',color=BLUE,ms=4)
for i,(_,r) in enumerate(p.iterrows()): ax.text(r.total_cites+40,i,str(int(r.first_year)),va='center',fontsize=6.3,color='0.35')
ax.set_yticks(range(len(p))); ax.set_yticklabels(p.platform.str.replace('/',' and ')); ax.set_xlim(0,2150)
ax.set_xlabel('Citations to works naming the platform\n(first year of appearance at right)'); letter(ax,'b',x=-0.6)
save(fig,'Figure5')
print('done')
