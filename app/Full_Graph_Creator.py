'''
This is a script that creates the output graphml or json
for the full graph

__author__ : Ryan Stephany
__purpose__: Georgetown Analytics
'''


import networkx as nx
from networkx.readwrite import json_graph
import community
from pymongo import MongoClient
from faker import Faker
import matplotlib.pyplot as plt
import pickle
import json
import random
import os

MODELS_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))),'models')
STATIC_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))),'static')

with open(os.path.join(MODELS_PATH,'hidden_names.pkl'),'rb') as handler:
	HIDDEN = pickle.load(handler)

NAME_MAP = {}
WATCHING_MAP = {}
F = Faker()

CONN = MongoClient()
DB = CONN['GtownTwitter_PROD']
USERS_COLL = DB['users_collection']
FRIENDSHIPS_COLL = DB['friendships_collection']

def add_node_tw (n, screen_name='', weight=None, color=None, size=5):
	if not G.has_node(n):
		G.add_node(n)
		G.node[n]['weight']=1
		G.node[n]['screen_name'] = screen_name
		G.node[n]['node_color']=color
		G.node[n]['size'] = size
	else:
		G.node[n]['weight']+=1


def add_edge_tw (n1,n2, weight=None):
	if not G.has_edge(n1, n2):
		G.add_edge(n1,n2)
		G[n1][n2]['weight'] = 1
	else:
		G[n1][n2]['weight']+=1


if __name__ == '__main__':
	# Add our defined users fake name to the name dictionary
	for k,v in HIDDEN['HIDDEN'].iteritems():
		# print USERS_COLL.find_one({'screen_name':k[1:]})['_id']
		# print v[1]
		# raw_input('wait')
		WATCHING_MAP[USERS_COLL.find_one({'screen_name':k[1:]})['_id']] = v[1]


	G = nx.erdos_renyi_graph(30, 0.05)	

	for friendship in FRIENDSHIPS_COLL.find():
		# to_size = 0
		# from_size = 0

		if friendship['user_id'] in WATCHING_MAP.keys():
			from_name = WATCHING_MAP[friendship['user_id']]
			from_color = '#1f77b4'
			from_size = 10

		elif friendship['user_id'] in NAME_MAP.keys():
			from_name = NAME_MAP[friendship['user_id']]
			from_color ='#dbdb8d'
			from_size = 5

		else:
			from_name = F.username()
			NAME_MAP[friendship['user_id']] = from_name
			from_color ='#dbdb8d'
			from_size = 5

		if friendship['follower_id'] in WATCHING_MAP.keys():
			to_name = WATCHING_MAP[friendship['follower_id']]
			to_color = '#1f77b4'
			to_size = 10

		elif friendship['follower_id'] in NAME_MAP.keys():
			to_name = NAME_MAP[friendship['follower_id']]
			to_color ='#dbdb8d'
			to_size = 5
		else:
			to_name = F.username()
			NAME_MAP[friendship['follower_id']] = to_name
			to_color ='#dbdb8d'
			to_size = 5

		# print to_name, from_name
		# print to_size, from_size
		# raw_input()



		add_node_tw(str(friendship['user_id']),screen_name=from_name, color=from_color, size=from_size)
		add_node_tw(str(friendship['follower_id']), screen_name=to_name, color=to_color, size=to_size)
		add_edge_tw(str(friendship['user_id']),str(friendship['follower_id']))

	partition = community.best_partition(G)
	size = float(len(set(partition.values())))

	count = 0
	for com in set(partition.values()):
		color = '#%06X' % random.randint(0,256**3-1)
		list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == com]
		for node in list_nodes:
			if G.node[node].has_key('node_color'):
				if G.node[node]['node_color'] != '#1f77b4':
					G.node[node]['node_color'] = color
			else:
				if G.node[node].has_key('screen_name'):
					if G.node[node]['screen_name'] not in WATCHING_MAP.values():
						G.node[node]['node_color'] = color
				else:
					G.node[node]['node_color'] = color
		count += 1

	pos=nx.spring_layout(G)

	plt.show()

	nx.write_graphml(G,os.path.join(MODELS_PATH,'all.graphml'))

	d = json_graph.node_link_data(G)

	with open(os.path.join(STATIC_PATH,'all_graph.json'),'wb') as handler:
		json.dump(d,handler)








