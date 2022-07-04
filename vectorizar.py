import pandas as pd
import os, pickle
from IPython.display import display
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer

def tokenize(x):
    """
    It takes a string as input and returns a list of words in the string
    
    :param x: The text to be tokenized
    :return: A list of words
    """
    return RegexpTokenizer(r'\w+').tokenize(x.lower())

def removeStopwords(x):
    """
    It opens the file "stopWords_es.txt" and reads it into a string. Then it splits the string into a
    list of words. Then it returns a list of words from the input list that are not in the list of stop
    words
    
    :param x: the list of words to be filtered
    :return: A list of words that are not in the prohibitedWords list.
    """
    with open("stopWords_es.txt") as f:
        text = f.read()
        prohibitedWords = text.split("\n")
        return [word for word in x if not word in prohibitedWords]

def stemming(x):
    """
    It takes a string as input, splits it into words, stems each word, and then joins the stemmed words
    back into a single string
    
    :param x: The text to be stemmed
    :return: A string of words
    """
    stemmer = SnowballStemmer(language="spanish")
    return ' '.join([stemmer.stem(word) for word in x])


def generateDF(path):
    """
    It takes a path to a directory, and returns a dataframe with the name, path, and content of all
    files in that directory and its subdirectories
    
    :param path: the path to the directory containing the files you want to read
    :return: A dataframe with the name, path, and content of each file in the directory.
    """
    df = pd.DataFrame({"name": [], "path": [], "content":[]})
    files = os.listdir(path)
    for file in files:
        if file.startswith("."): continue
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            with open(file_path, 'r',encoding='latin-1') as f:
                df = df.append({"name": file, "path": file_path, "content": f.read()}, ignore_index=True)
        elif os.path.isdir(file_path):
            df = df.append(generateDF(file_path))

    return df

def splitall(path):
    """
    It takes a path and splits it into a list of all the directories and files in the path
    
    :param path: The path to split
    :return: A list of all the parts of the path.
    """
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


# Creating a dataframe with the name, path, and content of all files in that directory and its
# subdirectories.

df = pd.DataFrame({"name": [], "path": [], "content":[]})
df = df.append(generateDF(os.path.join(os.getcwd(), "elMundo")))
df = df.append(generateDF(os.path.join(os.getcwd(), "elPais")))
df = df.append(generateDF(os.path.join(os.getcwd(), "20minutos")))
df['tokens'] = df['content'].map(tokenize)
df['tokens'] = df['tokens'].map(removeStopwords)
df['lemma'] = df['tokens'].map(stemming)

df["medio"] = df["path"].apply(lambda x: splitall(x)[len(splitall(x))-3])
df["categoria"] = df["path"].apply(lambda x: splitall(x)[len(splitall(x))-2])
df["etiquettas"] = df["content"].apply(lambda x: x.split("\n")[0])

vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform(df['lemma'])
feature_names = vectorizer.get_feature_names()
dense = vectors.todense()
denselist = dense.tolist()
df['vector'] = denselist
csv = df[['name','path', 'medio', 'categoria', 'etiquettas', 'vector']]
csv.to_csv("vectores.csv", index=False)
pickle.dump(vectorizer, open("vectorizer.file", 'wb'))
display(csv)
