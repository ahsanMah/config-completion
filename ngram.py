#! /usr/bin/python

import os as os
import re, numpy, sys, random, csv
import multiprocessing
from sklearn.model_selection import LeaveOneOut
from nltk.util import bigrams, trigrams
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from collections import defaultdict

###### Declaring constants #########
RANDOM_SEED = 42
SAMPLE_NUM = 0
NGRAM_SIZE = 0
NUM_PREDICTIONS = 0
TRAIN_DATA = []
TRAIN_SET = []
STANZA_DATA = {}

use_stanzas = False
_debug = False
_debugLong = False

def run(args, sample = 0, ngram = 3, predictions = 3, test_dir = None):

	global SAMPLE_NUM, NGRAM_SIZE, NUM_PREDICTIONS, TRAIN_DATA, TRAIN_SET, STANZA_DATA, _debug, _debugLong, use_stanzas

	SAMPLE_NUM = sample
	NGRAM_SIZE = ngram
	NUM_PREDICTIONS = predictions	
	
	dirname = args[1]
	# TODO: Use argument parsers
	# if len(args) > 2:
	# 	option = args[2]
	# 	use_stanzas = re.match(r'-.*s.*', option)
	# 	_debugLong = re.match(r'-.*dL.*', option)
	# 	_debug = re.match(r'-.*d.*', option)

	print "Directory: %s" % dirname

	dirlist, TRAIN_DATA, STANZA_DATA = getTokens(dirname)

	test_data = [] # If test data provided, all of TRAIN_DATA is used to train model
	if test_dir:
		dirlist, test_data, _ = getTokens(test_dir)
		for data in TRAIN_DATA:
			TRAIN_SET += data

	print "Sample size: %d" % len(TRAIN_DATA)
	print "Ngram size: %d" % NGRAM_SIZE
	if use_stanzas:
		print "Using Stanza Model"

	# dump_ngram_map()

	results = validate(test_data)

	return map(lambda x: list(x), zip(dirlist, results))



'''
Returns a sequence of (ngram, score) pairs
ordered from highest to lowest score
'''
def train_ngram(train_set):
	
	train_text = train_set
	bigram_scores = []
	trigram_scores = []

	try:

		#Getting bigrams
		bi_finder = BigramCollocationFinder.from_words(train_text)
		tri_finder = TrigramCollocationFinder.from_words(train_text)

		#Scoring each ngram using likelihood ratios
		bigram_scores = bi_finder.score_ngrams(BigramAssocMeasures.likelihood_ratio)
		trigram_scores = tri_finder.score_ngrams(TrigramAssocMeasures.likelihood_ratio)

	except Exception as e:
		print e
		# print train_set
		print "Insufficient data to build (stanza) model"

	return bigram_scores, trigram_scores

def getTokens(dirname):
	dirname = os.path.expanduser(dirname) 
	dirlist = os.listdir(dirname)

	print dirlist

	#Numpy RandomState maintains consistency across devices
	prng = numpy.random.RandomState(RANDOM_SEED)
	if SAMPLE_NUM > 0 and SAMPLE_NUM <= len(dirlist):
		dirlist = prng.choice(dirlist, SAMPLE_NUM)

	train_data = []
	stanza_train_data = defaultdict(list)
	config_list = []

	for _dir in dirlist:

		# Problematic directories
		# Most are unrealistic examples of configurations 
		# and therefore confound the model
		if re.match(r'^fat|^ext.*|^repair_tests|.*snapshots$|^dep|.*\.DS',_dir):
			print _dir
			continue

		token_file = dirname+"/"+_dir
		# print token_file
		config_list.append(_dir.replace(".txt",""))

		with open(token_file) as f:
			raw_text = f.read()
			train_text = preprocess_data(raw_text)
			if use_stanzas:
				get_stanzas(raw_text, stanza_train_data)
			train_data.append(train_text)
	# print config_list
	return config_list, train_data, stanza_train_data

#Wrapper function to allow to be used with map operator in Pool
#FIXME: Builds ngram every time
def run_analysis(test_set):
	return single_analysis(TRAIN_SET,test_set)

def single_analysis(train_set, test_set):
	bigram_model, trigram_model = train_ngram(train_set)
	bimodel = create_mapping(bigram_model)
	trimodel = create_mapping(trigram_model)

	test_ngram_list = list(bigrams(test_set) if NGRAM_SIZE==2 else trigrams(test_set))
	
	#Get accuracy
	run_score = score(bimodel,trimodel,test_ngram_list)
	
	if _debug:
		print "Score: " + str(run_score)

	return run_score

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
	test_set = train_list[test[0]]

	return single_analysis(train_set, test_set)


def validate(test_data):
	
	dataset = test_data
	analysis_func = run_analysis 

	if not test_data:
		dataset = LeaveOneOut().split(TRAIN_DATA)
		analysis_func = crossvalidate

	run_score = []

	if not _debug:
		#Making thread workers
		pool = multiprocessing.Pool(multiprocessing.cpu_count())
		run_score = pool.map(analysis_func, dataset)

		#Closing threads
		pool.close()
		pool.join()
	else:
		for train_test in dataset:
			run_score.append(analysis_func(train_test))

	total_score = sum(run_score)
	total_runs = len(run_score)
	print "Accuracy: %.4f" % (total_score/total_runs)
	return run_score



