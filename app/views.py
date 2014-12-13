'''
Script to construct the views for the 2 types of pages for output

__author__ = Ryan Stephany
__purpose__ Georgetown Data Analytics


'''

# import required modules
from flask import render_template, url_for, Flask
from app import app
import os
from sklearn.metrics.pairwise import linear_kernel
from pymongo import MongoClient
import pickle
from Processors import TextPreprocessor


# declare GLOBALS
PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))),'models')
with open(os.path.join(MODELS_PATH,'hidden_names.pkl'),'rb') as handler:
    NAMES = pickle.load(handler)

# NOTE: do I need this anymore  -- dont think its used
USERS = NAMES['FROM_HIDDEN'].keys()
# I don't want to show any twitter info that can be identified for each user
REMOVE_USER_KEYS = ('id')
CONN = MongoClient()
DB = CONN['GtownTwitter_PROD']




# with open(os.path.join(MODELS_PATH,'tfidf.pkl'),'rb') as handler:
#     TFIDF = pickle.load(handler)

# with open(os.path.join(MODELS_PATH,'tfidf_index.pkl'),'rb') as handler2:
#     TFIDF_INDEXES = pickle.load(handler2)

with open(os.path.join(MODELS_PATH,'tfidf_similar.pkl'),'rb') as tfidf_handler:
    SIMILARITIES = pickle.load(tfidf_handler)

with open(os.path.join(MODELS_PATH,'graph_measures.pkl'), 'rb') as handler3:
    GRAPH_MEASURES = pickle.load(handler3)

with open(os.path.join(MODELS_PATH,'collocations.pkl'), 'rb') as handler4:
    collocations = pickle.load(handler4)

#create mappings for the '/' and 'index' urls
@app.route('/')  
@app.route('/index')
def index():
    users = NAMES['FAKENAME_FROM_NICKNAME']
    user = {'nickname':'Ryan'}
    all_graph = GRAPH_MEASURES['all']
    graph_stats = all_graph['stats']
    degree_cent = all_graph['degree_centrality']
    betweenness_cent = all_graph['betweenness_centrality']
    closeness_cent = all_graph['closeness_centrality']
    eigenvector_cent = all_graph['eigenvector_centrality']
    katz_cent = all_graph['katz_centrality']

    return render_template('index.html', user=user, users=users, graph_stats=graph_stats,
             degree_centrality=degree_cent, betweenness_centrality=betweenness_cent,
             closeness_centrality=closeness_cent,eigenvector_centrality=eigenvector_cent,
             katz_centrality=katz_cent, collocations=collocations)


# create mapping for a given anonymous user name  
@app.route('/user/<nickname>')  
def user(nickname):
    #check if fake screen name is one of our peeps
    if nickname in NAMES['FROM_HIDDEN'].keys():
        user = DB['users_collection'].find_one({'screen_name':NAMES['FROM_HIDDEN'][nickname][1:]})
    else:
        user = None

    if user == None:
        # bad screen_name redirect to index page
        # flash('User %s not found.' % nickname)
        return redirect(url_for('index'))

    #instantiate the TextPreprocessor
    tp = TextPreprocessor()

    #replace the names
    user['screen_name'] = nickname
    user['name'] = NAMES['FROM_HIDDEN'][nickname]
    user['name'] = NAMES['FAKENAME_FROM_NICKNAME'][nickname]

    user = dict((k,v) for k,v in user.iteritems() if k not in (REMOVE_USER_KEYS))


    # create the lists of preprocessed posts
    # posts with duplicate datetimes are removed, not sure if I messed up in the wrangling/munging but I am viewing duplicate posts
    posts = []
    dts = set([])
    cursor = DB['tweets_collection'].find({'user_id': user['_id']}).sort("created_at",1)
    for post in cursor:
        if post['created_at'] not in dts:
            tweet_dict = {}

            tp.process(post['text'])
            tweet_dict['Keywords'] = tp.processed_text
            tweet_dict['author'] = nickname
            tweet_dict['Id'] = post['_id']
            tweet_dict['Date'] = post['created_at'] 

            # top_five_sims = SIMILARITIES[post['_id']]
            tweet_dict['html'] = SIMILARITIES[post['_id']]

            posts.append(tweet_dict)

            dts.add(post['created_at'])


    # open the pickles of percentage of word frequencies/frequencies of words
    # NOTE: nltk.FreqDist is ordered dict
    with open(os.path.join(PATH,'models/%s_bow_perc.pkl' % nickname), 'rb') as handler1:
        wfp = pickle.load(handler1)

    with open(os.path.join(PATH,'models/%s_bow_n.pkl' % nickname), 'rb') as handler2:
        wfn = pickle.load(handler2)



    # grab the top N for each to display in app
    word_freqs = wfp[:500]
    top_ten = wfn[:10]
    for i,d in enumerate(word_freqs):
        d['size'] = 10000*d['size']
        word_freqs[i] = d


    users_graph = GRAPH_MEASURES[nickname]

    with open(os.path.join(MODELS_PATH,'%s_ts.pkl' % nickname),'rb') as handler4:
        time_series = pickle.load(handler4)


    graph_stats = users_graph['stats']
    degree_cent = users_graph['degree_centrality']
    betweenness_cent = users_graph['betweenness_centrality']
    closeness_cent = users_graph['closeness_centrality']
    eigenvector_cent = users_graph['eigenvector_centrality']
        # katz_cent = users_graph['katz_centrality']
    # graph_stats = {'fake': 'value'}


    return render_template('home.html',
                           user=user,
                           posts=posts,
                           word_cloud=word_freqs,
                           top_ten=top_ten,
                           graph_stats=graph_stats,
                           degree_centrality=degree_cent,
                           betweenness_centrality=betweenness_cent,
                           closeness_centrality=closeness_cent,
                           eigenvector_centrality=eigenvector_cent,
                           time_series=time_series)
    