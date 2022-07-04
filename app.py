from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import pickle, os
from numpy import dot
from numpy.linalg import norm
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer

root = Tk()
tabs = ttk.Notebook(root)
tabs.pack(fill=BOTH, expand=TRUE)
busqFrame = ttk.Frame(tabs)
clasiFrame = ttk.Frame(tabs)
tabs.add(busqFrame, text="Búsqueda de noticias")
tabs.add(clasiFrame, text="Comparación de noticias")
vector_df = pd.read_csv("vectores.csv")

def sorensen(a,b):
    """
    It takes two strings, splits them into arrays, finds the intersection of the two arrays, and returns
    the length of the intersection divided by the sum of the lengths of the two arrays
    
    :param a: The first string to compare
    :param b: The list of words in the first sentence
    :return: The Sorensen similarity coefficient between two lists.
    """
    a = str(a).split(",")
    b = str(b).split(",")

    def intersect(arr1, arr2):
        r = []
        o = {}
        for i in arr2:
            o[i] = True
        for i in arr1:
            if i in o:
                r.append(i)
        return r

    return (2 * len(intersect(a,b))) / (len(a) + len(b))

def comparar():
    """
    It takes the selected news item, finds the vector and tags for that news item, then compares it to
    all the other news items in the database, and returns the top n most similar news items, and the top
    n most similar news items based on tags
    :return: A list of strings.
    """
    if not list_noticias.curselection():
        messagebox.showinfo("Porfavor elige una noticia", "Porfavor elige una noticia")
        return
    buscar_btn["text"] = "Calculando..."
    root.update()
    global vector_df
    selected = list_noticias.get(list_noticias.curselection()[0])
    row = vector_df[(vector_df['name'] == selected) 
        & (vector_df["medio"] == Medios_choices.get()) 
        & (vector_df["categoria"] == Categ_choices.get())]
    index_noticia = row.index.tolist()[0]
    vector_noticia = row["vector"].to_list()[0]
    etiquettas_noticia = row["etiquettas"].to_list()[0]
    filtered = vector_df.copy()
    if filter_noticias.get() != "todos":
        filtered = vector_df[vector_df["medio"] == filter_noticias.get()].copy()
    filtered["similitud"] = 0.0
    filtered["recomendacion"] = 0.0
    for index, row in filtered.iterrows():
        if index == index_noticia: continue
        vector = [float(i.strip()) for i in row["vector"][1:-1].split(",")]
        vector_noticia = [float(i.strip()) for i in str(vector_noticia)[1:-1].split(",")]
        similitud = cos_sim(vector, vector_noticia)
        filtered.loc[index, "similitud"] = similitud
        filtered.loc[index, "recomendacion"] = sorensen(str(row["etiquettas"]), etiquettas_noticia)
    sorted = filtered.sort_values(by='similitud', ascending=False).head(int(top_n_noticias.get()))
    recomendaciones = filtered.sort_values(by='recomendacion', ascending=False).head(int(top_n_noticias.get()))
    found_files = []
    for index, row in sorted.iterrows():
        found_files.append(f"{row['similitud']*100:.1f}% - {row['name']}")
    noticias_sim_var.set(found_files)
    found_files = []
    for index, row in recomendaciones.iterrows():
        found_files.append(f"{row['recomendacion']*100:.1f}% - {row['name']}")
    reco_var.set(found_files)
    buscar_btn["text"] = "Buscar"
    
def mostrarNoticias(event="dummy"):
    """
    It takes the current values of the two dropdown widgets and filters the dataframe to show only the
    rows that match those values
    
    :param event: the event that triggered the function (in this case, the selection of a value in the
    dropdown menu), defaults to dummy (optional)
    """
    global vector_df
    noticias_df = vector_df[(vector_df["medio"] == Medios_choices.get()) & (vector_df["categoria"] == Categ_choices.get())]
    noticias_var.set(noticias_df["name"].to_list())

