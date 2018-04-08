import sys, csv


# def get_tab_completions(config_file):


def make_completion_map(filename):
	completion_map = {}

	with open(filename, "r+") as csvfile:
		reader = csv.reader(csvfile)
		reader.next()
		for parsed_vals in reader:

			line_num = int(parsed_vals[0])
			token = parsed_vals[1]
			predictions = map(lambda x: x.strip().replace("'",""), parsed_vals[2:])
			if len(predictions) > 0:
				predictions[0] = predictions[0].replace("[","")
				predictions[-1] = predictions[-1].replace("]","")

			if line_num not in completion_map:
				completion_map[line_num] = {}

			# Add to completion map

			completion_map[line_num][token] = predictions
	return completion_map



data = make_completion_map("antlr-tab-completion/results/B.cfg.txt")
for x in data[7]:
	print "_________" + x + "_________"
	print data[7][x]