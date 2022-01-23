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
    if not list_noticias.curselection():
        messagebox.showinfo("Porfavor elige una noticia", "Porfavor elige una noticia")
        return
    buscar_btn["text"] = "Calculando..."
    global vector_df
    selected = list_noticias.get(list_noticias.curselection()[0])
    row = vector_df[(vector_df['name'] == selected) 
        & (vector_df["medio"] == Medios_choices.get()) 
        & (vector_df["categoria"] == Categ_choices.get())]
    index_noticia = row.index.tolist()[0]
    vector_noticia = row["vector"].to_list()[0]
    etiquettas_noticia = row["etiquettas"].to_list()[0]
    vector_df["similitud"] = 0.0
    vector_df["recomendacion"] = 0.0
    for index, row in vector_df.iterrows():
        if index == index_noticia: continue
        vector = [float(i.strip()) for i in row["vector"][1:-1].split(",")]
        vector_noticia = [float(i.strip()) for i in str(vector_noticia)[1:-1].split(",")]
        similitud = cos_sim(vector, vector_noticia)
        vector_df.loc[index, "similitud"] = similitud
        vector_df.loc[index, "recomendacion"] = sorensen(str(row["etiquettas"]), etiquettas_noticia)
    filtered = vector_df
    if filter_noticias.get() != "todos":
        filtered = vector_df[vector_df["medio"] == filter_noticias.get()]
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
    global vector_df
    noticias_df = vector_df[(vector_df["medio"] == Medios_choices.get()) & (vector_df["categoria"] == Categ_choices.get())]
    noticias_var.set(noticias_df["name"].to_list())

def onArticleSelect(event):
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
filter_choices = ["todos", "20minutes", "elMundo", "elPais"]
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
    return dot(a, b)/(norm(a)*norm(b))

def tokenize(x):
    return RegexpTokenizer(r'\w+').tokenize(x.lower())

def removeStopwords(x):
    with open("stopWords_es.txt") as f:
        text = f.read()
        prohibitedWords = text.split("\n")
        return [word for word in x if not word in prohibitedWords]

def stemming(x):
    stemmer = SnowballStemmer(language="spanish")
    return ' '.join([stemmer.stem(word) for word in x])

def calculateSimilarity(df):
    vectorizer = pickle.load(open("vectorizer.file", 'rb'))
    query = stemming(removeStopwords(tokenize(query_input.get())))
    if query == "": return
    consulta_vec = vectorizer.transform([query])
    dense = consulta_vec.todense()
    denselist = dense.tolist()
    for index, row in df.iterrows():
        vector = [float(i.strip()) for i in row["vector"][1:-1].split(",")]
        similitud = cos_sim(vector, denselist[0])
        df.loc[index, "similitud"] = similitud
    return df
                                                      
def buscar(event="dummy"):
    global vector_df
    if query_input.get() == "":
        messagebox.showinfo("Introduzca la consulta", "Introduzca la consulta")
        return
    search_btn["text"] = "Calculando..."
    vector_df["similitud"] = 0.0
    vector_df = calculateSimilarity(vector_df)
    amount = top_n_select.current()
    filtered = vector_df
    if filter_select.get() != "todos":
        filtered = vector_df[vector_df["medio"] == filter_select.get()]
    sorted = filtered.sort_values(by='similitud', ascending=False).head(top_n_choices[amount])
    found_files = []
    for index, row in sorted.iterrows():
        found_files.append(f"{row['similitud']*100:.1f}% - {row['name']}")
    choicesvar.set(found_files)
    search_btn["text"] = "Buscar"

def onFileSelect(event):
    if not listbox.curselection():
        return
    global vector_df
    selected = listbox.get(listbox.curselection()[0])
    # delete similarity before filename
    filename = selected[selected.find("-")+2::]
    row = vector_df.loc[vector_df['name'] == filename]
    path = row["path"].to_list()[0]
    if os.path.isfile(path):
        with open(path, "r") as f:
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
filter_choices = ["todos", "20Min", "elMundo", "elPais"]
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