#! /usr/bin/python

import os as os, sys, re
from time import time

def dumptext(_dir):
	if re.match(r'^fat|^ext.*|^repair_tests|.*snapshots$|^dep',_dir):
		return
	raw_text = ""
	currdir = dirname+_dir
	filelist = os.listdir(currdir)
	for file in filelist:
		if re.match(r'.*\.cfg$', file):
			filename = currdir + "/" + file
			with open(filename, 'r') as f:
				raw_text += f.read()

	with open(currdir + "/tokendump.txt", 'w') as f:
		f.write(raw_text)

start_time = time()

dirname  = sys.argv[1]

dirname = os.path.expanduser(dirname) 
dirlist = os.listdir(dirname)

for _dir in dirlist:
	dumptext(_dir)

print "Elapsed Time: {:.3f}".format((time()-start_time)) 
	# config_list.append(_dir)

