#! /usr/bin/python

import ngram as Model
import numpy as np
import sys, random, csv
from time import time

dirname = ["devices_10","devices_20"]#,"devices_30","devices_40"]
output_file = "devices_run.csv"
sample_size = 8

with open(output_file, "w+") as csvfile:
	writer = csv.writer(csvfile)
	writer .writerow(["Num Devices", "Timestamp", "Accuracy"])
	for idx, name in enumerate(dirname):
		random.seed(7)
		start_time = time()
		results = Model.run(["", sys.argv[1]+name],sample=sample_size)
		device_col = [[(idx+1)*10]]*sample_size
		results = np.append(device_col, results,axis=1)
		writer.writerows(results)

		print "Time elapsed: {:.3f}".format((time()-start_time))



########## Performing analyses ###################
with open(input_file, "r+") as csvfile:
	reader = csv.reader(csvfile)