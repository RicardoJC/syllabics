#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import string
import nltk
from syllabicator import Silabicador
from unidecode import unidecode
from collections import OrderedDict,Counter
import numpy as np

class Tokenizer(object):

    def unique_chars(self, text):
        chars = set(list(text))
        return chars

    def remove_punctuation(self, text):
        #spanish_punctuation = r"¡!“-,¿.?,…\xa0\xad–—\n«»”"
        text = text.replace('\n','')
        return re.sub(u'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]', '',text)
        #return re.sub('[%s]' % re.escape(spanish_punctuation + string.punctuation), ' ', text)


    def sentences(self, text):
        spanish_tokenizer = nltk.data.load('tokenizers/punkt/spanish.pickle')
        return spanish_tokenizer.tokenize(text)

    def tokenize(self, text):
        temp_text = self.remove_punctuation(text)
        temp_text = re.sub('\d+', # No numbers
                           '',
                           temp_text,
                           re.UNICODE).lower()
        temp_text = re.sub(r'[^\w\s]',
                           '',
                           temp_text,
                           re.UNICODE).lower()

        temp = temp_text.split(" ")
        while '' in temp:
            temp.remove('')
        return temp

    def tokenize_sentences(self, sentences):
        res = []
        for sentence in sentences:
            res.append(self.tokenize(sentence))


class SyllableStatistics(Tokenizer):

    def __init__(self, corpus_path, with_accents=False):

        self.pat = []
        self.freqs = {}
        self.readable = {}
        self.syllabificator = Silabicador()

        total_syllables = 0

        for root, _, files in os.walk(corpus_path):
            for filepath in files:

                with open(root + "/" + filepath, "r") as f:
                    content = f.read()

                tokens = self.tokenize(content)
                sentences = self.sentences(content) #####
                for token in tokens:
                    #print(token)
                    result, partiall_stuff = self.syllabificator(token)
                    partiall_stuff = encontrar_patrones(result)
                    #print(result,partiall_stuff) #imprime palabra dividida y patron
                    self.pat.append(tuple(partiall_stuff))
                    #print(result) ###### para dividir en silabas


                    #print(patrones_silabicos)
                    #print(partiall_stuff) ###### patronesobj
#                     try:
#                         print("-".join([str(res) for res in result]))
#                     except:
#                         import ipdb;ipdb.set_trace()
#                         exit(0)
                    for syllable in result:
                        syllable = str(syllable)
                        if not with_accents:
                            syllable = unidecode(syllable)

                        try:
                            self.freqs[syllable] += 1
                        except:
                            self.freqs[syllable] = 1
                        total_syllables += 1
                print(filepath)

        self.freqs = OrderedDict(sorted(self.freqs.items(),
                                        key=lambda x:x[1],
                                        reverse=True)
                                 )

        self.readable = OrderedDict(sorted(self.readable.items(),
                                           key=lambda x:x[1],
                                           reverse=True)
                                    )

        # Calculate probabilities
        probabilities = {}
        for syl, freq in self.freqs.items():
            probabilities[syl] = freq/total_syllables

        self.probabilities = np.array(sorted(probabilities.items()))
        self.syls = np.array(self.probabilities[:,0])
        self.proba = np.array(self.probabilities[:,1], dtype=np.float64)
        self.count = Counter(self.pat)


    def generate_samples(self, n):
        return np.random.choice(self.syls,
                                n,
                                p=self.proba)

def encontrar_patrones(palabra_silabicada):
    patrones = []
    for silaba in palabra_silabicada:
        patron = ""
        if silaba.lower() not in ['ya','ye','yi','yo','yu']:
            silaba = silaba.replace("y", "#", 1)
        for letra in silaba:
            if letra.lower() in "aeiouáéíóúü":
                patron += "V"
            elif letra.lower() in '#':
                patron += 'V'
            else: # es una consonante o una "y", hay que revisar
                patron += "C"
        patrones.append(patron)
    return patrones

palabra_silabicada = ['ya','hoy','ten','go','ham','bre','y','sue','ño']
patrones_silabicos = encontrar_patrones(palabra_silabicada)
#print(patrones_silabicos)
obj = SyllableStatistics(r'/Users/ricardoj/Documents/Engineering/Grupo_de_Ingenieria_Linguistica/Silabario/corpus')
#print(obj.count)
#print(obj.freqs)
#print(obj.pat)
#obj = SyllableStatistics(r'E:\IPERSPICUIDAD\inflez\5.muydificil\\')
##corpus_path= (r'E:\IPERSPICUIDAD\1muy fácil\textos\\')441
