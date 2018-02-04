#! /usr/bin/python

import ngram as Model
import matplotlib.pyplot as plt
import numpy as np
import sys, random, csv, dateutil.parser
from time import time
from collections import defaultdict

dirname = ["devices_10","devices_20"]#,"devices_30","devices_40"]
output_file = "devices_run.csv"
input_file = "devices_run.csv"
sample_size = 8

def run_analysis():
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

def parse_row(row, parsers):
	return [parser(val) for val,parser in zip(row, parsers)]
	
def process(input_file):
	parsers = [int, dateutil.parser.parse, float]
	rawdata = defaultdict(list)
	with open(input_file, "r+") as csvfile:
		reader = csv.reader(csvfile)
		reader.next()
		for row in reader:
			parsed_vals = parse_row(row,parsers)
			rawdata[parsed_vals[0]].append(parsed_vals[2])
	plot_data = [rawdata[size] for size in rawdata]
	print rawdata
	plt.figure()
	plt.boxplot(plot_data,0,'gD')

	plt.show()

run_analysis()