#! /usr/bin/python

import os as os
from time import time
import re, numpy, sys, random
from multiprocessing import Pool as ThreadPool
from sklearn.model_selection import LeaveOneOut
from nltk.util import bigrams, trigrams
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures

def train_ngram(train_set):
	
	train_text = train_set

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

	return bigram_scores, trigram_scores

def getTokens(dirname):
	dirname = os.path.expanduser(dirname) 
	dirlist = os.listdir(dirname)#[:SAMPLE_NUM]
	
	if len(dirlist) > SAMPLE_NUM:
		dirlist = random.sample(dirlist, SAMPLE_NUM)

	train_list = []
	config_list = []
	for _dir in dirlist:

		# Problematic directories
		# Most are unrealistic examples of configurations 
		# and therefore confound the model
		if re.match(r'^fat|^ext.*|^repair_tests|.*snapshots$|^dep',_dir):
			continue

		token_file = dirname+"/"+_dir
		config_list.append(_dir.replace(".txt",""))

		raw_text = open(token_file).read()
		train_text = preprocess_data(raw_text)
		train_list.append(train_text)
	# print config_list
	return train_list

	#Cross validating
def crossvalidate(train_test):
	train,test = train_test
	train_list = TRAIN_DATA
	
	if _debug:
		print("Train: %s, Test: %s" % (train, test))

	#Concatenate all training data
	train_set = []
	for _idx in train:
		train_set += train_list[_idx]

	bigram_model, trigram_model = train_ngram(train_set)
	model = bigram_model if NGRAM_SIZE==2 else trigram_model
	model = create_mapping(model,NGRAM_SIZE)
	
	test_set = train_list[test[0]]
	test_ngram_list = list(bigrams(test_set) if NGRAM_SIZE==2 else trigrams(test_set))
	
	#Get accuracy
	run_score = score(model,test_ngram_list)
	
	if _debug:
		print "Score: " + str(run_score)

	return run_score


def validate():
	
	split_set = LeaveOneOut().split(TRAIN_DATA)
	run_score = []

	if not _debug:
		#Making thread workers
		pool = ThreadPool(8)
		run_score = pool.map(crossvalidate, split_set)

		#Closing threads
		pool.close()
		pool.join()
	else:
		for train_test in split_set:
			run_score.append(crossvalidate(train_test))

	total_score = sum(run_score)
	total_runs = len(run_score)
	print "Accuracy: %.4f" % (total_score/total_runs)

def score(model, ngram_list):
	# for (key,val) in model.items(): print (key,val) 
	
	total_bigrams = 0 #len(ngram_list)
	incorrect = set()
	not_found = set()
	correct_predicitons = 0

	for ngram in ngram_list:

		# Don't predict for end of line
		if re.match(r'.*\n.+', "".join(ngram)):
			continue

		ngram = tuple(map(lambda x: x.strip(), ngram))

		prefix = ngram[:NGRAM_SIZE-1]
		correct = ngram[-1]


		total_bigrams += 1
		if prefix not in model:
			not_found.add((prefix,correct))
			continue

		prediction = model[prefix]
		sorted(prediction, key=lambda item: item[1],reverse=True)

		# Filter out predictions that match the correct answer
		filtered = list(filter(lambda x: (x[0]==correct), prediction[:NUM_PREDICTIONS]))
		
		if len(filtered) > 0:
			correct_predicitons += 1
		else:
			# print filtered
			incorrect.add((prefix,correct, tuple(map(lambda (_word,_prob): _word, prediction[:5]))))
		
	if _debugLong:
		print "\t Unable to correctly predict: %d" % len(incorrect)
		for (word,correct, prediction) in incorrect: 
			print "\t\t (%s,%s) -> %s" % (word,correct, prediction) #+ prediction
		
		print "\t Phrases not present in model: %d" % len(not_found)
		for (word,correct) in not_found: print "\t\t", word

	return float(correct_predicitons)/total_bigrams

def create_mapping(model, size):
	assoc_map = {}

	for (ngram, score) in model:
		prefix = ngram[:size-1]
		prediction = ngram[-1]

		#Not predicting after line ends
		if re.match(r'.*\n.*', "".join(prefix)):
			continue

		if prefix not in assoc_map:
			assoc_map[prefix] = []

		prediction = prediction.strip()
		assoc_map[prefix].append((prediction,score))

	return assoc_map


def preprocess_data(text):
	
	# NLTK expects lists of words to form ngrams
	train_text = []
	for line in text.splitlines(True): 
		for word in line.split(" "):
			if len(word) > 0:		
				train_text.append(word)

	return train_text


############ Start Running ################
start_time = time()

random.seed(7)

dirname = sys.argv[1]

NUM_PREDICTIONS = 3
NGRAM_SIZE = 2
SAMPLE_NUM = 20

_debug = len(sys.argv) > 2 and re.match(r'-d.?', sys.argv[2])
_debugLong = len(sys.argv) > 2 and re.match(r'-dL', sys.argv[2])

print "Directory: %s" % dirname
print "Sample size: %d" % SAMPLE_NUM
print "Ngram size: %d" % NGRAM_SIZE

# Makes things easier for using pool map later on
TRAIN_DATA = getTokens(dirname)
validate()

print "Time elapsed: {:.3f}".format((time()-start_time)) 