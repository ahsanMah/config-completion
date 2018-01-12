#! /usr/bin/python

import os as os, sys, re
from time import time
from multiprocessing.dummy import Pool as ThreadPool

def dumptext(dirname):
	if re.match(r'^fat|^ext.*|^repair_tests|.*snapshots$|^dep', dirname):
		return
	raw_text = ""
	currdir = dirpath + "/" + dirname
	filelist = os.listdir(currdir)
	for file in filelist:
		if re.match(r'.*\.txt$', file):
			continue
		filename = currdir + "/" + file
		print filename
		with open(filename, 'r') as f:
			raw_text += f.read()

	with open(outputdir + "/" + dirname +  ".txt", 'w') as f:
		f.write(raw_text)

start_time = time()

dirpath  = sys.argv[1]
outputdir = sys.argv[2]

dirpath = os.path.expanduser(dirpath)
outputdir = os.path.expanduser(outputdir)
dirlist = filter(lambda x: not re.match(r'.*\.txt$', x), os.listdir(dirpath))

print dirlist
#Making thread workers
pool = ThreadPool(8)
pool.map(dumptext, dirlist)

#Closing threads
pool.close()
pool.join()

# for _dir in dirlist:
# 	dumptext(_dir)

print "Elapsed Time: {:.3f}".format((time()-start_time)) 
	# config_list.append(_dir)

