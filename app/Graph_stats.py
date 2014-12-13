'''
Script to create Graph Statistics 
Statistics are dumped to disk for app ease


__author__ = Ryan Stephany
__purpose__ Georgetown Data Analytics

'''

import os
import pickle
import networkx as nx 
import community
import matplotlib.pyplot as plt
from operator import itemgetter

MODELS_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))),'models')
with open(os.path.join(MODELS_PATH,'hidden_names.pkl'),'rb') as handler:
	HIDDEN = pickle.load(handler)

NICKNAMES = [v[1] for v in HIDDEN['HIDDEN'].values()]

# Taken from Benjamin Bengfort and modified
def nbest_centrality(graph, metric, n=10, attribute="centrality", **kwargs):
    centrality = metric(graph, **kwargs)
    nx.set_node_attributes(graph, attribute, centrality)
    degrees = sorted(centrality.items(), key=itemgetter(1), reverse=True)
    
    output = []
    for idx, item in enumerate(degrees[0:n]):
    	item = list(item)
    	if graph.has_node(item[0]):
    		node = graph.node[item[0]]
    		try:
	       		item[0] = node['screen_name']
    		except:
    			pass
    		item = tuple(item)
        item = (idx+1,) + item
        print "%i. %s: %0.4f" % item
        output.append(item)
    
    return output

def gen_graph_stats (graph):
	G = nx.read_graphml(graph)
	stats = {}

	edges, nodes = 0,0
	for e in G.edges_iter(): edges += 1
	for n in G.nodes_iter(): nodes += 1
	stats['Edges'] = (edges,'The number of edges within the Graph')
	stats['Nodes'] = (nodes, 'The number of nodes within the Graph')
	print "%i edges, %i nodes" % (edges, nodes)


	# Accessing the highest degree node
	center, degree = sorted(G.degree().items(), key=itemgetter(1), reverse=True)[0]
	stats['Center Node'] = ('%s: %0.5f' % (center,degree),'The center most node in the graph. Which has the highest degree')


	hairball = nx.subgraph(G, [x for x in nx.connected_components(G)][0])
	print "Average shortest path: %0.4f" % nx.average_shortest_path_length(hairball)
	stats['Average Shortest Path Length'] = (nx.average_shortest_path_length(hairball), '')
	# print "Center: %s" % G[center]

	# print "Shortest Path to Center: %s" % p


	print "Degree: %0.5f" % degree
	stats['Degree'] = (degree,'The node degree is the number of edges adjacent to that node.')

	print "Order: %i" % G.number_of_nodes()
	stats['Order'] = (G.number_of_nodes(),'The number of nodes in the graph.')

	print "Size: %i" % G.number_of_edges()
	stats['Size'] = (G.number_of_edges(),'The number of edges in the graph.')

	print "Clustering: %0.5f" % nx.average_clustering(G)
	stats['Average Clustering'] = (nx.average_clustering(G),'The average clustering coefficient for the graph.')

	print "Transitivity: %0.5f" % nx.transitivity(G)
	stats['Transitivity'] = (nx.transitivity(G),'The fraction of all possible triangles present in the graph.')

	part = community.best_partition(G)
	# values = [part.get(node) for node in G.nodes()]

	# nx.draw_spring(G, cmap = plt.get_cmap('jet'), node_color = values, node_size=30, with_labels=False)
	# plt.show()

	mod = community.modularity(part,G)
	print "modularity: %0.5f" % mod
	stats['Modularity'] = (mod,'The modularity of a partition of a graph.')

	knn = nx.k_nearest_neighbors(G)
	print knn
	stats['K Nearest Neighbors'] = (knn,'the average degree connectivity of graph.\nThe average degree connectivity is the average nearest neighbor degree of nodes with degree k. For weighted graphs, an analogous measure can be computed using the weighted average neighbors degre')


	return G, stats



if __name__ == '__main__':
	graphs = {}
	for nn in NICKNAMES:
		G, g_stats = gen_graph_stats(os.path.join(MODELS_PATH,'%s.graphml' % nn))
		graphs[nn] = {}
		graphs[nn]['stats'] = g_stats

		dc = nbest_centrality(G, nx.degree_centrality, n=15)
		graphs[nn]['degree_centrality'] = dc

		bc = nbest_centrality(G, nx.betweenness_centrality, n=15)
		graphs[nn]['betweenness_centrality'] = bc

		cc = nbest_centrality(G, nx.closeness_centrality, n=15)
		graphs[nn]['closeness_centrality'] = cc

		ec = nbest_centrality(G, nx.eigenvector_centrality_numpy, n=15)
		graphs[nn]['eigenvector_centrality'] = ec


	G, g_stats = gen_graph_stats(os.path.join(MODELS_PATH,'all.graphml'))
	graphs['all'] = {}
	graphs['all']['stats'] = g_stats



	dc = nbest_centrality(G, nx.degree_centrality, n=15)
	graphs['all']['degree_centrality'] = dc

	bc = nbest_centrality(G, nx.betweenness_centrality, n=15)
	graphs['all']['betweenness_centrality'] = bc

	cc = nbest_centrality(G, nx.closeness_centrality, n=15)
	graphs['all']['closeness_centrality'] = cc

	ec = nbest_centrality(G, nx.eigenvector_centrality_numpy, n=15)
	graphs['all']['eigenvector_centrality'] = ec

	kc = nbest_centrality(G, nx.katz_centrality_numpy,n=15)
	graphs['all']['katz_centrality'] = kc

	partition = community.best_partition(G)
	size = float(len(set(partition.values())))

	count = 0
	for com in set(partition.values()):
		count+=1
	graphs['all']['Communities'] = count

	with open(os.path.join(MODELS_PATH,'graph_measures.pkl'),'wb') as handler:
		pickle.dump(graphs,handler)

