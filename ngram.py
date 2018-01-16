#! /usr/bin/python

import os as os
from time import time
import re, numpy, sys
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

	return bigram_scores

def getTokens(dirname):
	dirname = os.path.expanduser(dirname) 
	dirlist = os.listdir(dirname)
	train_list = []
	config_list = []
	for _dir in dirlist:

		# Problematic directories
		# Most are not realistic examples of configurations 
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
	train_list = train_data
	
	#Concatenate all training data
	train_set = []
	for _idx in train:
		train_set += train_list[_idx]

	model = train_ngram(train_set)
	model = create_mapping(model)
	
	#Get accuracy
	test_set = train_list[test[0]]
	run_score = score(model,test_set)
	
	if _debug:
		print("Train: %s, Test: %s" % (train, test))
		print "Score: " + str(run_score)

	return run_score


def validate():
	
	split_set = LeaveOneOut().split(train_data)
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

def score(model, test_data):
	# for (key,val) in model.items(): print (key,val) 

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
		filtered = list(filter(lambda x: (x[0]==correct), prediction[:NUM_PREDICTIONS]))
		if len(filtered) > 0:
			correct_predicitons += 1
		else:
			# print filtered
			incorrect.append((word,correct, prediction[:5]))
		
	if _debugLong:
		print "\tCorrect prediction not found"
		for (word,correct, prediction) in incorrect: print "\t\t", (word,correct) , "->", prediction
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

NUM_PREDICTIONS = 5
dirname = sys.argv[1]

_debug = len(sys.argv) > 2 and re.match(r'-d.?', sys.argv[2])
_debugLong = len(sys.argv) > 2 and re.match(r'-dL', sys.argv[2])


REPLACEMENTS = {'((255|0)\.?){4}' : "SUBNET",
				'(\d{1,3}\.?){4}' : "IPADDRESS",
				'(interface [a-zA-z]*)[^a-zA-z]*\s' : (lambda iface: iface+"#ID "),
				'description (\\b.*\\b)' : "description DESCRIPTION"
				}
REGEX_KEYS = REPLACEMENTS.keys()
COMPILED_KEYS = [re.compile(regex) for regex in REGEX_KEYS]

train_data = getTokens(dirname)
validate()

print "Time elapsed: {:.3f}".format((time()-start_time)) 
# train_ngram("token_dump.txt")