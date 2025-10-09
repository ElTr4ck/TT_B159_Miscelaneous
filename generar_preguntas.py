import os
import json
from openai import OpenAI

# Inicializa el cliente
client = OpenAI()

# Carpeta con las lecturas
LECTURAS_DIR = "lecturas_txt"
OUT_FILE = "banco_preguntas.json"

# Parámetros
N_PREGUNTAS = 6  # puedes ajustarlo

def generar_preguntas(nombre_lectura, texto):
    """Genera preguntas de opción múltiple con GPT-4o-mini"""
    prompt = f"""
Eres un generador automático de exámenes escolares.
Tu tarea es crear {N_PREGUNTAS} preguntas de opción múltiple sobre la siguiente lectura.

Instrucciones:
- Crea preguntas claras y relevantes sobre el contenido.
- Cada pregunta debe tener 4 opciones (A, B, C, D).
- Marca la respuesta correcta.
- Toma en cuenta que los textos fueron extraidos mediante OCR, por lo que puede haber errores tipográficos.
- Genera solo preguntas que puedan ser respondidas con la información del texto.
- En caso que la lectura sea muy corta, genera {N_PREGUNTAS - 4} preguntas o genera ERROR si no puedes sacar ninguna pregunta.
- Responde estrictamente en formato JSON con esta estructura:

{{
  "lectura": "{nombre_lectura}",
  "preguntas": [
    {{
      "pregunta": "...",
      "opciones": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "respuesta_correcta": "B"
    }},
    ...
  ]
}}

Lectura:
\"\"\"
{texto}
\"\"\"
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800
    )

    # Intentar parsear el JSON
    try:
        content = response.choices[0].message.content

        # 👇 Limpieza del bloque Markdown (caso típico: ```json {...} ```)
        if content.startswith("```"):
            content = content.strip().strip("`")
            if content.lower().startswith("json"):
                content = content[4:].strip()

        data = json.loads(content)
        return data

    except Exception as e:
        print(f"⚠️ Error al parsear JSON para {nombre_lectura}: {e}")
        print("Respuesta cruda del modelo:\n", response.choices[0].message.content)
        return None


def main():
    banco = []

    for filename in os.listdir(LECTURAS_DIR):
        if not filename.endswith(".txt"):
            continue
        lectura_name = os.path.splitext(filename)[0]
        path = os.path.join(LECTURAS_DIR, filename)
        print(f"📘 Generando preguntas para: {lectura_name}")

        with open(path, "r", encoding="utf-8") as f:
            texto = f.read()

        data = generar_preguntas(lectura_name, texto)
        if data:
            banco.append(data)

    # Guardar todo en un JSON
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(banco, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Banco de preguntas guardado en {OUT_FILE}")


if __name__ == "__main__":
    main()