def onArticleSelect(event):
    """
    If the user has selected an item in the listbox, then get the selected item, find the corresponding
    row in the dataframe, get the path from the row, and if the file exists, then read the file and
    display it in the textbox
    
    :param event: The event that triggered the callback
    :return: The path to the file
    """
    global vector_df
    if not list_noticias.curselection():
        return
    selected = list_noticias.get(list_noticias.curselection()[0])
    row = vector_df.loc[vector_df['name'] == selected]
    path = row["path"].to_list()[0]
    if os.path.isfile(path):
        with open(path, "r") as f:
            noticiaField.delete('1.0', END)
            noticiaField.insert('1.0',f.read())
    else:
        messagebox.showinfo("No podemos encontrar esta noticia")

def onSimSelect(event="dummy"):
    """
    It takes the selected item from the listbox, extracts the filename from it, finds the path to the
    file in the dataframe, and then opens the file and displays it in the textbox
    
    :param event: The event that triggered the function, defaults to dummy (optional)
    :return: The similarity between the selected news and the news that is being displayed in the
    textbox.
    """
    if not noticias_similares.curselection():
        return
    selected = noticias_similares.get(noticias_similares.curselection()[0])
    filename = selected[selected.find("-")+2::] # delete similarity before filename
    row = vector_df.loc[vector_df['name'] == filename]
    path = row["path"].to_list()[0]
    if os.path.isfile(path):
        with open(path, "r") as f:
            found_noticias.delete('1.0', END)
            found_noticias.insert('1.0',f.read())
    else:
        messagebox.showinfo("No podemos encontrar esta noticia")

def onRecoSelect(event="dummy"):
    """
    It takes the selected item from the listbox, finds the corresponding file in the dataframe, and then
    opens the file and displays it in the textbox
    
    :param event: The event that triggered the callback, defaults to dummy (optional)
    :return: The path to the file
    """
    if not noticias_reco.curselection():
        return
    selected = noticias_reco.get(noticias_reco.curselection()[0])
    filename = selected[selected.find("-")+2::] # delete similarity before filename
    row = vector_df.loc[vector_df['name'] == filename]
    path = row["path"].to_list()[0]
    if os.path.isfile(path):
        with open(path, "r") as f:
            found_noticias.delete('1.0', END)
            found_noticias.insert('1.0',f.read())
    else:
        messagebox.showinfo("No podemos encontrar esta noticia")

# Creating a GUI with a listbox and a combobox.
ttk.Label(clasiFrame, text="Periódico").grid(column=0, row=0,sticky=N)
Med = IntVar() 
Medios = ["20minutos", "elMundo", "elPais"]
Medios_choices =  ttk.Combobox(clasiFrame, textvariable=Med, state="readonly", values=Medios)
Medios_choices.current(0)
Medios_choices.bind("<<ComboboxSelected>>", mostrarNoticias)
Medios_choices.grid(column=0, row=1, sticky=(N,W))

ttk.Label(clasiFrame, text="Categoría ").grid(column=1, row=0, sticky=N)
Categ = IntVar()
Categorias = ["ciencia", "salud", "tecnologia"]
Categ_choices = ttk.Combobox(clasiFrame, textvariable=Categ, state="readonly", values=Categorias)
Categ_choices.bind("<<ComboboxSelected>>", mostrarNoticias)
Categ_choices.current(0)
Categ_choices.grid(column=1, row=1, sticky=N)

# Ranking
ttk.Label(clasiFrame, text="Noticias").grid(column=2, columnspan=2, row=0, sticky=W)
noticias_var = StringVar()
list_noticias = Listbox(clasiFrame, listvariable=noticias_var, height=5)
list_noticias.bind("<<ListboxSelect>>", onArticleSelect)
list_noticias.grid(column=2, columnspan=2, rowspan=3, row=1, sticky=(N,E,W,S))


ttk.Label(clasiFrame, text="Preview de la noticia:").grid(column=0, columnspan=2, row=3, sticky=N)

noticiaField = Text(clasiFrame, height=15)
noticiaField.grid(column=0, columnspan=2, row=3, sticky=(E,W))

min_size = 75
clasiFrame.columnconfigure(0, weight=1, minsize=min_size)
clasiFrame.columnconfigure(1, weight=1, minsize=min_size)
clasiFrame.columnconfigure(2, weight=1, minsize=min_size)
clasiFrame.columnconfigure(3, weight=1, minsize=min_size)

