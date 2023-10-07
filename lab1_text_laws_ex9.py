# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 10:49:25 2022

@author: iulia.stanciu
"""
import pandas as pd
import matplotlib.pyplot as plt
import math 

from os import listdir
from os.path import isfile, join, isdir

path = "./novels/novels"
k = 100000

plt.scatter([0], [0])
plt.title('Unique words in text per number of words(log)')

def word_stats(word_counts):      
    num_unique = len(word_counts)
    counts = word_counts.values() 
    return num_unique 

def readWords(path, output_filename_k):
    dictionary = {}
    unique_words = []
    count = 0;
    
    for f in listdir(path):
        ff = join(path,f)
        print("processing ",ff)
        for text in open(ff, "r", encoding="utf8"):
            # transform punctuation to spaces in line
            # text = text.read()
            skips = [".", ",", ":", ";", "-", "_", "'", '"', "\n", "\r", "?", "!", "(", ")", "*", "/", "[", "]",
                     "https", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"] 
            for ch in skips: 
                text = text.replace(ch, "") 
            
            # translate line to lowercase
            text = text.lower()
            for word in text.split(" "):
                count +=1
                if word in dictionary: 
                    dictionary[word] += 1
                else:
                    dictionary[word] = 1
                
                if(count % k == 0):
                    with open(output_filename_k, 'w') as of:
                        print(word_stats(dictionary))
                        print(count)
                        plt.plot(count, word_stats(dictionary), "or")
                        of.write( str(count) + ";" + str(word_stats(dictionary)) + "\n")


readWords(path,"frquency_list.csv")

nw = 'Number of Words'
uw = 'Unique words'


def read_data(file):
    csv_read = pd.read_csv(file, delimiter=';', usecols=[nw, uw])
    return csv_read

data = read_data("frquency_list.csv")

data.plot(kind='scatter', x='Number of Words', y='Unique words', color='red') 
plt.grid()
plt.title('Unique words in text per number of words')
plt.show()