def score(bimodel, trimodel, ngram_list):

	stanza_map = build_stanza_models()
	# print stanza_map

	total_bigrams = 0 #len(ngram_list)
	incorrect = set()
	not_found = set()
	correct_predicitons = 0
	current_stanza = ""

	for ngram in ngram_list:

		# Don't predict for end of line
		if re.match(r'.*\n.+', "".join(ngram)):
			# If not start of new line or end of comment
			if (not re.match(r'.*\n', ngram[0])) or re.match(r'.*\n', ngram[1]):
				# print "Skipping", ngram
				continue

			# Try to predict bigram if beginning of a new line
			ngram = ngram[1:]

		#Defaults to whatever the length of the ngram is
		ngram_length = len(ngram)
		ngram_model = trimodel if ngram_length == 3 else bimodel

		ngram = tuple(map(lambda x: x.strip(), ngram))
		prefix = ngram[:-1]
		correct = ngram[-1]
		stanza_candidate = prefix[0].strip()

		total_bigrams += 1

		if prefix not in ngram_model:
			# print "Not Found", prefix
			not_found.add((prefix,correct))
			continue

		stanza_start = False
		if stanza_candidate in STANZA_DATA:
			stanza_start = True
			current_stanza = stanza_candidate

		# Use stanza specific model if available
		# If start of stanza line, use default model to predict
		if use_stanzas and current_stanza in stanza_map and not stanza_start:
			# print current_stanza
			
			# Choose bigram or trigram according to (ngram_size - offset) into array
			model_idx = ngram_length-2
			ngram_model = stanza_map[current_stanza][model_idx]
		
		prediction = ngram_model.get(prefix)

		# Filter out predictions that match the correct answer
		filtered = []
		if prediction != None:
			filtered = list(filter(lambda x: (x[0]==correct), prediction[:NUM_PREDICTIONS]))

		# if len(filtered) == 0:
		# 	bi_prefix = prefix[-1]
		# 	prediction = trimodel[bi_prefix]
		# 	sorted(prediction, key=lambda item: item[1],reverse=True)
		# 	# Filter out predictions that match the correct answer
		# 	filtered = list(filter(lambda x: (x[0]==correct), prediction[:NUM_PREDICTIONS]))
		
		if len(filtered) > 0:
			correct_predicitons += 1
			# TODO: Compare with tab completion results
		else:
			# print "unable to predict ", ngram
			# print "using model ->" , ngram_model
			guess = "Null"
			if prediction != None:
				guess = tuple(map(lambda (_word,_prob): _word, prediction[:NUM_PREDICTIONS+5]))
			incorrect.add((prefix,correct, guess))
		
	if _debugLong:
		print "\t Unable to correctly predict: %d" % len(incorrect)
		for (word,correct, prediction) in incorrect: 
			print "\t\t (%s,%s) -> %s" % (word,correct, prediction) #+ prediction
		
		print "\t Phrases not present in model: %d" % len(not_found)
		for (word,correct) in not_found: print "\t\t", word

	# print bimodel.get(('ip',))

	return float(correct_predicitons)/total_bigrams

def create_mapping(model):
	assoc_map = {}
	size = len(model[0][0]) #Size of ngram

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
			if len(word) > 0 and word != "\n":		
				train_text.append(word)

	return train_text


def dump_ngram_map():
	train_set = [token for wordlist in TRAIN_DATA for token in wordlist]
	bigram_model, trigram_model = train_ngram(train_set)
	trimodel = create_mapping(trigram_model,3)	
	# print trigram_model
	output_file = "ngram_dump.csv"

	data = []
	for prefix in trimodel:
		w1,w2 = prefix
		results = [w1,w2]
		for (word,accuracy) in trimodel[prefix][:NUM_PREDICTIONS]:
			results.append(word)
		data.append(results)

	with open(output_file, "w+") as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(["First", "Second", "Prediction"])
		writer.writerows(data)

def get_stanzas(raw_text, stanza_map = defaultdict(list)):

	stanza_list = raw_text.split("!")
	
	for stanza in stanza_list:
		data = preprocess_data(stanza)
		if len(data)>0:#and data[0] in ["router", "interface", "ip", "route-map"]:
			stanza_map[data[0].strip()] += data[1:]

	return stanza_map

'''
The NLTK package breaks when all the tokens are the same as it cannot score them
For trigram model, we need at least two different tokens

	# tri_finder = TrigramCollocationFinder.from_words(["a","b","a", "a"])
	# trigram_scores = tri_finder.score_ngrams(TrigramAssocMeasures.likelihood_ratio)
	# print trigram_scores

Model is dict mapping from stanza name to ngrams scores for tokens that fall within the given stanza
Returns empty list if stanza doesn't exist

'''

def build_stanza_models():

	stanza_map = defaultdict(list)

	for stanza in STANZA_DATA:
		bigrams, trigrams = train_ngram(STANZA_DATA[stanza])

		if len(trigrams) > 0:
			stanza_map[stanza].append(create_mapping(bigrams))
			stanza_map[stanza].append(create_mapping(trigrams))
	# print stanza_map
	return stanza_map


if __name__ == "__main__":
	run(sys.argv)