ttk.Label(clasiFrame, text="TOP-N:").grid(column=0, row=5, sticky=W)
# results select
top_n = IntVar()
top_n_choices = [3, 5, 10, 15, 20]
top_n_noticias = ttk.Combobox(clasiFrame, state="readonly", values=top_n_choices, width=5)
top_n_noticias.current(0)
top_n_noticias.grid(column=0, row=5, sticky=E)

ttk.Label(clasiFrame, text="Filtrar:").grid(column=1, row=5, sticky=W)
# filter select
filter = IntVar()
filter_choices = ["todos", "20minutos", "elMundo", "elPais"]
filter_noticias = ttk.Combobox(clasiFrame, state="readonly", values=filter_choices, width=10)
filter_noticias.current(0)
filter_noticias.grid(column=1, row=5, sticky=E)

# search Button
buscar_btn = ttk.Button(clasiFrame, text="Buscar", default="active", command=comparar)
buscar_btn.grid(column=2, columnspan=2, row=5, sticky=E)

found_noticias = Text(clasiFrame)
found_noticias.grid(column=0, columnspan=2, rowspan=6, row=6, sticky=(N,E,W))

ttk.Label(clasiFrame, text="Noticias similares").grid(column=2, columnspan=2, row=6, sticky=(N,E))
noticias_sim_var = StringVar()
noticias_similares = Listbox(clasiFrame, listvariable=noticias_sim_var, height=5)
noticias_similares.bind("<<ListboxSelect>>", onSimSelect)
noticias_similares.grid(column=2, columnspan=2, row=7, sticky=(N,E,W))

ttk.Label(clasiFrame, text="Recomendaciones").grid(column=2, columnspan=2, row=8, sticky=(N,E))
reco_var = StringVar()
noticias_reco = Listbox(clasiFrame, listvariable=reco_var, height=5)
noticias_reco.bind("<<ListboxSelect>>", onRecoSelect)
noticias_reco.grid(column=2, columnspan=2, row=9, sticky=(N,E,W))

min_size = 75
clasiFrame.columnconfigure(0, weight=1, minsize=min_size)
clasiFrame.columnconfigure(1, weight=1, minsize=min_size)
clasiFrame.columnconfigure(2, weight=1, minsize=min_size)
clasiFrame.columnconfigure(3, weight=1, minsize=min_size)

def cos_sim(a,b):
    """
    It takes two vectors, a and b, and returns the cosine of the angle between them
    
    :param a: the first vector
    :param b: the vector of the word we're looking at
    :return: The cosine similarity between two vectors.
    """
    return dot(a, b)/(norm(a)*norm(b))

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

def calculateSimilarity(df):
    """
    It takes a dataframe, loads a vectorizer, transforms the query into a vector, calculates the cosine
    similarity between the query vector and the vector of each row in the dataframe, and returns the
    dataframe with the cosine similarity added as a column
    
    :param df: the dataframe with the vectors
    :return: A dataframe with the similarity between the query and the documents.
    """
    vectorizer = pickle.load(open("vectorizer.file", 'rb'))
    query = stemming(removeStopwords(tokenize(query_input.get())))
    if not query: return
    consulta_vec = vectorizer.transform([query])
    dense = consulta_vec.todense()
    denselist = dense.tolist()
    for index, row in df.iterrows():
        vector = [float(i.strip()) for i in row["vector"][1:-1].split(",")]
        similitud = cos_sim(vector, denselist[0])
        df.loc[index, "similitud"] = similitud
    return df
                                                      
