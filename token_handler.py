import nltk
from nltk.tokenize import RegexpTokenizer
nltk.download('punkt')
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem.porter import PorterStemmer
import re
from unidecode import unidecode


#Tokenize a query
def tokenize(string : str):

    stemmer = PorterStemmer()
    tokenizer = RegexpTokenizer(r'\w+')
    #Getting stop words
    stop_words = set(stopwords.words('english'))
    #Adding montreal,quebec,canada to stopwords as they appear in every page
    stop_words.add('montreal')
    stop_words.add('quebec')
    stop_words.add('canada')
    stop_words.add('qc')
    #Removing accents
    string = unidecode(string)
    #Case folding
    string = string.casefold()
    #Removing numbers
    string = re.sub(r'\d+', ' ', string)
    

    #Tokenizes and removes punctuation
    string = string.replace("_", " ")
    tokens = tokenizer.tokenize(string)
    
    #Porter Stemmer stemming and removing stop words
    filtered_tokens = [stemmer.stem(w) for w in tokens if not w in stop_words]
        

    return filtered_tokens