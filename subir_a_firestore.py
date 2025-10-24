"""
Script para subir lecturas y preguntas a Firestore
Estructura de Firestore:
lecturas/
  |- {nombre_lectura}/
     |- texto: string
     |- autor: string
     |- preguntas_vof: array[{afirmacion, respuesta, dificultad}]
"""

import json
import os
from firebase_admin import credentials, firestore, initialize_app

# === CONFIGURACIÓN ===
LECTURAS_DIR = "lecturas_finales"
BANCO_PREGUNTAS_JSON = "banco_verdadero_falso.json"
COLECCION = "lecturas"

# Inicializar Firebase
# IMPORTANTE: Necesitas tener un archivo de credenciales de Firebase
# Descárgalo desde: Firebase Console > Project Settings > Service Accounts
FIREBASE_CREDENTIALS = "firebase-credentials.json"

# Mapeo inverso de niveles
MAPEO_NIVELES = {
    "basico": "fácil",
    "intermedio": "intermedia",
    "avanzado": "difícil"
}

def inicializar_firebase():
    """Inicializa la conexión con Firebase"""
    if not os.path.exists(FIREBASE_CREDENTIALS):
        print(f"❌ ERROR: No se encontró el archivo de credenciales '{FIREBASE_CREDENTIALS}'")
        print("\n📝 Para obtener las credenciales:")
        print("1. Ve a Firebase Console: https://console.firebase.google.com/")
        print("2. Selecciona tu proyecto")
        print("3. Ve a Project Settings > Service Accounts")
        print("4. Click en 'Generate new private key'")
        print(f"5. Guarda el archivo como '{FIREBASE_CREDENTIALS}' en este directorio")
        return None
    
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        initialize_app(cred)
        db = firestore.client()
        print("✅ Conexión a Firebase establecida")
        return db
    except Exception as e:
        print(f"❌ Error al inicializar Firebase: {e}")
        return None

def extraer_titulo_y_autor(texto):
    """Extrae el título y autor del texto de la lectura"""
    lineas = texto.strip().split('\n')
    titulo = lineas[0].strip() if len(lineas) > 0 else "Sin título"
    autor = "Desconocido"
    
    # Buscar la línea que contiene "Autor:"
    for linea in lineas[:5]:  # Buscar en las primeras 5 líneas
        if linea.strip().startswith("Autor:"):
            autor = linea.replace("Autor:", "").strip()
            break
    
    # El texto completo es todo el contenido
    texto_completo = texto.strip()
    
    return titulo, autor, texto_completo

def cargar_preguntas():
    """Carga las preguntas desde el JSON y las organiza por origen"""
    with open(BANCO_PREGUNTAS_JSON, "r", encoding="utf-8") as f:
        banco = json.load(f)
    
    # Reorganizar por nombre de lectura
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
    """Normaliza el nombre del archivo para coincidir con el origen en el JSON"""
    # Quitar la extensión .txt
    nombre = nombre.replace(".txt", "")
    return nombre

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

def subir_lecturas(db):
    """Sube todas las lecturas a Firestore"""
    # Cargar preguntas
    print("\n📚 Cargando preguntas...")
    preguntas_por_lectura = cargar_preguntas()
    print(f"✅ Preguntas cargadas para {len(preguntas_por_lectura)} lecturas")
    
    # Obtener lista de archivos de texto
    archivos = [f for f in os.listdir(LECTURAS_DIR) if f.endswith('.txt')]
    print(f"\n📄 Se encontraron {len(archivos)} archivos de lecturas")
    
    lecturas_subidas = 0
    lecturas_fallidas = 0
    
    for archivo in archivos:
        nombre_lectura = normalizar_nombre_archivo(archivo)
        ruta_archivo = os.path.join(LECTURAS_DIR, archivo)
        
        try:
            # Leer el archivo
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
            
            # Extraer título y autor
            titulo, autor, texto = extraer_titulo_y_autor(contenido)
            
            # Obtener preguntas (con búsqueda flexible)
            preguntas = buscar_preguntas_por_nombre(nombre_lectura, preguntas_por_lectura)
            
            if not preguntas:
                print(f"⚠️  '{nombre_lectura}': No se encontraron preguntas")
                # Buscar nombres similares
                nombres_disponibles = list(preguntas_por_lectura.keys())
                print(f"   Nombres disponibles en el JSON: {nombres_disponibles}")
            
            # Crear documento en Firestore
            documento = {
                "texto": texto,
                "autor": autor,
                "preguntas_vof": preguntas
            }
            
            # Subir a Firestore usando el título como ID del documento
            db.collection(COLECCION).document(titulo).set(documento)
            
            print(f"✅ '{titulo}' subida correctamente ({len(preguntas)} preguntas)")
            lecturas_subidas += 1
            
        except Exception as e:
            print(f"❌ Error procesando '{nombre_lectura}': {e}")
            lecturas_fallidas += 1
    
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN:")
    print(f"   ✅ Lecturas subidas: {lecturas_subidas}")
    print(f"   ❌ Lecturas fallidas: {lecturas_fallidas}")
    print(f"{'='*60}")

def main():
    print("🔥 SUBIDA DE LECTURAS A FIRESTORE 🔥")
    print("="*60)
    
    # Inicializar Firebase
    db = inicializar_firebase()
    if db is None:
        return
    
    # Verificar que existan los archivos necesarios
    if not os.path.exists(LECTURAS_DIR):
        print(f"❌ ERROR: No se encontró el directorio '{LECTURAS_DIR}'")
        return
    
    if not os.path.exists(BANCO_PREGUNTAS_JSON):
        print(f"❌ ERROR: No se encontró el archivo '{BANCO_PREGUNTAS_JSON}'")
        return
    
    # Subir lecturas
    subir_lecturas(db)
    
    print("\n✨ Proceso completado")

if __name__ == "__main__":
    main()
