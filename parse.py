# Author: Sheng Wang
# Date: 2nd May, 2019
# Description: This file is created to parse the data - specically, to deal with 
# the text.

#!/usr/bin/python3

import sys
import json
import os
import pprint 
import random

import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

from nltk import tokenize
from nltk.tokenize import word_tokenize 
from nltk.tag import pos_tag
from nltk.chunk import conlltags2tree, tree2conlltags 
#from communicate import *
#from collector import *

import spacy
from spacy import displacy
from collections import Counter 
import en_core_web_sm 

from pattern.en import parse 
from pattern.en import tag
from pattern.en import sentiment, polarity, subjectivity, positive 
from pattern.en import mood
from pattern.en import wordnet
from pattern.en import modality
from pattern.en import Sentence

import re
from operator import itemgetter 
from collections import Counter 

# Variables 
tf = "Titles.txt"
df = "Des.txt"


data_t = []
data_d = []

global slist
slist = []

global base
base = []

global flist
flist = []

adjective_words = []
adverb_words = []
verb_words = []
noun = []

# A simple class for sentence
class negative_sen:

	def __init__(self, original_sentence, positive_words, polarity, subjectivity):
		self.original_sentence = original_sentence
		self.neg_sentence = original_sentence
		self.positive_words = positive_words 
		self.polarity = polarity
		self.subjectivity = subjectivity
		self.if_finished = False

	def write(self, filename):
		self.f = open(filename, 'a')
		self.f.write( self.neg_sentence )
		self.f.close()


	# For checking result
	def display(self):
		print("The original sentence is "+self.original_sentence +'\n')
		print("The changed result is " + self.neg_sentence + '\n')

	
	# Check if there is any postive words left 
	def if_finish (self):
		if len(self.positive_words) == 0:
			self.if_finished = True
		
	
	# Update word's positive_word list 
	def update(self):
		if len(self.positive_words) != 0:
			self.positive_words.pop(0)


	# Replace the word with some more negative word
	def replace(self, original_word, worse_word):
		temp = self.neg_sentence
		temp = temp.replace( original_word, worse_word)
		self.neg_sentence = temp
		
		#update new polarity and subjectivity
		w = sentiment(self.neg_sentence)
		self.polarity = w[0]
		self.subjectivity = w[1]


	
# define regular expression
rx_dict = {
		'title': re.compile( r'title = (?P<title>.*)\n'),
		'description': re.compile(r'description = (?P<description>.*)\n')
		
}


# A helper function to parse the line to return the key and the match result
def parse_line( line ):
	for key, rx in rx_dict.items():


		match = rx.search(line)
	

		if match:
			return key, match

	return None, None



# A helper function to categorize some negative words
def sort_bad_words():
	print ( "Categorize... lists of words ...\n")
	
	global adjective_words
	global adverb_words
	global verb_words
	global noun

	with open ( "negative-words.txt", 'r', encoding="ISO-8859-1") as f:
		word = f.readline()
		while word:
		
			#first parse to get a tag for the word
			w = nltk.word_tokenize(word)
			r = nltk.pos_tag(w)
			tag = r[0][1]

	
			#then get the polarity of the word with sentiment
			s = sentiment(word)

			polarity = s[0]
			subjectivity = s[1]
			
			#print( "Polarity is " + str(polarity) + " Subjectivity is " + str(subjectivity) + "\n")
			tup = (word, polarity)

			if tag == "JJ":
				adjective_words.append(tup)
			elif tag == "RB":
				adverb_words.append(tup)
			elif tag == "NN":
				noun.append(tup)
			elif tag == "NNS":
				noun.append(tup)
			elif tag == "VB":
				verb_words.append(tup)
			elif tag == "VBN":
				verb_words.append(tup)

			word = f.readline()


	# Sorted those words		
	adjective_words = sorted(adjective_words, key=itemgetter(1), reverse=True)
	adverb_words = sorted(adverb_words, key=itemgetter(1), reverse=True)
	verb_words = sorted(verb_words, key=itemgetter(1), reverse=True)
	noun = sorted(noun, key=itemgetter(1), reverse=True)






# Function for parse a single_file
def parse_file( filename, keyword ):
	global slist
	print ( "PARSING " + filename + "..... Wait\n")


	with open ( filename, 'r' ) as file_object:
		line = file_object.readline()

		while line:
			
			# Call helper fuchtion
			key, match = parse_line(line)
			


			# Check the result
			if key == 'title':

				t = match.group('title')
				length = len(t)

				if length <= 50:
					temp = t.lower()
					if temp.find(keyword) == -1:
						if temp.find('subject') == -1:
							data_t.append(t)
	
			if key == 'description':

				d = match.group('description')

				f = open("train_data.txt", 'a')
				f.write(d)
				f.write('\n')
				f.close()
				
				list_sentences = preprocess(d)
				
				for s in list_sentences:
					slist.append(s)


			line = file_object.readline()


	




# A preprocessor to divide paragraph into sentences
def preprocess( sent ):
	result = tokenize.sent_tokenize(sent)

	return result

	


# This function is used to randamly choose 20 sentences from the slist to 
# form a paragrah
def get_base( slist ):
	n = len(slist)

	global base
	

	for i in range(10):
		num = random.randint(1, n-1)

		s = slist[num]

		base.append(s)



# This function is used to parse sentence after chooing a base
def parse_sentence( slist ):
	length = len(slist)

	get_base( slist )

	length2 = len(base)

	print( 'Start processing ' + str(length2) + ' base sentence from total ' + str(length) + ' sentences\n')

	for s in base:
		process(s)

	print ( 'End base processing\n')



