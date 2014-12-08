import nltk
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import csv

#Takes all tweets from the 'tweets' column of the .csv, and combines them into a list
raw_docs = []
with open(r'C:\Users\Mason\Desktop\Capstone\CSV\Tweets_collection.csv', 'rb') as f:
    reader = csv.reader(f)
    next(reader) # Ignore first row

    for row in reader:
        raw_docs.append(row[12]) #Only pulls data from the "text" column, each row is its own list

tokenized_docs = [word_tokenize(doc) for doc in raw_docs]

merged_list = sum(tokenized_docs, []) #combines each list of lists into one list


fdist1 = FreqDist(merged_list) #Performs frequency distribution on "tweets" list --> This part now works
print fdist1

#Writes the frequency distribution list to a csv file
with open(r'C:\Users\Mason\Desktop\Snippets\Freq_Tweets.csv','wb') as fp:
    writer = csv.writer(fp, quoting=csv.QUOTE_ALL)
    writer.writerows(fdist1.items())
