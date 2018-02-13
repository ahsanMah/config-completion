#! /usr/bin/python

import ngram as Model
import matplotlib.pyplot as plt
import numpy as np
import sys, random, csv, dateutil.parser
from time import time
from collections import defaultdict


HEADERS = {"device":"Number of Devices", "samples":"Sample Size", "snapshots":"Snapshot Name"}
DEFAULT_OUTPUT_FILE = "analysis_results.csv"
DEFAULT_SNAPSHOT_DIRECTORY = sys.argv[1] + "default"
DEFAULT_SAMPLE_SIZE = 50

def analysis_func(type, idx, value):	
	func = TYPE_TO_FUNC[type]
	return func(value)

def snapshot_analysis(snapshot_name):
	return Model.run(["", DIRNAME+snapshot_name], sample=DEFAULT_SAMPLE_SIZE)

def sample_analysis(sample_size):
	return Model.run(["",DEFAULT_SNAPSHOT_DIRECTORY], sample=sample_size)

def run_analysis(variable, independent_vars, output_file=DEFAULT_OUTPUT_FILE):

	with open(output_file, "w+") as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow([HEADERS[variable], "Timestamp", "Accuracy"])

		for idx, value in enumerate(independent_vars):
			start_time = time()

			results = analysis_func(variable, idx, value)
			first_col = [[(idx+1)*10]] if variable == "device" else [[value]]
			results = np.append(first_col*len(results), results,axis=1)

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

	keys = sorted(rawdata.keys())
	print keys
	plot_data = [rawdata[independent_var] for independent_var in keys]
	labels = [str(label) for label in keys]

	plt.figure()
	bp = plt.boxplot(plot_data, whis=1.5, labels=labels, sym="gD", showmeans=True, meanline=True)
	plt.savefig('boxplot.png')
	plt.show()
	return rawdata

TYPE_TO_FUNC = {"device": snapshot_analysis, "snapshots": snapshot_analysis, "samples": sample_analysis}

DIRNAME = sys.argv[1]
process_mode = sys.argv[2] if len(sys.argv) > 2 else None
input_file = sys.argv[3] if len(sys.argv) > 3 else "analysis_results.csv"

DEVICES = ["devices_10","devices_20","devices_30","devices_40"]
SAMPLE_SIZES = range(50,300,50)
REPLACEMENTS = ["replacement_" + str(x) for x in range(1,2)]

if process_mode:
	process(input_file)
else:
	run_analysis(variable="snapshots", independent_vars=REPLACEMENTS)