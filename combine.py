#! /usr/bin/python

import os as os, sys, re
import numpy as np
from time import time
from multiprocessing.dummy import Pool as ThreadPool



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
	
	# Substitutes each matching regex with the corresponding
	# replacement using the callback function
	cleaned_text = MATCHER.sub(get_regex_match, text)
	cleaned_text = re.sub('(!.*\n)', "", cleaned_text)

	return cleaned_text

def dumptext(dirname):
	if re.match(r'^fat|^ext.*|^repair_tests|.*snapshots$|^dep', dirname):
		return
	raw_text = ""
	currdir = dirpath + "/" + dirname

	if os.path.isdir(currdir):

		filelist = filter(lambda x: not re.match(r'.*\.txt$', x), os.listdir(currdir))
		
		if FILENUM:
			filelist = filelist[:FILENUM]
		
		for file in filelist:
			filename = currdir + "/" + file
			with open(filename, 'r') as f:
				raw_text += f.read()
	else:
		filename = currdir
		with open(filename, 'r') as f:
				raw_text += f.read()

	with open(outputdir + "/" + dirname +  ".txt", 'w') as f:
		f.write(preprocess_data(raw_text))

def getConfigStats(configname):
	filename = dirpath + "/" + configname
	raw_text = ""
	with open(filename, 'r') as f:
		raw_text += f.read()
	# raw_text = preprocess_data(raw_text)
	total_lines = raw_text.split("\n")
	# num_tokens = raw_text.split(" ")
	return len(total_lines)


########### Start Running #################
start_time = time()

dirpath  = sys.argv[1]
outputdir = sys.argv[2]
FILENUM = int(sys.argv[3]) if len(sys.argv) > 3 else None

dirpath = os.path.expanduser(dirpath)
outputdir = os.path.expanduser(outputdir)
dirlist = filter(lambda x: not re.match(r'.*\.txt|(\.DS_Store)', x), os.listdir(dirpath))

REPLACEMENTS = {'((255|0)\.?){4}' : "SUBNET",
				'(\d{1,3}\.?){4}' : "IPADDRESS",
				'(interface [a-zA-z]*)[^a-zA-z]*\s' : (lambda iface: iface+"#ID\n"),
				'description (\\b.*\\b)' : "description DESCRIPTION"
				}
REGEX_KEYS = REPLACEMENTS.keys()
COMPILED_KEYS = [re.compile(regex) for regex in REGEX_KEYS]

# Combines all phrases to be replaced into one giant regex
# There's a bug in Python taht prevents the following regex from being compiled
# r"\b?%s\b?" % r"\b?|\b?".join(REGEX_KEYS)
MATCHER = re.compile(r"\b%s\b" % r"\b|\b".join(REGEX_KEYS))

print dirlist

#Making thread workers
pool = ThreadPool(8)
pool.map(dumptext, dirlist)
# results = pool.map(getConfigStats, dirlist)

#Closing threads
pool.close()
pool.join()

# print results
# print np.mean(results)

print "Elapsed Time: {:.3f}".format((time()-start_time)) 