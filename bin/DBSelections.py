from bson import ObjectId

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
    
def get_users_tweets (db, user_name):
	user_id = _get_mongo_user_id(db, user_name)
	if user_id:
		for tweet in _simple_query(db,'tweets_collection','user_id', user_id):
			yield tweet



def get_users_followers (db, user_name):
	user_id = _get_mongo_user_id(db, user_name)
	if user_id:
		for follower in _simple_query(db,'friendships_collection','user_id', user_id):
			yield follower['_id'], _simple_query_one(db,'users_collection', '_id', follower['follower_id'])

def get_users_friends (db, user_name):
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
    import pandas as pd
	import matplotlib.pyplot as plt
	conn = MongoClient()
	db = conn.GtownTwitter_PROD

    #NetworkX Graph example
	base_user = '@FarisBritani'
	mdb_user = get_user_by_user_name(db, base_user)
	g = nx.DiGraph()
	add_node_tw(mdb_user['_id'], mdb_user['screen_name'])


	for fid,user in get_users_followers(db,'@FarisBritani'):
		add_node_tw(user['_id'], user['screen_name'])
		add_edge_tw(mdb_user['_id'], user['_id'])
		print user['screen_name']
	pos=nx.spring_layout(g)
	nx.draw(g, pos=pos, with_labels=False)
	plt.savefig("graph.png", dpi=1000)
    
    
    
    
    #Pandas Example
	base_user = '@FarisBritani'
	mdb_user = get_user_by_user_name(db, base_user)
    
    #This is a cursor or also known as python generator
    tweets_cursor = get_users_tweets(db, base_user)
    
    #This is now a list of tweet documents
    tweets_list = list(tweets_cursor)
    
    df = pd.DataFrame(tweets_list)
    
    print df
    
    
    
    