def buscar(event="dummy"):
    """
    It takes the query, filters the dataframe by the selected medium, calculates the similarity between
    the query and the documents, sorts the dataframe by similarity, and then updates the listbox with
    the top n results
    
    :param event: The event that triggered the function, defaults to dummy (optional)
    :return: the filtered dataframe.
    """
    global vector_df
    if query_input.get() == "":
        messagebox.showinfo("Introduzca la consulta", "Introduzca la consulta")
        return
    search_btn["text"] = "Calculando..."
    root.update()
    filtered = vector_df.copy()
    if filter_select.get() != "todos":
        filtered = vector_df[vector_df["medio"] == filter_select.get()].copy()
    filtered.loc[:,"similitud"] = 0.0
    filtered = calculateSimilarity(filtered)
    amount = top_n_select.current()
    sorted = filtered.sort_values(by='similitud', ascending=False).head(top_n_choices[amount])
    found_files = []
    for index, row in sorted.iterrows():
        found_files.append(f"{row['similitud']*100:.1f}% - {row['name']}")
    choicesvar.set(found_files)
    search_btn["text"] = "Buscar"

def onFileSelect(event):
    """
    If the user has selected a file in the listbox, then get the filename from the listbox, find the
    path to the file in the dataframe, and if the file exists, then open it and display it in the text
    field
    
    :param event: The event that triggered this function
    :return: the path of the file.
    """
    if not listbox.curselection():
        return
    global vector_df
    selected = listbox.get(listbox.curselection()[0])
    # delete similarity before filename
    filename = selected[selected.find("-")+2::]
    row = vector_df.loc[vector_df['name'] == filename]
    path = row["path"].to_list()[0]
    if os.path.isfile(path):
        with open(path, "r",encoding='latin-1') as f:
            textField.delete('1.0', END)
            textField.insert('1.0',f.read())
    else:
        messagebox.showinfo("No podemos encontrar esta noticia")
    

# Query Label
ttk.Label(busqFrame, text="Consulta:").grid(column=0, row=1, sticky=W)
                                                                                                     
# OQuery input
query = StringVar()
query_input = ttk.Entry(busqFrame, textvariable=query)
query_input.bind('<Return>', buscar)
query_input.grid(column=1, row=0, columnspan=5, sticky=(W, E))


ttk.Label(busqFrame, text="TOP-N:").grid(column=0, row=1, sticky=W)
# results select
top_n = IntVar()
top_n_choices = [3, 5, 10, 15, 20]
top_n_select = ttk.Combobox(busqFrame, textvariable=top_n, state="readonly", values=top_n_choices)
top_n_select.current(2)
top_n_select.grid(column=1, row=1, sticky=W)

ttk.Label(busqFrame, text="Filtrar:").grid(column=2, row=1, sticky=W)
# filter select
filter = IntVar()
filter_choices = ["todos", "20minutos", "elMundo", "elPais"]
filter_select = ttk.Combobox(busqFrame, state="readonly", values=filter_choices)
filter_select.current(0)
filter_select.grid(column=3, row=1, sticky=W)

# search Button
search_btn = ttk.Button(busqFrame, text="Buscar", default="active", command=buscar)
search_btn.grid(column=4, columnspan=2, row=1, sticky=E)

# Ranking
ttk.Label(busqFrame, text="Ranking:").grid(column=0, columnspan=2, row=3, sticky=W)
choicesvar = StringVar()
listbox = Listbox(busqFrame, listvariable=choicesvar)
listbox.grid(column=0, columnspan=2, row=4, sticky=(N,E,W))
listbox.bind("<<ListboxSelect>>", onFileSelect)

# Texto de la noticia
ttk.Label(busqFrame, text="Texto de la noticia:").grid(column=2, columnspan=4, row=4, sticky=W)

text_var = StringVar()
textField = Text(busqFrame)
textField.grid(column=2, columnspan=4, row=4, sticky=(N,E,W))

min_size = 75
busqFrame.columnconfigure(0, weight=1, minsize=min_size)
busqFrame.columnconfigure(1, weight=1, minsize=min_size)
busqFrame.columnconfigure(2, weight=1, minsize=min_size)
busqFrame.columnconfigure(3, weight=1, minsize=min_size)
busqFrame.columnconfigure(4, weight=1, minsize=min_size)
busqFrame.columnconfigure(5, weight=1, minsize=min_size)

for child in busqFrame.winfo_children(): 
    child.grid_configure(padx=5, pady=5)
    
# for child in clasiFrame.winfo_children(): 
#     child.grid_configure(padx=5, pady=5)
    
mostrarNoticias()

root.geometry("800x700")
root.title("Proyecto 21-22")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.mainloop()