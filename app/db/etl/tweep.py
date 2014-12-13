import os
import sys
import tweepy
import pymongo
from time import sleep, clock
from Entities import EntityExtractor
from Genders import GenderPredictor


class TinyTweet (object):
    '''
    This filters the Tweepy Status Object to keep just the items we want
    Verbose is used to print the output.
    useage:
    T = TinyTweet(Status, screen_name)
    tweet_dictionary = T.get_data()
    '''

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
    '''
    This filters the Tweepy User Object to just keep the items we want
    Verbose is used to print the outputs

    U = TinyUser(User)
    user_dictionary = U.get_data()
    '''

    def __init__ (self, user, predict_gender=True, verbose=False):
        self.data           = {}
        self.predict_gender = predict_gender
        if predict_gender:
            self.g = GenderPredictor()
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
        if self.predict_gender:
            self.data['gender']         = self.g.predict_gender(user.name)

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
                    acc_sec=access_secret,
                    extract_entities=True,
                    predict_gender=True
                    ):
        '''
            This is the constructor only code within
            this method runs when the munger object is 
            instantiated.
        '''
        self.extract_entities   = extract_entities
        self.predict_gender     = predict_gender

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
        '''
        This is used for authorization
        '''
        return tweepy.auth.OAuthHandler(ck,cs)
        
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
        self.db = self.conn['GtownTwitter']

        # These are the 5 collections created.  --> Similar to tables.  The names are actually [users_collection, friendships_collection, tweets_collection, entities_collection, stems_collection]
        # Although possible only 3 collections might be created
        self.users_collection       = self.db.users_collection
        self.friendships_collection = self.db.friendships_collection
        self.tweets_collection      = self.db.tweets_collection
        if self.extract_entities:
            self.entities_collection    = self.db.entities_collection
            self.stems_collection           = self.db.stems_collection
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
        '''
        Pause the script for N specified seconds
        '''
        print 'Sleeping for %d Seconds' % secs
        sleep(secs)
        
        
    def get_user (self, screen_name):
        '''
        Return Tweepy User object from specified screen_name
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
        Generator that yields followers of specified user
        Sleeps if tweepy rate limit reached
        '''

        followers = tweepy.Cursor(self.api.followers, id=user.id).items()
        while True:
            try:
                yield followers.next()
            except StopIteration:
                break
            except tweepy.TweepError, e:
                print e
                self._sleep(secs=60*15)
                continue
                
    def get_friends (self, user):
        '''
        Generator that yields friends of specified user
        Sleeeps if tweepy rate limit reached.
        '''
        friends = tweepy.Cursor (self.api.friends, id=user.id).items()
        while True:
            try:
                yield friends.next()
            except StopIteration:
                break   
            except tweepy.TweepError, e:
                print e
                self._sleep(secs=60*15)
                continue    
    
    def get_tweets (self, user):
        '''
        Generator that yields tweets of a user
        Sleeps if tweepy rate limit reached
        '''
        tweets = tweepy.Cursor (self.api.user_timeline, id=user.id, include_entities=True, lang='en').items()
        while True:
            try:
                T = TinyTweet(tweets.next(), user.screen_name, verbose=self.verbose)
                yield T.get_data()
            except StopIteration:
                break
            except tweepy.TweepError:
                self._sleep(secs=60*15)
                continue

    def process_user (self, screen_name):
        '''
        This processes everything for 1 user
        '''

        # Keep track of counts that are inserted into the mongo collections
        tweets          = 0
        users           = 0
        friendships     = 0
        entities        = 0

        # Get the Tweepy user object from a screen name
        user = self.get_user (screen_name)
        _ = self.users_collection.find_one({"screen_name":user.screen_name})
        if _:
            mdb_user_id = _['_id']
        else:
            # Create the Tiny User object of what we want to keep from the user
            user_obj = TinyUser (user, predict_gender=self.predict_gender, verbose=self.verbose)
            user_data = user_obj.get_data()
            
            # Insert the user into mongo and return the auto generated id to be used with friendships table later 
            mdb_user_id = self.users_collection.insert (user_data)
            users += 1
        
        # Interate over all that users tweets
        for tweet in self.get_tweets (user):
            #Check to make sure the tweet is english
            if tweet['lang'].find('en') > -1:

                # Add an item to the Tweet dictionary with the mongo given id of the user
                d = {'user_id': mdb_user_id}
                if self.extract_entities:
                    e       = EntityExtractor(tweet)
                    ents    = list(set([j.lower() for j in e.get_entities()]))
                    stems   = e.get_entity_stems(ents)
                    d.update({'Entities': ents})
                tweet.update(d)

                # Insert the tweet into mongo
                mdb_tw_id = self.tweets_collection.insert(tweet)
                tweets += 1

                if self.extract_entities:

                    for idx, each_entity in enumerate(ents):
                        stem = stems[idx]
                        _sid = self.stems_collection.find_one({'entity': stem})
                        _eid = self.entities_collection.find_one({'entity': each_entity})

                        if not _eid:
                            _eid = self.entities_collection.insert ({'entity': each_entity, 'tweet_ids': [mdb_tw_id]})
                            entities += 1
                        else:
                            _eid = _eid['_id']
                            self.entities_collection.update ({'_id': _eid}, {'$addToSet':{'tweet_ids':mdb_tw_id}})
                            #self.entities_collection.update ({'_id': _eid}, {'$push': {'tweet_ids': {'$each':[mdb_tw_id]}}})
                        
                        if not _sid:
                            _sid = self.stems_collection.insert({'entity': stem, 'entity_ids':[_eid]})
                        else:
                            _sid = _sid['_id']
                            self.stems_collection.update ({'_id': _sid}, {'$addToSet':{'entity_ids':_eid}})
                            #self.stems_collection.update ({'_id': _sid['_id']}, {'$push': {'entity_ids': {'$each':[_eid]}}})


            
        # Take a 10 second Break    
        self._sleep (secs=10)
        
        # Iterate over all the friends (people that the user is following)  --> friend is actually a Tweepy User Object
        for friend in self.get_friends (user):

            _ = self.users_collection.find_one ({'id':friend.id})
            if _:
                frdb_user_id = _['_id']
            else:
                # Filter to keep only the User data we want to keep
                friend_obj = TinyUser(friend, predict_gender=self.predict_gender, verbose=self.verbose)
                friend_data = friend_obj.get_data()

                # Insert the friend into the users collection, get the Id given by mongo
                frdb_user_id = self.users_collection.insert (friend_data)
                users += 1

            # Insert into the friendships collection the Friend is followed by User
            self.friendships_collection.insert ({'user_id':frdb_user_id, 'follower_id':mdb_user_id})
            friendships += 1

            # Commented out to not collect tweets from followers

            # Iterate over all the friends tweets
            #for tweet in self.get_tweets (friend):
                # Add the friends user_id into the tweet dictionary
                #tweet.update ({'user_id': frdb_user_id})

                # Insert the friend tweet into the tweets collection
                #self.tweets_collection.insert (tweet)
                #tweets += 1

        # Take a 10 second Break     
        self._sleep (secs=10)
        
        # Iterate over the followers of the user  --> follower is a Tweepy User Object
        for follower in self.get_followers (user):

            _ = self.users_collection.find_one({'id':follower.id})
            if _:
                fodb_user_id = _['_id']
            else:
                # Filter the User to only keep the items we want from them
                follower_obj = TinyUser(follower, predict_gender=self.predict_gender, verbose=self.verbose)
                follower_data = follower_obj.get_data()

                # Insert the User dictionary into the mongo users collection, keep the autogenerated id
                fodb_user_id = self.users_collection.insert (follower_data)
                users += 1

            # Insert into the mongo friendships table that user is followed by follower
            self.friendships_collection.insert ({'user_id':mdb_user_id, 'follower_id':fodb_user_id})
            friendships += 1

            # Commented out to not collect tweets from friends
            # Iterate over all of the followers tweets
            #for tweet in self.get_tweets (follower):

                # Add an item to the tweet dictionary
                #tweet.update ({'user_id': fodb_user_id})

                # Insert the tweet dictionary into the mongo tweets collection
                #self.tweets_collection.insert (tweet)
                #tweets += 1
                
        # Return the counts of all documents added to mongodb
        return users, tweets, friendships, entities
        
        
