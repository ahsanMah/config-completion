#! /usr/bin/python

import ngram as Model
import matplotlib.pyplot as plt
import numpy as np
import sys, random, csv, dateutil.parser
from time import time
from collections import defaultdict


HEADERS = {"device":"Number of Devices", "snapshots":"Sample Size"}
DEFAULT_OUTPUT_FILE = "devices_run.csv"
DEFAULT_SNAPSHOT_DIRECTORY = sys.argv[1] + "default"
DEFAULT_SAMPLE_SIZE = 100

def analysis_func(type, value):	
	func = TYPE_TO_FUNC[type]
	return func(value)

def device_analysis(snapshot_name):
	results = Model.run(["",snapshot_name],sample=DEFAULT_SAMPLE_SIZE)
	device_col = [[(idx+1)*10]]*sample_size
	results = np.append(device_col, results,axis=1)
	return results

def snapshot_analysis(sample_size):
	results = Model.run(["",DEFAULT_SNAPSHOT_DIRECTORY],sample=sample_size)
	return results

def run_analysis(variable, independent_vars, output_file=DEFAULT_OUTPUT_FILE):

	with open(output_file, "w+") as csvfile:
		writer = csv.writer(csvfile)
		writer .writerow([HEADERS[variable], "Timestamp", "Accuracy"])

		for idx, value in enumerate(independent_vars):
			random.seed(7)
			start_time = time()
			results = analysis_func(variable, value)
			writer.writerows(results)

			print "Time elapsed: {:.3f}".format((time()-start_time))

########## Performing analyses ###################

def parse_row(row, parsers):
	return [parser(val) for val,parser in zip(row, parsers)]
	
def process(input_file):
	parsers = [str, dateutil.parser.parse, float]
	rawdata = defaultdict(list)
	with open(input_file, "r+") as csvfile:
		reader = csv.reader(csvfile)
		reader.next()
		for row in reader:
			parsed_vals = parse_row(row,parsers)
			rawdata[parsed_vals[0]].append(parsed_vals[2])
	print rawdata	
	plot_data = [rawdata[independent_var] for independent_var in rawdata]
	labels = [str(label) for label in rawdata]

	plt.figure()
	bp = plt.boxplot(plot_data, whis=1.5, labels=labels, sym="gD", showmeans=True, meanline=True)
	plt.savefig('boxplot.png')
	plt.show()
	return rawdata

TYPE_TO_FUNC = {"device": device_analysis, "snapshots": snapshot_analysis}

process_mode = sys.argv[2] if len(sys.argv) > 2 else None
input_file = sys.argv[3] if len(sys.argv) > 3 else "devices_run.csv"

DIRNAMES = ["devices_10","devices_20","devices_30","devices_40"]
DIRNAMES = map(lambda x: sys.argv[1]+x, DIRNAMES)

SAMPLE_SIZES = range(50,100,50)
print DEFAULT_SNAPSHOT_DIRECTORY
if process_mode:
	process(input_file)
else:
	run_analysis(variable="snapshots", independent_vars=SAMPLE_SIZES)