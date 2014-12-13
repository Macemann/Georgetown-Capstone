# ################################################################################
############ Generates Network Diagram from GTownTwitter_PROD DB     #############
############ outputs in graph file format                            #############
############
##### Author:  Mark Phillips
##### Created: December 2014


import pymongo
import pandas as pd
import networkx as nx


class Pandadf(object):
    def __init__(self, verbose=False):

        assert self._connect()
        self.verbose = verbose


    def _connect(self):
        '''
        Create the connection to the MongoDB and create 3 collections needed
        '''
        try:
            # Create the connection to the local host
            self.conn = pymongo.MongoClient()
            print 'MongoDB Connection Successful'
        except pymongo.errors.ConnectionFailure, err:
            print 'MongoDB Connection Unsuccessful'
            return False

        # This is the name of the database  -'GtownTwitter-Production final'
        self.db = self.conn['GtownTwitter_PROD']

        #self.screen_name = screen_name


        # These are the 3 collections created.  --> Similar to tables.  The names are actually [users_collection, friendships_collection, tweets_collection]
        self.users_collection = self.db.users_collection
        self.friendships_collection = self.db.friendships_collection
        self.tweets_collection = self.db.tweets_collection
        self.retweet_collection = self.db.retweet_collection

        return True

    def get_db_names(self):
        '''
        Return the names of database_names
        '''
        return self.con.database_names()

    def get_collection_names(self):
        '''
        Return the names of collections
        '''
        print self.db.collection_names()

    def get_user_info(self, id_in):

        ## Return the screen names for user id
        print id_in

        print self.users_collection.find({'id': id_in}, {'screen_name': 1}).rewind()

        return self.db.users_collection.find({'id': id_in}, {'screen_name': 1, '_id': 0})


    # This will read the tweets collection and find retweets


    def panda_df(self):
        # print "User name query tweet count:", self.tweets_collection.find({'user_name': 'AbooJihad2013'}).count()
        # print self.tweets_collection.distinct("user_name")
        users_df = pd.DataFrame(list(self.users_collection.find()))
        friendships_df = pd.DataFrame(list(self.friendships_collection.find()))

        #print friendships_df.head()
        print friendships_df.describe()
        #print friendships_df.groupby('follower_id').size()

        ## create dataframe that includes leader - follower relationship

        friendships_df.rename(columns={'_id': 'f_id'}, inplace=True)

        df_join1 = pd.merge(friendships_df, users_df, left_on='follower_id', right_on='_id',
                            how='left')  ## need to join twice to get user and follower names in one DF
        #print df_join1.head()
        df_join1 = df_join1[['f_id', 'follower_id', 'user_id', 'screen_name', 'id']]
        df_join1.rename(columns={'screen_name': 'follower_name'}, inplace=True)
        df_join1.rename(columns={'id': 'follower_userid'}, inplace=True)
        #print df_join1.head()

        df_join2 = pd.merge(df_join1, users_df, left_on='user_id', right_on='_id',
                            how='left')  ## join 2 to get leader user name
        #print df_join2.head()
        df_join2 = df_join2[['f_id', 'follower_id', 'user_id', 'follower_name', 'screen_name', 'follower_userid', 'id']]
        df_join2.rename(columns={'screen_name': 'leader_name'}, inplace=True)
        #print df_join2.head()

        return (users_df, df_join2)  ### sometimes needs render() ??


        #df.to_csv("C:\Users\Phlong\PycharmProjects\georgetown-tweepy\panda_rtwt_csv.csv",encoding='utf-8')


if __name__ == '__main__':
    pdf = Pandadf()
    pdf.get_collection_names()
    pdf.panda_df()

    usersdf, friendshipsdf = pdf.panda_df()

    print friendshipsdf.head()

    ### reference Gilad Lotan Networkx & Gephi tutorial

def get_user_info_df(n):

    one_user_df = usersdf[usersdf.id == n]
    #print one_user_df
    user_name = one_user_df.iloc[0,10]
    #print user_name
    return user_name


def add_node_tw(n, weight=None, time=None, source=None, location=None):
    if not g.has_node(n):
        #screen_name =str(n)

        screen_name = get_user_info_df(n)
        g.add_node(n)
        g.node[n]['weight'] = 1
        g.node[n]['screen_name'] = screen_name

    else:
        g.node[n]['weight'] += 1


def add_edge_tw(n1, n2, weight=None):
    """

        :rtype :
        """
    if not g.has_edge(n1, n2):
        g.add_edge(n1, n2)
        g[n1][n2]['weight'] = 1
    else:
        g[n1][n2]['weight'] += 1

# generate set of users
users = usersdf.id.tolist()

# directed graph
g = nx.DiGraph()

# add nodes/edges
for u_id in users:
    add_node_tw(u_id)
    #cursor.execute(select * from friendships collection where follower_userid = u_id)

print len(g)

for index, row in friendshipsdf.iterrows():
    print index
    add_edge_tw(row['id'], row['follower_userid'])

print g.number_of_edges()

nx.write_gexf(g, "C:\Users\Phlong\PycharmProjects\georgetown-tweepy\panda_graph3.gexf", encoding='utf-8')




##graphml = networkx.exception.NetworkXError: GraphML writer does not support <class 'pymongo.cursor.Cursor'> as data values.