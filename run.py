#! /usr/bin/python

import ngram as Model
import matplotlib.markers as mark
import matplotlib.lines as mlines
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
							"params":{"x":data, "labels":labels, "whis":1.5, "sym":"g*","showmeans":True, "meanline":True}
							}
				# 			,
				# "barchart": { "func" : plt.bar,
				# 			  "params": {"x":range(len(labels)), "height":np.mean(data,axis=1), "color":"g"}
				# 			}
				# "lineplot": { "func" : plt.plot,
				#   			  "params": {"xdata":range(len(labels)), "ydata":np.mean(data,axis=1), "marker":"go-"}
				# 			}
				}

	plotfunc = plotparams[plottype]["func"]
	pltparams = plotparams[plottype]["params"]

	plotfunc(**pltparams)

def process(input_file, parsetype="samples", plottype="boxplot"):
	parsers = {"samples": [int, str, float], "snapshots": [str, str, float], "replacements": [str, str, float], "devices": [int, str, float]}

	xlabels = {
				"devices":
					{"xlabel":"Number of Device Configurations", "Title":"Effect of Training Devices on Prediction"},

				"replacements":
			  		{"xlabel":"Number of Replacements", "Title":"Effect of Placeholders on Prediction"},
			  
		  		"snapshots":
				{"xlabel":"University Name", "Title":"Prediction Accuracies for Different Universities"},

				"samples":
					{"xlabel":"Sample Size", "Title":"Effect of Selecting More Samples in Time"}

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
	labels = [x for x in range(0,len(keys))] if parsetype == "replacements" else [str(label) for label in keys]
	# labels = ["A","B","C"]
	# labels = ["Core","Edge"]
	print labels
	print data
	fig, ax = plt.subplots(figsize=(5,4))

	plotdata(plottype, data, labels)
	# plt.bar(labels,np.mean(data,axis=1))

	green_line = mlines.Line2D([], [], color='green', ls='--', label='Mean')
	orange_line = mlines.Line2D([], [], color='orange',label='Median')
	green_marker = mlines.Line2D([], [], color='green', marker="*",ls="None", label='Outlier')

	legend = ax.legend(loc='lower right', fontsize="small", shadow=True, handles=[green_line, orange_line, green_marker])

	ax.set(ylabel="Prediction Accuracy", xlabel = xlabels[parsetype]["xlabel"])
	# plt.ylim((0.8,1))
	# plt.savefig("Poster/uni_analysis.png")
	plt.show()

	return rawdata

TYPE_TO_FUNC = {"device": snapshot_analysis, "snapshots": snapshot_analysis, "samples": sample_analysis}

process_mode = sys.argv[1]
DIRNAME = sys.argv[2]
input_file = sys.argv[3] if len(sys.argv) > 3 else "analysis_results.csv"

DIRNAMES = ["madison_2011", "umn", "northwestern" ]
CORE_EDGE = ["core_only","edge_only"]
DEVICES = ["devices_10","devices_20","devices_30","devices_40"]
SAMPLE_SIZES = range(50,300,50)
REPLACEMENTS = ["replacement_" + str(x) for x in range(1,2)]


process_dict = {
				"-p": {"input_file": DIRNAME, "parsetype":"samples"},
				"-s": {"variable":"snapshots", "independent_vars":[input_file]},
				"-m": {"variable":"snapshots", "independent_vars":CORE_EDGE}
}

proc_args = process_dict[process_mode]

if process_mode == "-p":
	process(**proc_args)
else:
	run_analysis(**proc_args)