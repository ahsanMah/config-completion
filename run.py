#! /usr/bin/python

import ngram as Model
import sys, random

random.seed(7)
dirname = ["devices_10","devices_20","devices_30"]

for name in dirname:
	Model.run(["", sys.argv[1]+name])

