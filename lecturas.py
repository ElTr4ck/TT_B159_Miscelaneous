import os
import requests
import img2pdf
import subprocess

# Carpeta de salida
OUT_DIR = "libro_paginas_cuarto"

PDF_PATH = os.path.join(OUT_DIR, "libro_cuarto.pdf")
OUTPUT_PDF = os.path.join(OUT_DIR, "libro_cuarto_ocr.pdf")
os.makedirs(OUT_DIR, exist_ok=True)

# URL base del libro
BASE_URL = "https://libros.conaliteg.gob.mx/2024/c/P4MLA/{:03d}.jpg"

# Rango de páginas (1 a 249)
for i in range(1, 250):  # 250 no incluido
    url = BASE_URL.format(i)
    nombre_archivo = os.path.join(OUT_DIR, f"pagina_{i:03d}.jpg")
    if os.path.exists(nombre_archivo):
        print(f"Saltando {nombre_archivo}, ya existe.")
        continue
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            with open(nombre_archivo, "wb") as f:
                f.write(resp.content)
            print(f"Descargada página {i:03d}")
        else:
            print(f"No encontrada {url} (status {resp.status_code})")
    except Exception as e:
        print(f"Error en {url}: {e}")
        continue

# Crear PDF a partir de las imágenes descargadas
imagenes = sorted([
    os.path.join(OUT_DIR, f) for f in os.listdir(OUT_DIR) if f.endswith(".jpg")
])

with open(PDF_PATH, "wb") as f:
    f.write(img2pdf.convert(imagenes))

# Corre OCR con idioma español
subprocess.run([
    "ocrmypdf", "--language", "spa", "--force-ocr", PDF_PATH, OUTPUT_PDF
])

print(f"OCR terminado, archivo generado: {OUTPUT_PDF}")