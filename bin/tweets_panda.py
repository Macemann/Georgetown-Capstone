import os
import sys
import tweepy
import pymongo
import pandas as pd
from pandas.tseries.resample import TimeGrouper
from pandas.tseries.offsets import DateOffset
from time import sleep
import vincent





class Pandadf (object):


    def __init__ (self, verbose = False):

        assert self._connect()
        self.verbose = verbose


    def _connect (self):
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



        # These are the 3 collections created.  --> Similar to tables.  The names are actually [users_collection, friendships_collection, tweets_collection]
        self.users_collection       = self.db.users_collection
        self.friendships_collection = self.db.friendships_collection
        self.tweets_collection      = self.db.tweets_collection
        self.retweet_collection     = self.db.retweet_collection


        return True
        
    def get_db_names (self):
        '''
        Return the names of database_names
        '''
        return self.con.database_names()
        
    def get_collection_names (self):
        '''
        Return the names of collections
        '''
        print self.db.collection_names()

    # This will read the tweets collection and find retweets

    def panda_df (self):
        print "User name query tweet count:", self.tweets_collection.find({'user_name': 'AbooJihad2013'}).count()
        print self.tweets_collection.distinct("user_name")
        df = pd.DataFrame(list(self.tweets_collection.find()))  ##Mark - AbooJihad2013 & 4bu_Muhaj1r

        df['created_at'] = pd.to_datetime(pd.Series(df['created_at']))
        df.set_index('created_at', drop = False, inplace=True)
        df.index



        print df.head()
        print df.describe()
        tweet_freq = df['created_at'].resample('D', how='count') ##counts tweets per day
        print tweet_freq.head()
        tweet_freq.to_csv("C:\Users\Mason\Desktop\panda_csv.csv",encoding='utf-8')


        avg_tweets = tweet_freq.mean()
        print "Average tweets per day:", avg_tweets



        ##bar = vincent.Bar(tweet_freq)
        ##bar.to_json('bar.json', html_out=True, html_path='bar_template.html')




if __name__ == '__main__':
    pdf = Pandadf()
    pdf.get_collection_names()
    pdf.panda_df()




