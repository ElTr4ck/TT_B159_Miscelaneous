import pdfplumber
import json, os

'''lecturas = {
    "lectura1.txt": (5, 12),
    "lectura2.txt": (13, 20),
    "lectura3.txt": (21, 28),
}
'''

# Cargar las lecturas desde un archivo externo JSON
lecturas = {}
OUTPUT_DIR = "textos_lecturas"
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open("lecturas_cuarto.json", "r", encoding="utf-8") as f:
    lecturas = json.load(f)

with pdfplumber.open(r"/home/eltr4ck/pythonUtils/libro_paginas_cuarto/libro_cuarto_ocr.pdf") as pdf:
    for item in lecturas:
        nombre = item["lectura"] + ".txt"
        paginas = item["paginas"].split("-")
        ini = int(paginas[0])
        fin = int(paginas[1])
        with open(os.path.join(OUTPUT_DIR, nombre), "w", encoding="utf-8") as f:
            for i in range(ini-1, fin):  # pdfplumber es 0-index
                page = pdf.pages[i]
                text = page.extract_text()
                if text:
                    f.write(text + "\n\n")
        print(f"{nombre} generado.")
