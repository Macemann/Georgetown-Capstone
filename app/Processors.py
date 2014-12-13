
import re
import sys
import nltk
import unicodedata


PUNCTUATION 	= dict.fromkeys(i for i in xrange(sys.maxunicode)
                      if unicodedata.category(unichr(i)).startswith('P'))


STOPWORDS 		= set(nltk.corpus.stopwords.words('english'))

IMPORTANT_POS	= ['NN','NNS','NNP','NNPS','RB','RBR','RBS','VB','VBG','VBN','VBD','VBP','VBZ','JJ','IN','JJR','JJS']

EMOTICONS 	=	{
					'&lt;3' :' good ',
					':d'	:' good ',
					':dd'	:' good ',
					'8)'	:' good ',
					':-)'	:' good ',
					':)'	:' good ',
					';)'	:' good ',
					'(-:'	:' good ',
					'(:'	:' good ',

					':/'	:' bad ',
					':&gt'	:' sad ',
					":')"	:' sad ',
					':-('	:' bad ',
					':('	:' bad ',
					':S'	:' bad ',
					':-S'	:' bad '
				}

ABBREVIATIONS 	= 	{
						r'\br\b'		: 'are',
						r'\bu\b'		: 'you',
						r'\bhaha\b'		: 'ha',
						r'\bhahaha\b'	: 'ha',
						r"\bdon't\b"	: 'do not',
						r"\bdoesn't\b"	: 'does not',
						r"\bdidn't\b"	: 'did not',
						r"\bhasn't\b"	: 'has not',
						r"\bhaven't\b"	: 'have not',
						r"\bhadn't\b"	: 'had not',
						r"\bwon't\b"	: 'will not',
						r"\bwouldn't\b"	: 'would not',
						r"\bcan't\b"	: 'can not',
						r"\bcannot\b"	: 'can not'

					}



class TextPreprocessor (object):
	'''
	Class to preprocess text from a string
	Text can be returned in string or list types
	Expects Unicode Text
	'''
	
	def __init__ (self, stopwords=STOPWORDS,
					 keep_important=True, remove_emoticons=True,
					 remove_punctuation=True, replace_abbreviations=True):
		self.stopwords 				= stopwords
		self.keep_important 		= keep_important
		self.remove_punctuation 	= remove_punctuation
		self.remove_emoticons 		= remove_emoticons
		self.repl_order 			= []
		if self.remove_emoticons:
			self.repl_order			= [k for (k_len,k) in reversed(sorted([(len(k), k) for k in EMOTICONS.keys()]))]
		self.replace_abbreviations 	= replace_abbreviations
		self.processed_text 		= ''
		self.tokens 				= []

	def get_text (self):
		return self.processed_text

	def get_tokens (self):
		return self.tokens

	def rep_abbr (self, text):
		'''
		Replaces abbreviations in text with the two word meaning
		'''
		for abbr, repl in ABBREVIATIONS.iteritems():
			text = re.sub(abbr, repl, text)
		return text

	def rem_emos (self, text):
		'''
		Replaces Emoticons, which occur frequently in tweets with words
		such as 'good' or 'bad'
		'''
		for emo in self.repl_order:
			text = text.replace(emo,EMOTICONS[emo])
		return text

	def keep_imp (self, tokens):
		'''
		Only keep the important terms from the list of words
		Terms are determined important by the Part of Speech
		'''
		tags = nltk.pos_tag(tokens)
		return [term for (term,tag) in tags if tag in IMPORTANT_POS]

	def process (self, text):
		'''
		Method to process text from defined class options
		'''
		self.text = text
		self.processed_text = text.lower()
		if self.remove_emoticons:
			self.processed_text = self.processed_text.translate(PUNCTUATION)
		if self.replace_abbreviations:
			self.processed_text = self.rep_abbr(self.processed_text)
		if self.remove_emoticons:
			self.processed_text = self.rem_emos(self.processed_text)

		self.tokens = [w for w in nltk.word_tokenize(self.processed_text) if w not in self.stopwords]
		if self.keep_important:
			self.tokens = self.keep_imp(self.tokens)
		self.processed_text = ' '.join(self.tokens)






