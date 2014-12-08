import os
import sys
import tweepy
import pymongo
from time import sleep


class TinyTweet (object):
    def __init__ (self, tweet, screen_name, verbose=False):
        self.data = {}
        self.update(tweet, screen_name)
        if verbose:
            print 'Tweet:\n'
            for k,v in self.data.iteritems():
                print '\t\t\t%s\t:\t%s' % (k,v)
        
    def update (self, tweet, screen_name):
        self.data['user_name']          = screen_name
        self.data['created_at']         = tweet.created_at
        self.data['coordinates']        = tweet.coordinates
        self.data['in_reply_to_user_id']= tweet.in_reply_to_user_id
        self.data['retweet_count']      = tweet.retweet_count
        self.data['source_url']         = tweet.source_url
        self.data['retweeted']          = tweet.retweeted
        self.data['contributors']       = tweet.contributors
        self.data['geo']                = tweet.geo
        self.data['id']                 = tweet.id
        self.data['source']             = tweet.source
        self.data['text']               = tweet.text
        self.data['lang']               = tweet.lang 

        
    def get_data (self):
        return self.data

class TinyUser (object):
    def __init__ (self, user, verbose=False):
        self.data = {}
        self.update (user)
        if verbose:
            print 'User:\t%s\n' % self.data['screen_name']
            for k,v in self.data.iteritems():
                print '\t\t\t\t%s\t:\t%s' % (k,v)

    def update (self, user):
        self.data['id']                 = user.id
        self.data['folllowers_count']   = user.followers_count
        self.data['location']           = user.location
        self.data['statuses_count']     = user.statuses_count
        self.data['description']        = user.description
        self.data['friends_count']      = user.friends_count
        self.data['geo_enabled']        = user.geo_enabled
        self.data['screen_name']        = user.screen_name
        self.data['lang']               = user.lang
        self.data['name']               = user.name
        self.data['time_zone']          = user.time_zone

    def get_data (self):
        return self.data 
        

        
        


class Munger (object):
    consumer_key    = ''
    consumer_secret = ''
    access_key      = ''
    access_secret   = ''
    def __init__ (self, 
                    verbose=False,
                    con_key=consumer_key,
                    con_sec=consumer_secret,
                    acc_key=access_key,
                    acc_sec=access_secret
                    ):
        '''
            This is the constructor only code within
            this method runs when the munger object is 
            instantiated.
        '''
        assert self._connect()
        self.con_key    = con_key
        self.con_sec    = con_sec
        self.acc_key    = acc_key
        self.acc_sec    = acc_sec
        self.auth       = self._authorize (self.con_key, self.con_sec)
        self.auth.set_access_token (self.acc_key, self.acc_sec)
        self.api        = tweepy.API (self.auth)
        self.verbose    = verbose
        
    def _authorize (self,ck, cs):
        return tweepy.auth.OAuthHandler(ck,cs)
        
    def _connect (self):
        '''
        Create the connection to the MongoDB and create 3 collections needed
        '''
        try:
            self.conn = pymongo.MongoClient()
            print 'MongoDB Connection Successful'
        except pymongo.errors.ConnectionFailure, err:
            print 'MongoDB Connection Unsuccessful'
            return False
            
        self.db = self.conn['GtownTwitter']
        self.users_collection       = self.db.users_collection
        self.friendships_collection = self.db.friendships_collection
        self.tweets_collection      = self.db.tweets_collection
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
        return self.db.collection_names()
        
    def _sleep (self, secs=60):
        print 'Sleeping for %d Seconds' % secs
        sleep(secs)
        
        
    def get_user (self, screen_name):
        '''
        Return User object from specified screen_name
        '''
        return self.api.get_user(screen_name=screen_name)
        
    def get_num_followers (self, user):
        '''
        Return the number of followers from specified user
        '''
        return user.followers_count
        
    def get_remaining_limits (self):
        return self.api.rate_limit_status['remaining_hits']
        
    def get_followers (self, user):
        '''
        Generator that returns followers of specified user
        Sleeps if tweepy rate limit reached
        '''

        followers = tweepy.Cursor(self.api.followers, id=user).items()
        while True:
            try:
                yield followers.next()
            except tweepy.TweepError:
                self._sleep(secs=60*15)
                continue
            except StopIteration:
                break
                
    def get_friends (self, user):
        '''
        Generator that returns friends of specified user
        Sleeeps if tweepy rate limit reached.
        '''
        friends = tweepy.Cursor (self.api.friends, id=user).items()
        while True:
            try:
                yield friends.next()
            except tweepy.TweepError:
                self._sleep(secs=60*15)
                continue
            except StopIteration:
                break        
    
    def get_tweets (self, user):
        '''
        Generator that returns tweets of a user
        Sleeps if tweepy rate limit reached
        '''
        tweets = tweepy.Cursor (self.api.user_timeline, id=user.id, include_entities=True, lang='en').items()
        while True:
            try:
                T = TinyTweet(tweets.next(), user.screen_name, verbose=self.verbose)
                yield T.get_data()
            except tweepy.TweepError:
                self._sleep(secs=60*15)
                continue
            except StopIteration:
                break

    def process_user (self, screen_name):
        user = self.get_user (screen_name)
        user_obj = TinyUser (user, verbose=self.verbose)
        user_data = user_obj.get_data()

        mdb_user_id = self.users_collection.insert (user_data)
        
        for tweet in self.get_tweets (user):

            tweet.update ({'user_id': mdb_user_id})
            self.tweets_collection.insert(tweet)
            
        self._sleep (secs=10)
        
        for friend in self.get_friends (user):
            friend_obj = TinyUser(friend, verbose=self.verbose)
            friend_data = friend_obj.get_data()

            frdb_user_id = self.users_collection.insert (friend_data)
            self.friendships_collection.insert ({'user_id':frdb_user_id, 'follower_id':mdb_user_id})
            for tweet in self.get_tweets (friend.id):
                tweet.update ({'user_id': frdb_user_id})

                self.tweets_collection.insert (tweet)
                
        self._sleep (secs=10)
        
        for follower in self.get_followers (user):
            follower_obj = TinyUser(follower, verbose=self.verbose)
            follower_data = follower_obj.get_data()

            fodb_user_id = self.users_collection.insert (follower_data)
            self.friendships_collection.insert ({'user_id':mdb_user_id, 'follower_id':fodb_user_id})
            for tweet in self.get_tweets (follower):
                tweet.update ({'user_id': fodb_user_id})

                self.tweets_collection.insert (tweet)
                
        self._sleep (secs=10)
        
        
if __name__ == '__main__':
    m = Munger(verbose=True)
    m.process_user('@AbooJihad2013')
    #m.process_user('@jab2victory')
    #for user_name in ('@onthatpath3','@jab2victory','@AbooJihad2013','@julaybeeeeb','@AbuTalha001', '@AQIS_Bangla'):
        #m.process_user(user_name)