# This function is to further process description to categorize each words 
def process(sent):
	original_sen = sent 

	print ( "Processing sentence ....\n")
	# Give each word in a sentence a tag 
	sent= nltk.word_tokenize(sent)
	result = nltk.pos_tag(sent)


	chunk_pattern = 'NP: {<DT>?<JJ>*<NN>}'
	cp = nltk.RegexpParser(chunk_pattern)
	cs = cp.parse(result)

	iob_tagged = tree2conlltags(cs)

#	print(json.dumps(iob_tagged, ident=4, sort_keys=False))

	# Find the most_postive_word in one sentence

	subjectivity = 0
	polarity = 0
	
	most_positive = -1
	positive_words = list( tuple() )

	for item in iob_tagged:
		pos = item[1]
		if pos == "JJ":
			w = sentiment(item[0])
			if w[0] >= 0:
				tup = (item[0],w[0],w[1],pos)
				positive_words.append( tup )

		elif pos == "VB":
			w = sentiment(item[0])
			if w[0] >= 0:
				tup = (item[0],w[0],w[1],pos)
				positive_words.append( tup )



		elif pos == "NN":
			w = sentiment(item[0])
			if w[0] > 0:
				tup = (item[0],w[0],w[1],pos)
				positive_words.append( tup )

		elif pos == "NNS":
			w = sentiment(item[0])
			if w[0] > 0:
				tup = (item[0],w[0],w[1],pos)
				positive_words.append( tup )

		elif pos == "VBN":
			w = sentiment(item[0])
			if w[0] >= 0:
				tup = (item[0],w[0],w[1],pos)
				positive_words.append( tup )

		elif pos == "RB":
			w = sentiment(item[0])
			if w[0] >= 0:
				tup = (item[0],w[0],w[1],pos)
				positive_words.append( tup )



	# Sort the word list according to its polarity
	positive_words = sorted(positive_words, key=itemgetter(1), reverse=True)

	#for item in positive_words:
	#	print(item[0]+" "+str(item[3])+" "+str(item[1])+"\n")
	


	# Create sentences 
	s = sentiment(original_sen)
	polarity = s[0]
	subjectivity = s[1] 
	
	
	new_sen = negative_sen(original_sen, positive_words, polarity, subjectivity)

	flist.append( new_sen )


# This program is to modify all the sentence to its most negative form 
def transform():
	print ( "Transform sentence start ....\n")
	n1 = len(adjective_words)
	n2 = len(adverb_words)
	n3 = len(verb_words)
	n4 = len(noun)

	for sentence in flist:
		while not sentence.if_finished:
			if sentence.positive_words:
				tup = sentence.positive_words[0]
			else:
				sentence.if_finish()
				continue

			# Generate random index
			index1 = random.randint(0,n1-1)
			index2 = random.randint(0,n2-1)
			index3 = random.randint(0,n3-1)
			index4 = random.randint(0,n3-1)
			index5 = random.randint(0,n4-1)


			word = tup[0]
			tag = tup[3]

			if tag == "JJ":
				worse_word = adjective_words[index1][0]
			elif tag == "RB":
				worse_word = adverb_words[index2][0]
			elif tag == "VB":
				worse_word = verb_words[index3][0]
			elif tag == "VBN":
				worse_word = verb_words[index4][0]
			else:
				worse_word = noun[index5][0]
		
			sentence.replace( word, worse_word)

			#update sentence's positive_word list
			sentence.update()
			sentence.if_finish()


	

	print ("#Transform sentences end. Total " + str(len(flist)) + " sentences get transformed \n")



# This function is used to parse title
def parse_title():
	print( "Start parsing titles ... Wait\n")

	# Clean the title file
	cwd = os.getcwd()
	exist = os.path.isfile(cwd+"/"+"Titles.txt")
	if exist:
		os.remove(cwd+"/"+"Titles.txt")

	global data_t

	nlp = en_core_web_sm.load()


	temp_list = []
	for title in data_t:

		doc = nlp(title)


		unqualify = False
		for x in doc:
			if x.ent_type_ == 'NORP':
				unqualify = True
				break
			elif x.ent_type_ == 'MONEY':
				unqualify = True
				break
			elif x.ent_type_ == 'GPE':
				unqualify = True
				break
			elif x.ent_type_ == 'PERSON':
				unqualify = True
				break
			elif x.ent_type_ == 'LANGUAGE':
				unqualify = True
				break
			elif x.ent_type_ == 'DATE':
				unqualify = True
				break
			elif x.ent_type_ == 'LOC':
				unqualify = True
				break
			elif x.ent_type_ == 'ORG':
				unqualify = True
				break
			elif str(x) == 'Philippine':
				unqualify = True
				break
			elif str(x) == 'Principles' or str(x) == "History" or str(x) == "Oxford":
				unqualify = True
				break

		
		if not unqualify:
			temp_list.append(title)
		#else:
		#	print( title + "\n" )


	data_t = temp_list

	for t in data_t:
		f = open("Titles.txt", 'a')
		f.write(t)
		f.write("\n")
		f.close() 
		







# Main execution

topics = ["Vampire", "Zombie", "Aliens", "Ghost", "Witch", "Demon", "Clown", "Babayaga", \
		"Mummy", "Siren", "Werewolf", "Godzilla", "Dragon", "Jorogumo", \
		"FoxSpirits", "Tikbalang", "Killer"]

files = []
for t in topics:
	tup = (t+".txt", t.lower())
	files.append( tup )

sort_bad_words()

parse_title()

for f in files:
	parse_file( f[0], f[1])

parse_sentence( slist )
 
transform() 


