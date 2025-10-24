# Normaliza un JSON generado como respuesta de la IA y lo concatena a un archivo final
import json
import os
import re

INPUT_FILE = "banco_ia_analiza.txt"
OUTPUT_JSON = "banco_verdadero_falso.json"

# === Mapeo de niveles ===
MAPEO_NIVELES = {
    "fácil": "basico",
    "intermedia": "intermedio",
    "difícil": "avanzado"
}

# === 1. Leer el archivo JSON de salida si existe ===
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        banco_preguntas = json.load(f)
else:
    # Inicializar estructura si no existe
    banco_preguntas = {
        "basico": [],
        "intermedio": [],
        "avanzado": []
    }

# === 2. Cargar el archivo con todas las lecturas ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    contenido = f.read()

# Parsear usando un enfoque más robusto
# Buscar el patrón: "Nombre": "```json...```",
# El patrón captura hasta el cierre de ```
patron = r'"([^"]+)":\s*"(```json.*?```)"'
matches = re.findall(patron, contenido, re.DOTALL)

lecturas_dict = {}
for nombre, json_str in matches:
    lecturas_dict[nombre] = json_str

# === 3. Procesar cada lectura ===
total_procesadas = 0
for nombre_lectura, json_mal_formateado in lecturas_dict.items():
    # Limpiar el JSON mal formateado
    # Decodificar todos los escapes: \n, \", etc.
    try:
        # Usar json.loads dos veces: primero para decodificar los escapes de la string
        json_decodificado = json.loads('"' + json_mal_formateado + '"')
        json_limpio = json_decodificado.replace("```json\n", "").replace("\n```", "").replace("```json", "").replace("```", "")
    except Exception as e1:
        # Si falla, intentar el método directo
        json_limpio = json_mal_formateado.replace("```json\\n", "").replace("\\n```", "").replace("\\n", "\n").replace('\\"', '"')
    
    try:
        # Cargar JSON de entrada
        data = json.loads(json_limpio)
        
        # Normalizar y agregar preguntas
        for item in data["preguntas"]:
            nivel_original = item["nivel"]
            nivel_normalizado = MAPEO_NIVELES.get(nivel_original, "basico")
            pregunta = item["pregunta"].strip()
            respuesta_str = item["respuesta_correcta"].strip()
            
            # Convertir respuesta a booleano
            respuesta_bool = respuesta_str.lower() == "verdadero" or respuesta_str.lower() == "true"
            
            # Crear entrada normalizada
            entrada_normalizada = {
                "afirmacion": pregunta,
                "respuesta": respuesta_bool,
                "origen": nombre_lectura
            }
            
            # Agregar al nivel correspondiente
            banco_preguntas[nivel_normalizado].append(entrada_normalizada)
        
        total_procesadas += 1
        print(f"✅ Procesada: {nombre_lectura} ({len(data['preguntas'])} preguntas)")
    
    except Exception as e:
        print(f"❌ Error procesando '{nombre_lectura}': {e}")

# === 4. Guardar el JSON actualizado ===
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(banco_preguntas, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"✅ Todas las preguntas normalizadas y guardadas en {OUTPUT_JSON}")
print(f"   - Lecturas procesadas: {total_procesadas}")
print(f"   - Básico: {len(banco_preguntas['basico'])} preguntas")
print(f"   - Intermedio: {len(banco_preguntas['intermedio'])} preguntas")
print(f"   - Avanzado: {len(banco_preguntas['avanzado'])} preguntas")
print(f"{'='*60}")