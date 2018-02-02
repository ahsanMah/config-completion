#! /usr/bin/python

import ngram as Model
import sys, random, csv
from time import time

random.seed(7)
dirname = ["devices_10","devices_20","devices_30","devices_40"]
output_file = "devices_run.csv"

with open(output_file, "w+") as csvfile:
	writer = csv.writer(csvfile)
	for name in dirname:
		writer.writerow([name])
		start_time = time()
		results = Model.run(["", sys.argv[1]+name],sample=100)
		
		writer.writerows(results)

		print "Time elapsed: {:.3f}".format((time()-start_time))