from pymongo import MongoClient
import nltk
from Processors import TextPreprocessor
import pickle
import collections
import os

MODELS_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))),'models')

if __name__ == '__main__':
	conn = MongoClient()
	db = conn['GtownTwitter_PROD']
	tweets_col = db['tweets_collection']

	dts = set([])
	# Instantiate the Text Preprocessor to do the text manipulation
	tp = TextPreprocessor()

	tokens = []
	# Iterate over tweets ordered by date
	for tweet in tweets_col.find().sort('created_at'):
		if tweet['created_at'] not in dts:

			# Process the tweet text and add to corpus
			tp.process(tweet['text'])
			tokens.extend(tp.tokens)

	text = nltk.Text(tokens)
	words = ['isis', 'islamicstate', 'caliphate','jihad','american','british','usa']
	text.dispersion_plot(words)

	bgm    = nltk.collocations.BigramAssocMeasures()
	finder = nltk.collocations.BigramCollocationFinder.from_words(text)
	scored = finder.score_ngrams(bgm.likelihood_ratio)

	# Group bigrams by first word in bigram.                                        
	prefix_keys = collections.defaultdict(list)
	for key, scores in scored:
	   prefix_keys[key[0]].append((key[1], scores))

	# Sort keyed bigrams by strongest association.                                  
	for key in prefix_keys:
	   prefix_keys[key].sort(key = lambda x: -x[1])

  	html='<p style="border-color:black; border:1px;"><h2><font color="red">Collocations and Likelihood Ratio</font></h2><br><br><hr><ol>'
	for word in words:
		print word, prefix_keys[word][:5]
		html='%s<li><b><font color="red">%s</b></font><br>%s</li>' % (html,word, '<br>'.join(['%s:&nbsp;%s' % (x[0],x[1]) for x in prefix_keys[word][:5]]))
	html='%s</ol></p>' % html
	print html

	with open(os.path.join(MODELS_PATH,'collocations.pkl'),'wb') as handler:
		pickle.dump(html, handler)

