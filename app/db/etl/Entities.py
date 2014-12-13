import nltk
from nltk.corpus import stopwords


class EntityExtractor (object):
	'''
	Class used to extract Named Entities from a string
	'''
	def __init__ (self, tweet):
		self.tweet = tweet
		self.text = tweet['text']
		self.lang = tweet['lang']
		self.bool = tweet['text'] and tweet['lang'].find('en') > -1
		self.tokens, self.tags = self.genTokensTags()

	def genTokensTags (self, rem_stop_words=False):
		'''
		Generates tokens --> tokens removes punctuation and is a list of words
		Generates tags --> list of tuples for each word and the type of speech of each word
		'''
		if self.bool:
			text = self.text.replace('#','').replace('RT ', ' ')
			if rem_stop_words: 
				text = ' '.join([word for word in text.split() if word not in stopwords.words('english')])
			sentences = nltk.sent_tokenize(text)
			tokens = [nltk.word_tokenize(sentence) for sentence in sentences]
			tags = [nltk.pos_tag(token) for token in tokens]
			return tokens, tags
		return None, None
		
	def get_entities (self):
		if self.tags:
			entities = []
			chunks = nltk.batch_ne_chunk(self.tags, binary=True)
			for tree in chunks:
				entities.extend(self.extractEntities(tree))
			return entities
		return []

	def get_entity_stems (self, words):
		porter = nltk.PorterStemmer()
		return [porter.stem(w) for w in words]
			
	def extractEntities (self, tree):
		'''
		Gets the Proper Nouns from the tags
		'''
		ents = []
		if hasattr(tree,'node') and tree.node:
			if tree.node == 'NE':
				ents.append(' '.join([child[0] for child in tree]))
			else:
				for child in tree:
					if child:
						ents.extend(self.extractEntities(child))
		return ents


if __name__ == '__main__':
	tweet = {'text': 'This is an example tweet made by Ryan Stephany on Ubuntu using Python','lang': 'en'}
	entity_extractor = EntityExtractor(tweet)
	entities = entity_extractor.get_entities()
	print entities
	stems = entity_extractor.get_entity_stems(entities)
	print stems

