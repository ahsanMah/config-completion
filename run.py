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

def plotdata(plottype, data, labels):
	plotparams = {
				"boxplot": { "func" : plt.boxplot,
							"params":{"x":data, "whis":1.5, "sym":"gD","showmeans":True, "meanline":True}
							},
				"barchart": { "func" : plt.bar,
							  "params": {"x":range(len(labels)), "height":np.mean(data,axis=1), "color":"g"}
							}
				}

	plotfunc = plotparams[plottype]["func"]
	pltparams = plotparams[plottype]["params"]

	plotfunc(**pltparams)

def process(input_file, parsetype="samples", plottype="boxplot"):
	parsers = {"samples": [int, str, float], "snapshot": [str, str, float], "replacement": [str, str, float]}

	xlabels = {
				"samples":
					{"xlabel":"Number of Samples", "Title":"Varying Sample Size"},

				"replacement":
			  		{"xlabel":"Number of Replacements", "Title":" Accuracies After Adding Replacements"}
			  }

	rawdata = defaultdict(list)
	with open(input_file, "r+") as csvfile:
		reader = csv.reader(csvfile)
		reader.next()
		for row in reader:
			parsed_vals = parse_row(row,parsers[parsetype])
			rawdata[parsed_vals[0]].append(parsed_vals[2])

	keys = sorted(rawdata.keys())
	print keys
	data = [rawdata[independent_var] for independent_var in keys]
	labels = [x for x in range(0,len(keys))] if parsetype == "replacement" else [str(label) for label in keys]
	

	fig, ax = plt.subplots()
	plotdata(plottype, data, labels)
	# plt.boxplot(plot_data, whis=1.5, labels=labels, sym="gD",showmeans=True, meanline=True)
	# plt.scatter(x_axis, y_axis.flatten())
	# plt.savefig('boxplot.png')
	ax.set(ylabel="Prediction Accuracy", **xlabels[parsetype])
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
	process(input_file, parsetype="replacement")
else:
	run_analysis(variable="snapshots", independent_vars=REPLACEMENTS)