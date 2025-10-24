import os
import json
from openai import OpenAI

# Carga tu API key desde variables de entorno
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt base para limpiar lecturas OCR
PROMPT_LIMPIEZA = """Eres un corrector de textos breves extraídos mediante OCR.
Corrige errores de ortografía, puntuación y coherencia.
No cambies el significado ni resumas el texto.
Devuelve solo el texto limpio.
Texto:
"""

# Prompt base para generar preguntas de verdadero/falso
PROMPT_PREGUNTAS = """Eres un creador de ejercicios de comprensión lectora para niños de primaria.
Lee el texto siguiente y genera exactamente 8 preguntas de verdadero o falso:
- 4 fáciles (respuestas literales del texto)
- 2 intermedias (inferencia directa)
- 2 difíciles (requieren interpretación o deducción)
Devuelve el resultado en formato JSON con la siguiente estructura:

{
  "preguntas": [
    {"nivel": "fácil", "pregunta": "...", "respuesta_correcta": "Verdadero" o "Falso"},
    {"nivel": "intermedia", "pregunta": "...", "respuesta_correcta": "..."},
    {"nivel": "difícil", "pregunta": "...", "respuesta_correcta": "..."}
  ]
}

Texto:
"""

def limpiar_lectura(texto):
    """Corrige texto OCR."""
    prompt = PROMPT_LIMPIEZA + texto
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

def generar_preguntas(texto):
    """Genera preguntas en formato JSON."""
    prompt = PROMPT_PREGUNTAS + texto
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000
    )
    contenido = response.choices[0].message.content.strip()

    # Intentamos convertir directamente a JSON
    try:
        data = json.loads(contenido)
        return data.get("preguntas", [])
    except json.JSONDecodeError:
        print("⚠️ Advertencia: respuesta no en formato JSON, se guardará como texto plano.")
        return [{"nivel": "error", "pregunta": contenido, "respuesta_correcta": ""}]

def main():
    # Cargar lecturas desde archivos .txt en la carpeta 'lecturas_txt'
    def cargar_lecturas_desde_directorio(dir_path="lecturas_txt"):
        lecturas = []
        if not os.path.isdir(dir_path):
            print(f"⚠️ Directorio '{dir_path}' no encontrado")
            exit(1)

        archivos = sorted([f for f in os.listdir(dir_path) if f.lower().endswith('.txt')])
        if not archivos:
            print(f"⚠️ No se encontraron archivos .txt en '{dir_path}'.")
            return []
    
        for nombre in archivos:
            ruta = os.path.join(dir_path, nombre)
            try:
                with open(ruta, 'r', encoding='utf-8') as fh:
                    contenido = fh.read()
            except UnicodeDecodeError:
                try:
                    with open(ruta, 'r', encoding='latin-1') as fh:
                        contenido = fh.read()
                except Exception as e:
                    print(f"⚠️ Error leyendo '{ruta}': {e}")
                    continue
            except Exception as e:
                print(f"⚠️ Error leyendo '{ruta}': {e}")
                continue

            if contenido and contenido.strip():
                lecturas.append(contenido.strip())

        return lecturas

    lecturas_ocr = cargar_lecturas_desde_directorio()

    lecturas_limpias = []
    banco_preguntas = []

    for i, texto in enumerate(lecturas_ocr, 1):
        print(f"\n🧹 Procesando lectura {i}...")
        lectura_limpia = limpiar_lectura(texto)
        lecturas_limpias.append(lectura_limpia)

        print("🧠 Generando preguntas...")
        preguntas = generar_preguntas(lectura_limpia)
        banco_preguntas.append({
            "id": i,
            "lectura": lectura_limpia,
            "preguntas": preguntas
        })

    # Guardar textos limpios
    with open("lecturas_limpias.txt", "w", encoding="utf-8") as f:
        for i, texto in enumerate(lecturas_limpias, 1):
            f.write(f"--- Lectura {i} ---\n{texto}\n\n")

    # Guardar banco de preguntas
    with open("banco_preguntas.json", "w", encoding="utf-8") as f:
        json.dump(banco_preguntas, f, ensure_ascii=False, indent=2)

    print("\n✅ Lecturas guardadas en 'lecturas_limpias.txt'")
    print("✅ Banco de preguntas guardado en 'banco_preguntas.json'")

if __name__ == "__main__":
    main()
