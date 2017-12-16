#! /usr/bin/python

import os as os
from time import time
import re, numpy
from sklearn.model_selection import LeaveOneOut
from nltk.util import bigrams, trigrams
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures

def train_ngram(train_set):
	
	train_text = train_set
	# train_text = []
	# for line in train_set.splitlines(True):
	# 	if "!" not in line:
	# 		for word in line.split(" "):
	# 			train_text.append(word)

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
	config_list = []
	for _dir in dirlist:
		if re.match(r'^fat|^ext.*|^repair_tests|.*snapshots$|^dep',_dir):
			continue

		token_file = dirname+"/"+_dir+"/token_dump.txt"
		config_list.append(_dir)

		raw_text = open(token_file).read()
		train_text = preprocess_data(raw_text)
		train_list.append(train_text)
	print config_list
	return train_list


def validate():
	dirname = "~/arc/configs/examples"
	train_list = getTokens(dirname)
	split_set = LeaveOneOut().split(train_list)
	total_runs = 0
	total_score = 0

	#Cross validating
	for train, test in split_set:
		print("Train: %s, Test: %s" % (train, test))
		train_set = []
		for _idx in train:
			train_set += train_list[_idx] #Concatenate all training data
		model = train_ngram(train_set)
		model = create_mapping(model)
		#Get accuracy
		test_set = train_list[test[0]]
		run_score = score(model,test_set)
		print "Score: " + str(run_score)
		total_score += run_score
		total_runs += 1
	print "Avg: " + str(total_score/total_runs)

def score(model, test_data):
	# for (key,val) in model.items(): print (key,val) 

	_debug = False

	bigram_list = list(bigrams(test_data))

	total_bigrams = 0 #len(bigram_list)
	incorrect = []
	not_found = []
	correct_predicitons = 0

	for (word, correct) in bigram_list:

		if re.match(r'.*\n.*', word): #Dont predict for end of line
			continue

		total_bigrams += 1
		word = word.strip()
		correct = correct.strip()

		if word not in model:
			not_found.append((word,correct))
			continue
		prediction = model[word]
		sorted(prediction, key=lambda item: item[1],reverse=True)

		#if correct prediction in top 3
		filtered = list(filter(lambda x: (x[0]==correct), prediction[:3]))
		# print filtered
		if len(filtered) > 0:
			correct_predicitons += 1
		else:
			incorrect.append((word,correct))
		
	if _debug:
		print "\tCorrect prerdiction not found"
		for (word,correct) in incorrect: print "\t\t", (word,correct)
		print "\tWords not found"
		for (word,correct) in not_found: print "\t\t", word

	return float(correct_predicitons)/total_bigrams

def create_mapping(model):
	assoc_map = {}

	for _bigram in model:
		w1 = _bigram[0][0]
		w2 = _bigram[0][1]
		score = _bigram[1]

		#Not predicting after line ends
		if re.match(r'.*\n.*', w1):
			continue

		if w1 not in assoc_map:
			assoc_map[w1] = []

		w2 = w2.strip()
		assoc_map[w1].append((w2,score))

	return assoc_map

def preprocess_data(text):
	train_text = []
	text = re.sub(r'((255|0)\.?){4}',"SUBNET",text)
	text = re.sub(r'(\d{1,3}\.?){4}',"IPADDRESS",text)
	# print text
	for line in text.splitlines(True):
		if "!" not in line:
			for word in line.split(" "):
				if len(word) > 0:
					train_text.append(word)
	return train_text

start_time = time()
validate()
print "Time elapsed: {:.3f}".format((time()-start_time)) 
# train_ngram("token_dump.txt")