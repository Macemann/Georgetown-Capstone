'''
This is a script to create the time series analysis outputs

__author__ : Ryan Stephany
__purpose__: Georgetown Analytics
'''


import os
import pickle
import itertools
import pandas as pd 
from pandas import DataFrame, Series
from nltk import bigrams
import numpy as np
from pymongo import MongoClient
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
from Processors import TextPreprocessor
from Graphml_creator2 import get_user_by_user_name
from mann_kendall import MannKendall
import matplotlib.pyplot as plt 


IMPORTANT_WORDS = ('terror','terrorists','terrorin','airstrikes','muslim','muslims','war','isis','jihad','beheading',
	'kill','killed','khorasan','taliban','beseige','mujahid','islamicstate','baghdadi',
	'mujahideen','mujahireen','caliphate','fight','fighter','fighting','isil','executed','assualted','raids',
	'disbelievers','prisoner','prisoners','islamic','muslimrebels''khalifa')
INTERMEDIATES = ['join','good','like','state','help','recruit','british','usa','austrailia']



MODELS_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))),'models')
with open(os.path.join(MODELS_PATH,'hidden_names.pkl'),'rb') as handler:
	HIDDEN = pickle.load(handler)	

STATIC_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))),'static')



if __name__ == '__main__':
	conn = MongoClient()
	db = conn['GtownTwitter_PROD']
	tweets_col = db['tweets_collection']
	tp = TextPreprocessor()

	events = DataFrame.from_csv(os.path.join(STATIC_PATH,'events.csv'),index_col='Date')
	events = events.drop('Iraq', 1)
	events = events.drop('Syria',1)
	events = events.drop('Tweets',1)

	imp_events = events['Events']
	imp_events = imp_events.dropna()
	imp_events = imp_events.index.values


	events = events.drop('Events',1)
	cor = 0
	r = 0
	m = 0
	p = 0

	output = {}

	# Iterate over users
	for user,fakes in HIDDEN['HIDDEN'].iteritems():
		user = get_user_by_user_name(db, user)
		user_scores = []
		n=0
		dts = set([])

		pd_dict = {}

		# Iterate over user tweets sorted by date
		for tweet in tweets_col.find({'user_id': user['_id']}).sort('created_at'):
			if tweet['created_at'] not in dts:
				tp.process(tweet['text'])

				date = tweet['created_at'].date()
				if n==0:
					start_date = tweet['created_at'].date()
				else:
					end_date = tweet['created_at'].date()

				# Score the tweet based on if tweet contains bad words
				# Score is n++ for each bad word found
				score = 0
				for word in tp.tokens:
					if word in IMPORTANT_WORDS:
						score+=1

				# Add to the score if tweet contains bigrams with additional intermediate terms
				# Score adds 10 for each bigram found
				tweet_bigrams = bigrams(tp.processed_text)
				for bg in tweet_bigrams:
					if bg[0] in IMPORTANT_WORDS and bg[1] in IMPORTANT_WORDS:
						score+=1

					if bg[0] in IMPORTANT_WORDS and bg[1] in  INTERMEDIATES:
						score+=10
					if bg[1] in IMPORTANT_WORDS and bg[0] in  INTERMEDIATES:
						score+=10					

				# keep sequential scores for each day
				if date in pd_dict.keys():
					score = score+pd_dict[date]
					user_scores[-1] = score
					pd_dict[date] = score
				else:
					pd_dict[date] = score
					user_scores.append(score)

				dts.add(tweet['created_at'])

		# Check is scores were calculated
		if len(dts) > 0:	

			# Create the Index based on Date
			date_index = pd.DatetimeIndex(sorted(pd_dict.keys()))
			# Create the dataframe
			ts = pd.DataFrame(user_scores, index=date_index, columns=['Tweet Score'])
			ts.index.name = 'Date'
			# Reindex the date index to include any missing dates
			ts = ts.reindex(pd.date_range(min(date_index), max(date_index)),fill_value=0)

			# Create the Scores Graph
			fig1 = plt.figure()
			ts.plot()
			plt.savefig(os.path.join(STATIC_PATH,'%s_tweet_scores.png' % fakes[-1]))
			plt.close(fig1)	

			# Add Airstrike data into the dataset
			merged = ts.join(events)


			# Find the first non missing data to slice the dataframe where airstrikes and tweet scores overlap
			air_inds = np.where(merged['Airstrikes'].notnull())[0]
			score_inds = np.where(merged['Tweet Score'].notnull())[0]
			for i in air_inds:
				if i in score_inds:
					break
			# Slice the dataframe where data overlaps
			sliced = merged._slice(slice(i, len(merged)))
			
			# Calculate the Pearson Correlation between Tweet Score and Airstrikes
			r = sliced['Tweet Score'].corr(sliced['Airstrikes'])
			print 'Pearson Correlation: Tweet Score|# Air Strikes --- %f' % r
			if r >= 0.7:
				cor = 'Very Strong positive relationship'
			elif r >= 0.4:
				cor = 'Strong positive relationship'
			elif r >= 0.3: 
				cor = 'Moderate positive relationship'
			elif r >= 0.2:
				cor = 'Weak positive relationship'
			elif r >= -.19:
				cor = 'No or negligable relationship'
			elif r <= -.70:
				cor = 'Very Strong negative relationship'
			elif r <= -.40:
				cor = 'Strong negative relationship'
			elif r <= -.30:
				cor = 'Moderate negative relationship'
			elif r <= -.20:
				cor = 'Weak negative relationship'

			print cor

			# Test the users sequential tweet scores using the Mann-Kendall Statistic
			mk = MannKendall(user_scores)
			h,m,p = mk.test()
			print fakes[-1],h,m,p

			# Create the graph for the scores and the airstrikes
			fig = plt.figure()
			ax = sliced.plot()
			ymin, ymax = ax.get_ylim()
			# Add vertical lines where the key events occurred
			ax.vlines(x=imp_events, ymin=ymin, ymax=ymax-1, color='r',linewidth=5)
			plt.savefig(os.path.join(STATIC_PATH,'%s_corr.png' % fakes[-1]))
			plt.close(fig)

		# Output to a dictionary
		output[fakes[-1]] = {}
		output[fakes[-1]]['Pearson Correlation'] = cor
		output[fakes[-1]]['Pearson Correlation Statistic'] = r
		output[fakes[-1]]['Trend'] = h
		if h:
			if m == '+':
				m = 'Increasing'
			else:
				m = 'Decreasing'
		else:
			m = 'N/A'
		output[fakes[-1]]['Increasing or Decreasing Trend'] = m
		output[fakes[-1]]['P Value'] = p

		# Write the dictionary to a pickle
		with open(os.path.join(MODELS_PATH,'%s_ts.pkl' % fakes[-1]),'wb') as handler:
			pickle.dump(output, handler)


