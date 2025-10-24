"""
Script para verificar los datos antes de subirlos a Firestore
Muestra un preview de cómo se verán los documentos en Firestore
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
    """Extrae el título y autor del texto de la lectura"""
    lineas = texto.strip().split('\n')
    titulo = lineas[0].strip() if len(lineas) > 0 else "Sin título"
    autor = "Desconocido"
    
    for linea in lineas[:5]:
        if linea.strip().startswith("Autor:"):
            autor = linea.replace("Autor:", "").strip()
            break
    
    texto_completo = texto.strip()
    return titulo, autor, texto_completo

def cargar_preguntas():
    """Carga las preguntas desde el JSON y las organiza por origen"""
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

def normalizar_nombre_archivo(nombre):
    """Normaliza el nombre del archivo"""
    return nombre.replace(".txt", "")

def buscar_preguntas_por_nombre(nombre_lectura, preguntas_por_lectura):
    """Busca las preguntas de una lectura, siendo flexible con mayúsculas/minúsculas"""
    # Primero intentar búsqueda exacta
    if nombre_lectura in preguntas_por_lectura:
        return preguntas_por_lectura[nombre_lectura]
    
    # Búsqueda case-insensitive
    nombre_lower = nombre_lectura.lower()
    for nombre_key, preguntas in preguntas_por_lectura.items():
        if nombre_key.lower() == nombre_lower:
            return preguntas
    
    return []

def verificar_datos():
    """Verifica y muestra un preview de los datos"""
    print("🔍 VERIFICACIÓN DE DATOS PARA FIRESTORE")
    print("="*70)
    
    # Cargar preguntas
    print("\n📚 Cargando preguntas del JSON...")
    preguntas_por_lectura = cargar_preguntas()
    
    print(f"\n✅ Lecturas encontradas en el JSON:")
    for nombre, preguntas in preguntas_por_lectura.items():
        niveles = {}
        for p in preguntas:
            dif = p["dificultad"]
            niveles[dif] = niveles.get(dif, 0) + 1
        
        print(f"   • {nombre}:")
        for nivel, cant in sorted(niveles.items()):
            print(f"     - {nivel}: {cant} preguntas")
    
    # Obtener archivos de texto
    print(f"\n📄 Archivos en '{LECTURAS_DIR}/':")
    archivos = [f for f in os.listdir(LECTURAS_DIR) if f.endswith('.txt')]
    
    if not archivos:
        print("   ❌ No se encontraron archivos .txt")
        return
    
    for archivo in archivos:
        print(f"   • {archivo}")
    
    # Verificar coincidencias
    print(f"\n🔗 Verificando coincidencias...")
    for archivo in archivos:
        nombre_lectura = normalizar_nombre_archivo(archivo)
        ruta_archivo = os.path.join(LECTURAS_DIR, archivo)
        
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        titulo, autor, texto = extraer_titulo_y_autor(contenido)
        preguntas = buscar_preguntas_por_nombre(nombre_lectura, preguntas_por_lectura)
        
        print(f"\n{'─'*70}")
        print(f"📖 Archivo: {archivo}")
        print(f"   Título extraído: {titulo}")
        print(f"   Autor extraído: {autor}")
        print(f"   Nombre normalizado: {nombre_lectura}")
        print(f"   Caracteres de texto: {len(texto)}")
        print(f"   Preguntas encontradas: {len(preguntas)}")
        
        if len(preguntas) == 0:
            print(f"   ⚠️  ADVERTENCIA: No se encontraron preguntas para '{nombre_lectura}'")
            print(f"   Nombres disponibles en JSON: {list(preguntas_por_lectura.keys())}")
        else:
            print(f"   ✅ Coincidencia encontrada")
            
            # Mostrar preview de preguntas
            print(f"\n   Preview de preguntas:")
            for i, p in enumerate(preguntas[:3], 1):
                resp = "✓" if p["respuesta"] else "✗"
                print(f"     {i}. [{p['dificultad']}] {resp} {p['afirmacion'][:60]}...")
            
            if len(preguntas) > 3:
                print(f"     ... y {len(preguntas) - 3} preguntas más")
    
    print(f"\n{'='*70}")
    print("✅ Verificación completada")
    print("\n💡 Si todo se ve bien, ejecuta: python3 subir_a_firestore.py")

if __name__ == "__main__":
    verificar_datos()
