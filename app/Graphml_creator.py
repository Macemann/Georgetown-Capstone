'''
This is a script to create the users graphml files and json graphs

__author__ : Ryan Stephany
__purpose__: Georgetown Analytics
'''

import os
import pickle
from pymongo import MongoClient
import networkx as nx
import community
import d3py
import json
import matplotlib.pyplot as plt
from faker import Faker
from datetime import datetime
from operator import itemgetter
from networkx.readwrite import json_graph

MODELS_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))),'models')
STATIC_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))),'static')
with open(os.path.join(MODELS_PATH,'hidden_names.pkl'),'rb') as handler:
	HIDDEN = pickle.load(handler)	


def _removeAt (screen_name):
	'''
	Remove the @ symbol from a screen_name
	'''
	return screen_name.replace('@','')


def _get_mongo_user_id (db, user_name):
	'''
	Returns the mongodb "_id" from a given screen_name
	'''
	user_name = _removeAt(user_name)
	user = get_user_by_user_name(db, user_name)
	if user:
		return user['_id']

def _simple_query (db, collection, key, value):
	query = {key:value}
	for item in db[collection].find(query):
		yield item

def _simple_query_one(db, collection, key, value):
	query = {key:value}
	return db[collection].find_one(query)


def get_user_by_twitter_id (db, twitter_id, one=False):
	for item in _simple_query(db,'users_collection', 'id', twitter_id):
		yield item


def get_user_by_user_name(db, user_name):
	user_name = _removeAt(user_name)
	return _simple_query_one(db, 'users_collection', 'screen_name', user_name)


def get_users_followers (db, user_name):
	user_id = _get_mongo_user_id(db, user_name)
	if user_id:
		for follower in _simple_query(db,'friendships_collection','user_id', user_id):
			yield _simple_query_one(db,'users_collection', '_id', follower['follower_id'])

def get_users_friendships(db,user_name):
	user_id = _get_mongo_user_id(db, user_name)
	if user_id:
		for friend in _simple_query(db,'friendships_collection','follower_id', user_id):
			yield _simple_query_one(db,'users_collection', '_id', friend['user_id'])


def add_node_tw (n, screen_name='', weight=None, color=None, size=5):
	if not G.has_node(n):
		G.add_node(n)
		G.node[n]['weight']=1
		G.node[n]['screen_name'] = screen_name
		G.node[n]['node_color']=color
		G.node[n]['size'] = size
	else:
		G.node[n]['weight']+=1

	# G.node[n]['screen_name'] = screen_name
	# G.node[n]['node_color']=color

def add_edge_tw (n1,n2, weight=None):
	if not G.has_edge(n1, n2):
		G.add_edge(n1,n2)
		G[n1][n2]['weight'] = 1
	else:
		G[n1][n2]['weight']+=1



if __name__ == '__main__':
	conn = MongoClient()
	db = conn.GtownTwitter_PROD
	f = Faker()
	shortest_paths = {}

	known_names = [k for k in HIDDEN['HIDDEN'].keys()]

	shortest_paths['names'] = {}

	for name,fakenames in HIDDEN['HIDDEN'].iteritems():
		primary_labels = {}
		n=0
		# print name, fakenames
		sp = shortest_paths['names'][fakenames[-1]] = str('mer')

		mdb_user = get_user_by_user_name(db, name)
		uid = str(mdb_user['_id'])
		# sp = shortest_paths['names'][fakenames[-1]] = uid

		# Create the graph and give it some properties
		G = nx.erdos_renyi_graph(30, 0.05)
		# G = nx.DiGraph()

		# Add the main user node
		add_node_tw(fakenames[-1], fakenames[-1], color='#d62728',size=20)
		# primary_labels[uid] = fakenames[0]
		id_user_map = {}

		prev_friends = set([])
		secondary_labels = {}
		for user in get_users_friendships(db,name):
			fid = str(user['_id'])
			if fid not in prev_friends:
				if user['screen_name'] in [x[1:] for x in known_names]:
					friend_fakenames = HIDDEN['HIDDEN']['@%s' % user['screen_name']]
					screen_name = friend_fakenames[-1]
					secondary_labels[fid] = friend_fakenames[0]
					print '%s: found a common friend: %s' % (fakenames[-1], screen_name)
					color = '#1f77b4'
					size = 10
				else:
					if fid in id_user_map.keys():
						screen_name = id_user_map[fid]
					else:
						screen_name = f.username()
						id_user_map[fid] = screen_name
					color ='#dbdb8d'
					size = 5
				
				add_node_tw(screen_name,screen_name=screen_name, color=color, size=size)
				add_edge_tw(fakenames[-1], screen_name)
				prev_friends.add(fid)

		prev_followers = set([])
		for user in get_users_followers(db,name):
			fid = str(user['_id'])
			if fid not in prev_followers:
				if user['screen_name'] in [x[1:] for x in known_names]:
					follower_fakenames = HIDDEN['HIDDEN']['@%s' % user['screen_name']] 
					screen_name = follower_fakenames[-1]
					secondary_labels[fid] = follower_fakenames[0]
					print '%s: found a common friend: %s' % (fakenames[-1], screen_name)
					color = '#1f77b4'
					size = 10
				else:
					if fid in id_user_map.keys():
						screen_name = id_user_map[fid]
					else:
						screen_name = f.username()
						id_user_map[fid] = screen_name
					color ='#dbdb8d'
					size = 5
				
				# add_node_tw(uid,screen_name=screen_name, color=color)
				add_node_tw(screen_name,screen_name=screen_name, color=color, size=size)
				add_edge_tw(fakenames[-1], screen_name)
				prev_followers.add(fid)

		# partition = community.best_partition(G)
		# size = float(len(set(partition.values())))

		pos=nx.spring_layout(G)
		# count = 0
		# for com in set(partition.values()):
		# 	count += 1
		# 	list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == com]
			# nx.subsubgraph(list_nodes)
			# fn = os.path.join(in_dir)
			# send_subgraph(g, fn)
			# raw_input()
			# nx.draw_networkx_nodes(G,pos, list_nodes, node_size = 20)

		# node_color=[float(G.degree(v)) for v in G]
		# nx.draw_networkx_edges(G,pos,alpha=0.5)

		# nx.draw_networkx_labels(G,pos,secondary_labels,font_size=16,font_color='g')
		# nx.draw_networkx_labels(G,pos,primary_labels,font_size=25,font_color='r')
		# nx.draw(G, pos=pos, with_labels=False, node_color=node_color)
		# plt.show()


		nx.write_graphml(G,os.path.join(MODELS_PATH,'%s.graphml' % fakenames[-1]))

		d = json_graph.node_link_data(G)

		with open(os.path.join(STATIC_PATH,'%s_graph.json' % fakenames[-1]),'wb') as handler:
			json.dump(d,handler)



