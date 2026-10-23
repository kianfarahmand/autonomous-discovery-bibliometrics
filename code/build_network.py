import os
DATA=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data')
import pandas as pd, itertools, networkx as nx, collections, sys
d=pd.read_csv(os.path.join(DATA,'corpus_screened_classified.csv'))
inst=d.institutions.fillna('').apply(lambda s:sorted({x.strip() for x in s.split(';') if x.strip()}))
cnt=collections.Counter(i for l in inst for i in l)
keep={k for k,v in cnt.items() if v>=8}
E=collections.Counter()
for l in inst:
    for a,b in itertools.combinations([x for x in l if x in keep],2): E[(a,b)]+=1
G=nx.Graph(); G.add_nodes_from(keep)
for (a,b),w in E.items():
    if w>=2: G.add_edge(a,b,weight=w)
bc=nx.betweenness_centrality(G)
fam=d.assign(inst=inst).explode('inst').groupby('inst').family.agg(lambda s:s.value_counts().index[0])
nodes=pd.DataFrame({'institution':list(keep)})
nodes['n_works']=nodes.institution.map(cnt); nodes['degree']=nodes.institution.map(dict(G.degree()))
nodes['betweenness']=nodes.institution.map(bc).round(4); nodes['dominant_family']=nodes.institution.map(fam)
nodes=nodes.sort_values('n_works',ascending=False)
nodes.to_csv(os.path.join(DATA,'collaboration_network_nodes.csv'),index=False)
pd.DataFrame([(a,b,w['weight']) for a,b,w in G.edges(data=True)],columns=['source','target','co_authored_works']).to_csv(os.path.join(DATA,'collaboration_network_edges.csv'),index=False)
print(G.number_of_nodes(),G.number_of_edges(), nx.number_connected_components(G), len(max(nx.connected_components(G),key=len)))
print(nodes.sort_values('betweenness',ascending=False).head(8).to_string())
print(nodes.head(8).to_string())
