from nltk.corpus import names
import random
import nltk
import os
import nameparser


class GenderPredictor(object):
	def __init__ (self):
		self.featuresets 	= self.create_featuresets()
		self.classifier 	= self.create_classifier()


	def gender_features(self, word):
		return {'last_letter': word[-1]}

	def create_featuresets(self):
		'''
		Create featuresets of name, gender based on the names corpora
		'''
		train_names = ([(name,'male') for name in names.words('male.txt')] +
				 [(name,'female') for name in names.words('female.txt')])

		random.shuffle(train_names)
		return [(self.gender_features(n), g) for (n,g) in train_names]

	def create_classifier (self):
		'''
		Trains a NaiveBayesClassifier based on the training and test sets
		'''
		train_set, test_set = self.featuresets[500:], self.featuresets[:500]
		return nltk.NaiveBayesClassifier.train(train_set)

	def predict_gender (self, full_name):
		'''
		Returns the predicted gender of a first name based on the classifier
		'''
		try:
			name = nameparser.HumanName(full_name)
			return self.classifier.classify(self.gender_features(name.first))
		except:
			print 'Unable to Predict : %s ' % full_name


if __name__ == '__main__':
	g = GenderPredictor()

	# 1 Test
	# This is a unittest checking the users from our project
	# If you don't have data loaded yet try the second test below and
	# comment out this group of code
	import pymongo
	from pymongo import MongoClient
	conn 	= MongoClient()
	db 		= conn['GtownTwitter_PROD']
	users 	= db.users_collection
	for doc in users.find():
		name = doc['name']
		print name, g.predict_gender(name)

	# 2 Test
	# This test checks 1 given name
	name = 'Ryan Stephany'
	print name, g.predict_gender(name)
