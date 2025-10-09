import boto3
import time
import json
import os

# === CONFIGURACIÓN ===
S3_BUCKET = "mi-libro-cuarto"      # tu bucket
DOCUMENT  = "libro_cuarto.pdf"               # nombre del PDF en S3
LECTURAS_JSON = "lecturas_cuarto.json"       # tu JSON con rangos
OUT_DIR = "lecturas_txt"
os.makedirs(OUT_DIR, exist_ok=True)

# === CLIENTE TEXTRACT ===
textract = boto3.client("textract", region_name="us-east-1")

# === 1. Iniciar la tarea de detección de texto ===
print("Iniciando análisis de documento...")
response = textract.start_document_text_detection(
    DocumentLocation={"S3Object": {"Bucket": S3_BUCKET, "Name": DOCUMENT}}
)
job_id = response["JobId"]
print(f"Job iniciado: {job_id}")

# === 2. Esperar hasta que termine ===
while True:
    status = textract.get_document_text_detection(JobId=job_id)
    job_status = status["JobStatus"]
    print("Estado:", job_status)
    if job_status in ["SUCCEEDED", "FAILED"]:
        break
    time.sleep(5)

if job_status == "FAILED":
    raise RuntimeError("❌ El análisis de Textract falló.")

# === 3. Obtener todos los resultados ===
pages = []
next_token = None
print("Descargando resultados...")
while True:
    if next_token:
        response = textract.get_document_text_detection(JobId=job_id, NextToken=next_token)
    else:
        response = textract.get_document_text_detection(JobId=job_id)
    pages.extend(response["Blocks"])
    next_token = response.get("NextToken")
    if not next_token:
        break

# === 4. Separar texto por página ===
print("Procesando texto por página...")
page_texts = {}
for block in pages:
    if block["BlockType"] == "LINE":
        page = block["Page"]
        text = block["Text"]
        page_texts.setdefault(page, []).append(text)

# Convertir listas en texto concatenado
for page in page_texts:
    page_texts[page] = "\n".join(page_texts[page])

# === 5. Cargar JSON de lecturas ===
with open(LECTURAS_JSON, "r", encoding="utf-8") as f:
    lecturas = json.load(f)

# === 6. Extraer texto por lectura ===
for lectura in lecturas:
    nombre = lectura["lectura"]
    paginas = lectura["paginas"]
    if "-" in paginas:
        start, end = map(int, paginas.split("-"))
    else:
        start = end = int(paginas)

    texto_lectura = ""
    for p in range(start, end + 1):
        if p in page_texts:
            texto_lectura += page_texts[p] + "\n\n"
        else:
            print(f"⚠️ Página {p} sin texto detectado.")

    # Guardar cada lectura en archivo .txt
    out_path = os.path.join(OUT_DIR, f"{nombre}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(texto_lectura.strip())

    print(f"✅ Guardado: {out_path}")

print("\n🎉 Extracción completa. Archivos listos en", OUT_DIR)
