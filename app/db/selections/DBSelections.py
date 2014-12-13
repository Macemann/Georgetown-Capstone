

def _removeAt (screen_name):
	return screen_name.replace('@','')

def _get_mongo_user_id (db, user_name):
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
			yield follower['_id'], _simple_query_one(db,'users_collection', '_id', follower['follower_id'])


def add_node_tw (n, screen_name, weight=None, time=None, source=None, location=None):
	if not g.has_node(n):
		g.add_node(n)
		g.node[n]['weight']=1
		g.node[n]['screen_name'] = screen_name
	else:
		g.node[n]['weight']+=1

def add_edge_tw (n1,n2, weight=None):
	if not g.has_edge(n1, n2):
		g.add_edge(n1,n2)
		g[n1][n2]['weight'] = 1
	else:
		g[n1][n2]['weight']+=1


if __name__ == '__main__':
	from pymongo import MongoClient
	import networkx as nx
	import community
	import d3py
	import matplotlib.pyplot as plt
	conn = MongoClient()
	db = conn.GtownTwitter_PROD

	for user_name in ('@FarisBritani','@4bu_Muhaj1r','@AbuHussain104','@onthatpath3','@jab2victory','@AbooJihad2013','@julaybeeeeb','@AbuTalha001','@AbuDujanah','@Dawlat_Islam2'):
		base_user = user_name
		# base_user = '@4bu_Muhaj1r'
		mdb_user = get_user_by_user_name(db, base_user)
		# g = nx.DiGraph()
		g = nx.erdos_renyi_graph(30, 0.05)
		add_node_tw(str(mdb_user['_id']), mdb_user['screen_name'])


		for fid,user in get_users_followers(db,base_user):
			add_node_tw(str(user['_id']), user['screen_name'])
			add_edge_tw(str(mdb_user['_id']), str(user['_id']))
			print user['screen_name']

		partition = community.best_partition(g)
		size = float(len(set(partition.values())))

		pos=nx.spring_layout(g)
		count = 0
		for com in set(partition.values()):
			count += 1
			list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == com]
			nx.draw_networkx_nodes(g,pos, list_nodes, node_size = 20, node_color = str(count/size))


		nx.draw_networkx_edges(g,pos,alpha=0.5)
		plt.show()

	nx.draw(g, pos=pos, with_labels=False)
	plt.show()
	with d3py.NetworkXFigure(g, width=1000, height=1000,host="localhost") as p:
	    p += d3py.ForceLayout()
	    p.show()
	plt.savefig("graph.png", dpi=1000)
	# import random
	# g = nx.erdos_renyi_graph(100, 0.05)
	# # val_map = {0: 1.0,
	# #            1: 0.5714285714285714,
	# #            2: 0.0,
	# #            3:}
	# for idx,user_name in enumerate(['@FarisBritani','@4bu_Muhaj1r','@AbuHussain104','@onthatpath3','@jab2victory','@AbooJihad2013','@julaybeeeeb','@AbuTalha001','@AbuDujanah','@Dawlat_Islam2']):
	# 	base_user = user_name
	# 	# base_user = '@4bu_Muhaj1r'
	# 	mdb_user = get_user_by_user_name(db, base_user)
	# 	# g = nx.DiGraph()
	# 	add_node_tw(mdb_user['_id'], mdb_user['screen_name'])


	# 	for fid,user in get_users_followers(db,base_user):
	# 		# add_node_tw(user['_id'], user['screen_name'])
	# 		add_node_tw(user['_id'], '')
	# 		add_edge_tw(mdb_user['_id'], user['_id'])
	# 		print user['screen_name']

	# 	partition = community.best_partition(g)
	# 	size = float(len(set(partition.values())))

	# 	pos=nx.spring_layout(g)
	# 	count = 0
	# 	for com in set(partition.values()):
	# 		count += 1
	# 		list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == com]
	# 		nx.draw_networkx_nodes(g,pos, list_nodes, node_size = 5, node_color = str(random.uniform(0.0,1.0)))


	# 	nx.draw_networkx_edges(g,pos,alpha=0.5)
	# plt.show()