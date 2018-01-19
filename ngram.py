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
	dirlist = os.listdir(dirname)[:SAMPLE_NUM]
	
	# if len(dirlist) > SAPMLE_NUM:
	# 	dirlist = random.sample(dirlist, SAPMLE_NUM)

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
	print config_list
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
	# model = create_mapping(bigram_model, 2)
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
		#Making thread wordkers
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
	print "Avg: " + str(total_score/total_runs)

def score(model, ngram_list):
	# for (key,val) in model.items(): print (key,val) 
	

	total_bigrams = 0 #len(ngram_list)
	incorrect = []
	not_found = []
	correct_predicitons = 0

	for ngram in ngram_list:

		if re.match(r'.*\n.+', "".join(ngram)): #Dont predict for end of line
			# print prefix
			continue

		ngram = tuple(map(lambda x: x.strip(), ngram))

		prefix = ngram[:NGRAM_SIZE-1]
		correct = ngram[-1]


		total_bigrams += 1
		if prefix not in model:
			not_found.append((prefix,correct))
			continue

		prediction = model[prefix]
		sorted(prediction, key=lambda item: item[1],reverse=True)

		# Filter out predictions that match the correct answer
		filtered = list(filter(lambda x: (x[0]==correct), prediction[:NUM_PREDICTIONS]))
		
		if len(filtered) > 0:
			correct_predicitons += 1
		else:
			# print filtered
			incorrect.append((prefix,correct, map(lambda (_word,_prob): _word, prediction[:5])))
		
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


''' Callback function for returning the appropriate substitution 
	for any regex that is matched while preprocesisng data
'''
def get_regex_match(matchObj):
	phrase = matchObj.group(0)
	replacement = "<REMOVED>"

	for regex_num, regex in enumerate(COMPILED_KEYS):
		if regex.match(phrase):
			replacement = REPLACEMENTS[REGEX_KEYS[regex_num]]
			break
	
	if callable(replacement):
		replacement = replacement(matchObj.group(1))

	return replacement


def preprocess_data(text):
	train_text = []

	matching_regex = re.compile(r"\b%s\b" % r"\b|\b".join(REGEX_KEYS))
	text = matching_regex.sub(get_regex_match, text)
	# print text

	for line in text.splitlines(True):
		if "!" not in line:
			for word in line.split(" "):
				if len(word) > 0:
					train_text.append(word)
	return train_text


############ Start Running ################
start_time = time()

dirname = sys.argv[1]

NUM_PREDICTIONS = 3
NGRAM_SIZE = 3
SAMPLE_NUM = 10

_debug = len(sys.argv) > 2 and re.match(r'-d.?', sys.argv[2])
_debugLong = len(sys.argv) > 2 and re.match(r'-dL', sys.argv[2])


REPLACEMENTS = {'((255|0)\.?){4}' : "SUBNET",
				'(\d{1,3}\.?){4}' : "IPADDRESS",
				'(interface [a-zA-z]*)[^a-zA-z]*\s' : (lambda iface: iface+"#ID\n"),
				'description (\\b.*\\b)' : "description DESCRIPTION"
				}
REGEX_KEYS = REPLACEMENTS.keys()
COMPILED_KEYS = [re.compile(regex) for regex in REGEX_KEYS]

# Makes things easier for using pool map later on
TRAIN_DATA = getTokens(dirname)
validate()

print "Time elapsed: {:.3f}".format((time()-start_time)) 
# train_ngram("token_dump.txt")