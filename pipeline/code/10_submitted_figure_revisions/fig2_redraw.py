"""Redraw of Fig. 2 for submission: same data and colours as the session figure, with the
overlapping legend, labels and truncated subfield name fixed.

Usage: python fig2_redraw.py data Fig2.png
"""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
D=sys.argv[1]  # folder containing subfield_clusters.csv and subfield_summary.csv (data/)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.linewidth':0.8})
c=pd.read_csv(f'{D}/subfield_clusters.csv'); s=pd.read_csv(f'{D}/subfield_summary.csv')
pal={'Platforms & self-driving labs':'#1F4E79',
     'Automated synthesis & reaction optimization':'#00876C',
     'Adaptive experimental design':'#7B3294',
     'AI agents & AI scientists':'#E08214',
     'Automation & lab robotics':'#56B4A4',
     'Overviews & closed-loop frameworks':'#9A9A9A'}
fig=plt.figure(figsize=(7.2,4.9),dpi=300)
ax=fig.add_axes([0.03,0.22,0.36,0.64]); bx=fig.add_axes([0.665,0.12,0.31,0.74])
for fam,col in pal.items():
    g=c[c.family==fam]
    ax.scatter(g.tx,g.ty,s=2+np.sqrt(g.cites)*1.6,c=[col],alpha=0.6,lw=0.2,edgecolors='white',label=fam)
ax.set_xticks([]);ax.set_yticks([])
for sp in ax.spines.values(): sp.set_visible(False)
fig.text(0.035,0.985,'Six families separate in the\nabstract-text embedding',fontsize=9,va='top')
fig.text(0.008,0.985,'a',fontsize=11,fontweight='bold',va='top')
lg=ax.legend(loc='upper left',bbox_to_anchor=(-0.02,-0.02),frameon=False,fontsize=6.5,ncol=1,markerscale=1.6,handletextpad=0.3,labelspacing=0.35)
for h in lg.legend_handles: h.set_sizes([18]); h.set_alpha(0.8)
ax.annotate('',xy=(0.12,-0.0),xytext=(0.0,-0.0),xycoords='axes fraction',arrowprops=dict(arrowstyle='->',color='0.4',lw=0.7))
ax.text(0.14,-0.0,'t-SNE 1',transform=ax.transAxes,fontsize=6,color='0.4',va='center')
ax.annotate('',xy=(0.0,0.12),xytext=(0.0,0.0),xycoords='axes fraction',arrowprops=dict(arrowstyle='->',color='0.4',lw=0.7))
ax.text(0.0,0.14,'t-SNE 2',transform=ax.transAxes,fontsize=6,color='0.4')
ax.text(1.0,-0.0,'marker area ∝ citations',transform=ax.transAxes,fontsize=6,color='0.4',ha='right',va='center')
s=s.sort_values('share_2023on',ascending=True).reset_index(drop=True)
y=np.arange(len(s))
bx.hlines(y,0,s.closed_rate*100,color='0.8',lw=1)
bx.scatter(s.closed_rate*100,y,c=[pal[f] for f in s.family],s=28,zorder=3)
for i,r in s.iterrows():
    bx.text(r.closed_rate*100+1.8,i,f'{r.share_2023on*100:.0f}% new',va='center',fontsize=6.5,color='0.35')
bx.set_yticks(y); bx.set_yticklabels(s.cluster_name,fontsize=7)
bx.set_xlim(0,70); bx.set_ylim(-0.6,len(s)-0.4)
bx.spines[['top','right']].set_visible(False)
bx.set_xlabel('Works implementing a closed loop (%)\nsubfields ordered by share published since 2023',fontsize=7.5)
bx.tick_params(labelsize=7)
fig.text(0.445,0.985,'Newer subfields implement closed loops less often\n(Spearman ρ = −0.52, p = 0.048)',fontsize=9,va='top')
fig.text(0.42,0.985,'b',fontsize=11,fontweight='bold',va='top')
fig.savefig(sys.argv[2],dpi=300,facecolor='white')
