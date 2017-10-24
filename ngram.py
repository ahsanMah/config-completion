#! /usr/bin/python

import os as os
from time import time
import re, numpy
from sklearn.model_selection import LeaveOneOut
from nltk.util import bigrams, trigrams
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures

def train_ngram(train_set):
	# train_file = open(filename).read().split()
	train_text = [token for token in train_set if "!" not in token]

	#Getting bigrams
	bi_finder = BigramCollocationFinder.from_words(train_text)
	tri_finder = TrigramCollocationFinder.from_words(train_text)
	bi_finder.apply_freq_filter(3)

	#Scoring each ngram using likelihood ratios
	bigram_scores = bi_finder.score_ngrams(BigramAssocMeasures.likelihood_ratio)
	trigram_scores = tri_finder.score_ngrams(TrigramAssocMeasures.likelihood_ratio)


	bigram_scores = sorted(bigram_scores, key=lambda item: item[1],reverse=True)
	trigram_scores = sorted(trigram_scores, key=lambda item: item[1],reverse=True)

	bigram_scores = bigram_scores[:5]
	trigram_scores = trigram_scores[:5]

	for result in bigram_scores: print result
	for result in trigram_scores: print result

	return

def getTokens(dirname):
	dirname = os.path.expanduser(dirname) 
	dirlist = os.listdir(dirname)
	train_list = []
	for _dir in dirlist:
		if re.match(r'^fat|^ext.*|^repair_tests|.*snapshots$|^dep',_dir):
			continue
		token_file = dirname+"/"+_dir+"/token_dump.txt"

		train_text = open(token_file).read().split()
		train_list.append(train_text)
	return train_list


def validate():
	dirname = "~/arc/configs/examples"
	train_list = getTokens(dirname)
	split_set = LeaveOneOut().split(train_list)
	for train, test in split_set:
		print("Train: %s, Test: %s" % (train, test))
		train_set = []
		for _idx in train:
			train_set += train_list[_idx]
		train_ngram(train_set)
		break
		
start_time = time()
validate()
print "Time elapsed: {:.3f}".format((time()-start_time)) 
# train_ngram("token_dump.txt")