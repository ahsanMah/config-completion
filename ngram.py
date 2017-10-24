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


	# bigram_scores = sorted(bigram_scores, key=lambda item: item[1],reverse=True)
	# trigram_scores = sorted(trigram_scores, key=lambda item: item[1],reverse=True)

	# bigram_scores = bigram_scores[:5]
	# trigram_scores = trigram_scores[:5]

	# for result in bigram_scores: print result
	# for result in trigram_scores: print result

	return bigram_scores

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
	# total_runs = len(split_set)
	for train, test in split_set:
		print("Train: %s, Test: %s" % (train, test))
		train_set = []
		for _idx in train:
			train_set += train_list[_idx]
		model = train_ngram(train_set)
		model = create_mapping(model)
		#Get accuracy
		test_set = train_list[test[0]]
		run_score = score(model,test_set)
		print "Score: " + str(run_score)

def score(model, test_set):
	test_text = [token for token in test_set if "!" not in token]
	bigram_list = list(bigrams(test_text))

	total_bigrams = len(bigram_list)
	correct_predicitons = 0

	for (word, correct) in bigram_list:
		if word not in model:
			continue
		prediction = model[word]
		sorted(prediction, key=lambda item: item[1],reverse=True)
		# print word + "-->" + str(prediction)

		#if correct prediction in top 3
		filtered = list(filter(lambda x: (x[0]==correct), prediction[:3]))
		# print filtered
		if len(filtered) > 0:
			correct_predicitons += 1

	return float(correct_predicitons)/total_bigrams

def create_mapping(model):
	assoc_map = {}

	for _bigram in model:
		w1 = _bigram[0][0]
		w2 = _bigram[0][1]
		score = _bigram[1]
		if w1 not in assoc_map:
			assoc_map[w1] = []

		assoc_map[w1].append((w2,score))
	return assoc_map

start_time = time()
validate()
print "Time elapsed: {:.3f}".format((time()-start_time)) 
# train_ngram("token_dump.txt")