if __name__ == '__main__':
    m = Munger(verbose=True, extract_entities=True, predict_gender=True)

    total_tweets        = 0
    total_friendships   = 0
    total_users         = 0
    total_entities      = 0

    for user_name in ('@FarisBritani','@4bu_Muhaj1r','@AbuHussain104','@onthatpath3','@jab2victory','@AbooJihad2013','@julaybeeeeb','@AbuTalha001','@AbuDujanah','@Dawlat_Islam2'):
        #'@AbuDujanah'
        start = clock()
        # try:
        m.process_user(user_name)
        users_added, friendships_added, tweets_added, entities_added = m.process_user(user_name)
        print 'Processed User : %s\n\tProcessing time: %f seconds' % (user_name, clock()-start) 
        print '%s -- Friendships: %d' % (user_name, friendships_added)
        print '%s -- Tweets: %d' % (user_name, tweets_added)
        print '%s -- Users: %d' % (user_name, users_added)
        total_tweets        += tweets_added
        total_users         += users_added
        total_friendships   += friendships_added
        # except:
        #     pass

    print '\n\n\n*************************************************************'
    print 'Total Tweets : %d' % total_tweets
    print 'Total Friendships : %d' % total_friendships
    print 'Total Users : %d' % total_users
    print '****************************************************************'
