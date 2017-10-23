#! /usr/bin/python

import nltk
from nltk.util import bigrams, trigrams
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures

train_file = open("token_dump.txt").read().split()
train_text = [token.strip() for token in train_file]

#Getting bigrams
bi_finder = BigramCollocationFinder.from_words(train_text)
tri_finder = TrigramCollocationFinder.from_words(train_text)
bi_finder.apply_freq_filter(3)

#Scoring each ngram using likelihood ratios
bigram_scores = bi_finder.score_ngrams(BigramAssocMeasures.likelihood_ratio)
trigram_scores = tri_finder.score_ngrams(TrigramAssocMeasures.likelihood_ratio)


bigram_scores = sorted(bigram_scores, key=lambda item: item[1],reverse=True)
trigram_scores = sorted(trigram_scores, key=lambda item: item[1],reverse=True)

bigram_scores = bigram_scores[:]
 
for result in bigram_scores: print result
for result in trigram_scores: print result
