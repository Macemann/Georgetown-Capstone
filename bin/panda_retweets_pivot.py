############################################################################################################
########################   Panda Retweets               ####################################################
############  Inputs retweets from Mongo collection
############  Then uses creates a Pandas pivot table total by tweeted / retweeted account
############  Author:  Mark Phillips
############  Created: November 2014

import os
import sys
import tweepy
import pymongo
import pandas as pd
import numpy as np
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
        # print "User name query tweet count:", self.tweets_collection.find({'user_name': 'AbooJihad2013'}).count()
        # print self.tweets_collection.distinct("user_name")
        rt_df = pd.DataFrame(list(self.retweet_collection.find()))  ##Mark - AbooJihad2013 & 4bu_Muhaj1r
        tweets_df = pd.DataFrame(list(self.tweets_collection.find()))





        print rt_df.head()
        print rt_df.describe()
        print rt_df.groupby('rt_screen_name').size()

        #indexed_rt_df = rt_df.set_index('twt_collection_id')
        #print indexed_rt_df.head()
        df_joined = pd.merge(rt_df, tweets_df, left_on='twt_collection_id', right_on='_id', how='left')
        joined_rtwt = df_joined[['user_name', 'rt_screen_name', 'rt_text']]
        # print joined_rtwt.head()

        pvt_rtwt = joined_rtwt.pivot_table(cols = 'user_name',rows='rt_screen_name', aggfunc = len, fill_value=0)

        print pvt_rtwt.head()

        pvt_rtwt.to_csv("C:\Users\Phlong\PycharmProjects\georgetown-tweepy\panda_rtwt_csv.csv",encoding='utf-8')


        #avg_tweets = tweet_freq.mean()
        #print "Average tweets per day:", avg_tweets








if __name__ == '__main__':
    pdf = Pandadf()
    pdf.get_collection_names()
    pdf.panda_df()