def create_freq_dists (names, outdir, fake_screen_name=None):
	'''
	This is a function to create pickled frequency distributions used in the app
	It should be split into a class.
	'''
	db = MongoClient()
	conn = MongoClient()
	db = conn['GtownTwitter_PROD']
	tweets_col = db['tweets_collection']
	tp = TextPreprocessor()
	corpora = []
	if fake_screen_name:
		print os.path.abspath(__file__)
		# print os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__)),'/models/hidden_names.pkl')
		with open(names,'rb') as handler:
			NAMES = pickle.load(handler)

		user_name = NAMES['FROM_HIDDEN'][fake_screen_name]
		user_name = user_name.replace('@','')
		cursor = tweets_col.find({'user_name':user_name})
	else:
		fake_screen_name = 'all'
		user_name = 'all'
		cursor = tweets_col.find()

	for tweet in cursor:
		if tweet['lang'].find('en') > -1:
			print tweet['text']
			tp.process(tweet['text'].translate(PUNCTUATION))

			corpora.extend(tp.tokens)
	fdist = nltk.FreqDist(corpora)		
	n = fdist.N()
	js_text_perc = []
	js_text_n = []
	for k,v in fdist.iteritems():
		if v > 4 and k != u'%s' % 'rt':
			try:
				js_text_perc.append({'text':str(k), 'size': float(v)/n})
				js_text_n.append({'text':str(k), 'size':v})
			except:
				continue

	with open(os.path.join(outdir,'%s_bow_n.pkl' % fake_screen_name), 'wb') as n_handle:
  		pickle.dump(js_text_n, n_handle)

  	with open(os.path.join(outdir,'%s_bow_perc.pkl' % fake_screen_name), 'wb') as perc_handle:
  		pickle.dump(js_text_perc, perc_handle)
	print fdist

if __name__ == '__main__':
	from pymongo import MongoClient
	import pickle
	import os
	# conn = MongoClient()
	# db = conn['GtownTwitter_PROD']
	# tweets_col = db['tweets_collection']
	# tp = TextPreprocessor()
	# corpora = []
	# for user_name in  ('@FarisBritani','@4bu_Muhaj1r','@AbuHussain104','@onthatpath3','@jab2victory','@AbooJihad2013','@julaybeeeeb','@AbuTalha001','@AbuDujanah','@Dawlat_Islam2'):
	# 	user_name = user_name.replace('@','')
	# 	for tweet in tweets_col.find({'user_name':user_name}):
	# 		print tweet
	# 		if tweet['lang'].find('en') > -1:
	# 			tp.process(tweet['text'].translate(PUNCTUATION))
	# 			tokens = nltk.word_tokenize(tp.processed_text)
	# 			tokens = [t for t in tokens if t not in tp.stopwords]
	# 			tags = nltk.pos_tag(tokens)
	# 			important_words = [term for (term,tag) in tags if tag in IMPORTANT_POS]
	# 			corpora.extend(important_words)
	# 	fdist = nltk.FreqDist(corpora)
	# 	n = fdist.N()
	# 	mer = []
	# 	for k,v in fdist.iteritems():
	# 		if v > 4 and k != u'%s' % 'rt':
	# 			try:
	# 				mer.append({'text':str(k), 'size': float(v)/n})
	# 			except:
	# 				continue

	# 	with open('%s_bow.pkl' % user_name, 'wb') as handle:
	#   		pickle.dump(mer, handle)
	# 	print fdist
	# print fdist.most_common(50)
	# print fdist.most_common(50)
	names = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models/hidden_names.pkl')
	outdir = os.path.abspath(os.path.dirname(names))
	with open(names,'rb') as handler:
		NAMES = pickle.load(handler)
		screen_names = [v[1] for k,v in NAMES['HIDDEN'].iteritems()]
	for screen_name in screen_names:
		create_freq_dists (names, outdir,fake_screen_name=screen_name)


	create_freq_dists (names, outdir,fake_screen_name=None)