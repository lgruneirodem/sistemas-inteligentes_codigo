from tkinter import *
from tkinter import ttk

root = Tk()
tabs = ttk.Notebook(root)
tabs.pack(fill=BOTH, expand=TRUE)
busqFrame = ttk.Frame(tabs)
clasiFrame = ttk.Frame(tabs)
tabs.add(busqFrame, text="Búsqueda de noticias")
tabs.add(clasiFrame, text="Comparación de noticias")

def buscar():
    pass

# Query Label
ttk.Label(busqFrame, text="Consulta:").grid(column=0, row=0, sticky=W)
# OQuery input
query = StringVar()
query_input = ttk.Entry(busqFrame, textvariable=query)
query_input.grid(column=1, row=0, columnspan=5, sticky=(W, E))


ttk.Label(busqFrame, text="TOP-N:").grid(column=0, row=1, sticky=W)
# results select
top_n = IntVar()
top_n_choices = [1, 2, 3]
top_n_select = ttk.Combobox(busqFrame, textvariable=top_n, state="readonly", values=top_n_choices).grid(column=1, row=1, sticky=W)

ttk.Label(busqFrame, text="Filtrar:").grid(column=2, row=1, sticky=W)
# filter select
filter = IntVar()
filter_choices = ["20Min", "ElMundo", "ElPais"]
filter_select = ttk.Combobox(busqFrame, textvariable=filter, state="readonly", values=filter_choices).grid(column=3, row=1, sticky=W)

# search Button
ttk.Button(busqFrame, text="Buscar", default="active", command=buscar).grid(column=4, columnspan=2, row=1, sticky=E)


# Ranking
ttk.Label(busqFrame, text="Ranking:").grid(column=0, columnspan=2, row=3, sticky=W)
choices = ["1.txt", "2.txt", "3.txt"]
choicesvar = StringVar(value=choices)
listbox = Listbox(busqFrame, listvariable=choicesvar).grid(column=0, columnspan=2, row=4, sticky=(N,E,W))

# Texto de la noticia
ttk.Label(busqFrame, text="Texto de la noticia:").grid(column=2, columnspan=4, row=3, sticky=W)

Text(busqFrame).grid(column=2, columnspan=4, row=4, sticky=(N,E,W))

min_size = 75
busqFrame.columnconfigure(0, weight=1, minsize=min_size)
busqFrame.columnconfigure(1, weight=1, minsize=min_size)
busqFrame.columnconfigure(2, weight=1, minsize=min_size)
busqFrame.columnconfigure(3, weight=1, minsize=min_size)
busqFrame.columnconfigure(4, weight=1, minsize=min_size)
busqFrame.columnconfigure(5, weight=1, minsize=min_size)

for child in busqFrame.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

root.geometry("600x400")
root.title("Proyecto 21-22")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.mainloop()