#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
from datetime import datetime
import PyPDF2
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize 

import os
import re 
import math
import operator
import requests

from bs4 import BeautifulSoup as soup
from bs4.element import Comment

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from collections import Counter
from pprint import pprint


# In[2]:

def readContents():
    pdf_file = open('FAQs.pdf', 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    number_of_pages = read_pdf.getNumPages()

    questions = []
    answers = []
    for i in range(3, number_of_pages-1):
        page = read_pdf.getPage(i)
        page_content = page.extractText()
        
        while page_content.find('Q.')!=-1:
            question = page_content[page_content.find(' Q.')+4:page_content.find('A.')]
            questions.append(question.replace('\n',''))
            page_content = page_content[page_content.find('A.'):]
            answer = page_content[page_content.find('A.')+4:page_content.find('Q.')]
            answers.append(answer.replace('\n',''))
            page_content = page_content[page_content.find('A.')+4:]

    return (questions, answers);


def words(questions):

    words = []
    doc_text = []
    stop_words = set(stopwords.words('english'))


    for q in questions:
        
        
        # Tokenize
        
        tokens = word_tokenize(q)
        
        # Stop word removal
        
        filtered_words = [w for w in tokens if not w in stop_words]
        
        new_words = []
        ps = PorterStemmer() 
        for w in filtered_words:
            if len(w) != 1:
                new_words.append(ps.stem(w))
        doc_text.append(new_words)
        
        for w in new_words:
            words.append(w)
    return (words,stop_words, doc_text, ps);

#print('Word count: ', len(words))


# In[47]:


# Word frequency

#frequency = Counter(words)
#print('Word frequency: \n')
#print(frequency)


# In[21]:


# Cosine similarity

#WORD = re.compile(r'\w+')

# Calculate the cosine similarity between the two vectors
# Parameters:
#     vec1: Vector 1
#     vec2: Vector 2
# Return: 
#     Cosine similarity value
def get_cosine(vec1, vec2):
    
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

# Vectorize words
# Parameters:
#     text: Text data
# Return:
#     Text vector
def text_to_vector(text):
    WORD = re.compile(r'\w+')
    words = WORD.findall(text)
    return Counter(words)


# In[84]:

def find(userQUERY,stop_words,doc_text,answers,ps):
    #userQUERY = "SPP stands for?"
    QUERY = userQUERY.replace("?", "").split(" ")
    filtered_query = [ps.stem(w) for w in QUERY if not w in stop_words]
    #print(filtered_query)
    cosine_similarities = {}

    for idx, data in enumerate(doc_text):
        
        data = ' '.join(data)
        
        vector1 = text_to_vector(" ".join(filtered_query))
        vector2 = text_to_vector(data)
        
        cosine_similarities[idx] = get_cosine(vector1, vector2)

        
    key_max = max(cosine_similarities.keys(), key=(lambda k: cosine_similarities[k]))

    # print('Maximum Value: ', cosine_similarities[key_max], '\n')
    # print("Q. ", userQUERY)

    if(cosine_similarities[key_max] < 0.4):
        return "Kindly be more precise."
    else:
        return answers[key_max]
    

