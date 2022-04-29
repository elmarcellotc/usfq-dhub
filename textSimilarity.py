# 
# Name: textSimilarity.py
# Author: Marcello Coletti
# Contact: coletti.marcello@gmail.com
# USFQ Data Hub
#

### Description:

# This script return an object with a cosine similarity matrix and a dictionary with the pairs and their similarity value.

### Libraries required:

# pip install numpy
# pip install googletrans==3.1.0a0
# pip install contractions
# pip install sklearn
# pip install nltk
# pip install pandas
# pip install openpyxl

### Must run before start textSimilarity.py:

# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('omw-1.4')

from googletrans import Translator
translator = Translator()
import string
from contractions import fix
from nltk.corpus import stopwords
stopwords = stopwords.words('english')
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

def clean_string(text): # The strings should avoid stopwords, digits, punctuations and 
                        # characters that do not belong to the English alphabet
    
    text = fix(text)
    
    text = text.lower()
    text = text.replace('_',' ')
    text = text.replace('-',' ')
    text = text.replace('(',' ')
    text = text.replace(')',' ')
    
    text = ''.join([word for word in text if word not in string.punctuation])
    
    text = ' '.join([word for word in text.split() if word not in stopwords])
    
    return ' '.join(s for s in text.split() if not any(c.isdigit() for c in s))

def get_synonyms(word): # To increase the efficiency of the matrix. 
                        # Moreover get synonyms and the definitions, also cleaned, of the words
    
    from nltk.corpus import wordnet
    
    synonyms = []
    for syn in wordnet.synsets(word):
        
        for name in syn.lemma_names():
            
            name = clean_string(name)
            
            for word in name.split(' '):
                if word not in synonyms:
                    synonyms.append(word)
                    
                    try:
                        defin = wordnet.synsets(name)
                        definition = defin[0].definition()
                        definition = clean_string(definition)
                        
                        for def_word in definition.split(' '):
                            if def_word not in synonyms:
                                synonyms.append(def_word)
                        
                    except:
                        None
    
    return synonyms

def get_words_group(sentences): # This function returns the original self.sentences plus
                                # the words cleaned and add them synonyms and definitions.
    
    words_group = []
    for i in range(len(sentences)):
        
        words = sentences[i].split(' ')
        syns_group = []
        
        for word in words:
            syns_group.extend(get_synonyms(word))
            
        words_group.append(syns_group)
        
    return words_group

class Similarity:
    
    def __init__(self, id, sentences, var_names):
        self.id = id+': Cosine Similarity Analisys' # The name of the object
        self.sentences = sentences # The strings used to calculate cosine similarity. This variable only store the ofiginals.
        self.var_names = var_names # Name of each string in self.sentences 
        
        self.similarity_matrix = None # The matrix (self.var_names x self.var_names) store a proportion of how similar are two 
                                      # variables according to sentences.
        self.get_similarity() # To assemble self.similarity_matrix
        
        self.s_min_value = 1 # Represents the second minimum value in self.similarity_matrix. The firts should be 0. 
                             # If not 0 in the matrix, self.s_min_value will be the minimum.
                             # It start as 1 and decreases after run self.get_similarity_dict()
                             
        self.s_max_value = 0 # Represents the second maximum value in self.similarity_matrix. The firts should be 1. 
                             # self.similarity_matrix must have a 1 on it with different strings in at least one character.
                             # self.s_max_value only could be the first maximum if all strings in sentences are strictly equal.
                             # It start as 0 and increases after run self.get_similarity_dict().
                             
        self.values = [] # Will be a dictionary with pair of variables and its cosine similarity.
        self.get_similarity_dict() # To assemble self.s_min_value, self.s_max_value and self.values.
        
        self.__str__()
        
    def __str__(self):
        print(f'\n{self.id}\n',
              f'\n{len(self.var_names)} strings used',
              f'\nSecond minimum value: {self.s_min_value}',
              f'\nSecond maximum value: {self.s_max_value}',
              f'\n')
        
    def get_similarity(self):

        sentences = [translator.translate(x).text for x in self.sentences]
        sentences = [clean_string(x) for x in sentences]

        words_group = get_words_group(sentences)

        sentences = [' '.join(x) for x in words_group]
        vectorizer = CountVectorizer().fit_transform(sentences)
        vectorizer = vectorizer.toarray()
        self.similarity_matrix = cosine_similarity(vectorizer)
        
    def get_similarity_dict(self):
        
        values = []
        pairs = []
        
        for i in range(len(self.var_names)):
            for j in range(len(self.var_names)):
                if self.var_names[j]+'/'+self.var_names[i] not in pairs:
                    pairs.append( self.var_names[i]+'/'+self.var_names[j] )
                    k = round(self.similarity_matrix[i][j], 2)
                    values.append( k )
                    
                    if k > 0 and k < self.s_min_value:
                        self.s_min_value = k
                    if k < 1 and k > self.s_max_value:
                        self.s_max_value = k
                    
        self.values = dict(zip(pairs, values))