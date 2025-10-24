"""
Script de ejemplo - Muestra cómo se vería un documento en Firestore
Este script NO sube nada, solo muestra un preview en JSON
"""

import json
import os

LECTURAS_DIR = "lecturas_finales"
BANCO_PREGUNTAS_JSON = "banco_verdadero_falso.json"

MAPEO_NIVELES = {
    "basico": "fácil",
    "intermedio": "intermedia",
    "avanzado": "difícil"
}

def extraer_titulo_y_autor(texto):
    lineas = texto.strip().split('\n')
    titulo = lineas[0].strip() if len(lineas) > 0 else "Sin título"
    autor = "Desconocido"
    
    for linea in lineas[:5]:
        if linea.strip().startswith("Autor:"):
            autor = linea.replace("Autor:", "").strip()
            break
    
    return titulo, autor, texto.strip()

def cargar_preguntas():
    with open(BANCO_PREGUNTAS_JSON, "r", encoding="utf-8") as f:
        banco = json.load(f)
    
    preguntas_por_lectura = {}
    
    for nivel, preguntas in banco.items():
        dificultad = MAPEO_NIVELES[nivel]
        for pregunta in preguntas:
            origen = pregunta["origen"]
            if origen not in preguntas_por_lectura:
                preguntas_por_lectura[origen] = []
            
            preguntas_por_lectura[origen].append({
                "afirmacion": pregunta["afirmacion"],
                "respuesta": pregunta["respuesta"],
                "dificultad": dificultad
            })
    
    return preguntas_por_lectura

def buscar_preguntas_por_nombre(nombre_lectura, preguntas_por_lectura):
    if nombre_lectura in preguntas_por_lectura:
        return preguntas_por_lectura[nombre_lectura]
    
    nombre_lower = nombre_lectura.lower()
    for nombre_key, preguntas in preguntas_por_lectura.items():
        if nombre_key.lower() == nombre_lower:
            return preguntas
    
    return []

def generar_preview():
    print("📋 PREVIEW DE DOCUMENTOS FIRESTORE")
    print("="*70)
    
    preguntas_por_lectura = cargar_preguntas()
    
    # Tomar el primer archivo como ejemplo
    archivos = [f for f in os.listdir(LECTURAS_DIR) if f.endswith('.txt')]
    
    if not archivos:
        print("❌ No se encontraron archivos")
        return
    
    # Usar el primer archivo
    archivo = archivos[0]
    nombre_lectura = archivo.replace(".txt", "")
    ruta_archivo = os.path.join(LECTURAS_DIR, archivo)
    
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()
    
    titulo, autor, texto = extraer_titulo_y_autor(contenido)
    preguntas = buscar_preguntas_por_nombre(nombre_lectura, preguntas_por_lectura)
    
    documento = {
        "texto": texto,
        "autor": autor,
        "preguntas_vof": preguntas
    }
    
    print(f"\n📖 Ejemplo de documento para: {titulo}")
    print(f"\nRuta en Firestore: lecturas/{titulo}")
    print(f"\n{'─'*70}")
    print("\nContenido del documento (JSON):\n")
    
    # Crear una versión resumida para el preview
    documento_preview = {
        "texto": texto[:200] + "..." if len(texto) > 200 else texto,
        "autor": autor,
        "preguntas_vof": preguntas[:2] + [{"...": f"y {len(preguntas)-2} preguntas más"}] if len(preguntas) > 2 else preguntas
    }
    
    print(json.dumps(documento_preview, indent=2, ensure_ascii=False))
    
    print(f"\n{'─'*70}")
    print(f"\n📊 Estadísticas:")
    print(f"   • Caracteres de texto: {len(texto)}")
    print(f"   • Total de preguntas: {len(preguntas)}")
    
    niveles = {}
    for p in preguntas:
        dif = p["dificultad"]
        niveles[dif] = niveles.get(dif, 0) + 1
    
    for nivel, cant in sorted(niveles.items()):
        print(f"   • Preguntas {nivel}: {cant}")
    
    print(f"\n{'='*70}")
    print("\n💾 Para subir todos los documentos a Firestore:")
    print("   1. Instala: pip install firebase-admin")
    print("   2. Descarga las credenciales de Firebase")
    print("   3. Ejecuta: python3 subir_a_firestore.py")

if __name__ == "__main__":
    generar_preview()
