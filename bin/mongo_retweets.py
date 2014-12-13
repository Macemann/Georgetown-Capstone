######################################################################################################
##########                      Mongo Retweets Collection                  ##########################
########## Reads tweets collection, finds tweets with "RT" in text
########## Spits out the retweeted user id and tweet then writes to new retweet collection
##########  Author:  Mark Phillips
##########  Created: October 2014

import os
import sys
import tweepy
import pymongo
from time import sleep





class Retwt (object):


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

        # This is the name of the database  -'GtownTwitter'
        self.db = self.conn['GtownTwitter_PROD']



        # These are the 3 collections created.  --> Similar to tables.  The names are actually [users_collection, friendships_collection, tweets_collection]
        self.users_collection       = self.db.users_collection
        self.friendships_collection = self.db.friendships_collection
        self.tweets_collection      = self.db.tweets_collection
        self.retweet_collection     = self.db.retweet_collection  #try 2
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

    # This will read the tweets collection and find retweets and insert to the rt_users_collection

    def extract_retweets (self):
        tweets = self.db.tweets_collection.find()   ##remove limit after testing !!
        screen_nm_list = []

        for tweet in tweets:
            txt = tweet["text"]
            #print txt

            if txt[:2] == "RT":
                rt = txt.split()
                rt_id = rt[1]
                rt_id = rt_id[:-1]
                rt_id = rt_id[1:]
                #print rt_id
                screen_nm_list.append(str(rt_id))
                #print screen_nm_list
                self.retweet_collection.insert({"twt_collection_id": tweet["_id"], "rt_screen_name": rt_id, "rt_text":txt})

        unique_screen_names = set(screen_nm_list)
        print unique_screen_names

    ####add import Munger from tweep and use get_user function for unique_screen_names. Then write to rt_users_collection


if __name__ == '__main__':
    rt = Retwt()
    rt.get_collection_names()
    rt.extract_retweets()


