"""
Ejemplo de cómo leer datos desde Firestore
Este script muestra cómo consultar y usar los datos subidos
"""

from firebase_admin import credentials, firestore, initialize_app
import os

FIREBASE_CREDENTIALS = "firebase-credentials.json"
COLECCION = "lecturas"

def inicializar_firebase():
    """Inicializa la conexión con Firebase"""
    if not os.path.exists(FIREBASE_CREDENTIALS):
        print(f"❌ ERROR: No se encontró '{FIREBASE_CREDENTIALS}'")
        return None
    
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        initialize_app(cred)
        db = firestore.client()
        print("✅ Conexión a Firebase establecida\n")
        return db
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def ejemplo_1_listar_todas_lecturas(db):
    """Ejemplo 1: Listar todas las lecturas"""
    print("📚 EJEMPLO 1: Listar todas las lecturas")
    print("="*60)
    
    lecturas_ref = db.collection(COLECCION)
    docs = lecturas_ref.stream()
    
    for doc in docs:
        data = doc.to_dict()
        print(f"\n📖 {doc.id}")
        print(f"   Autor: {data.get('autor', 'N/A')}")
        print(f"   Preguntas: {len(data.get('preguntas_vof', []))}")
        print(f"   Texto (primeros 100 chars): {data.get('texto', '')[:100]}...")

def ejemplo_2_obtener_lectura_especifica(db, nombre_lectura):
    """Ejemplo 2: Obtener una lectura específica"""
    print(f"\n\n📖 EJEMPLO 2: Obtener lectura '{nombre_lectura}'")
    print("="*60)
    
    doc_ref = db.collection(COLECCION).document(nombre_lectura)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        print(f"\n✅ Lectura encontrada:")
        print(f"   Autor: {data.get('autor')}")
        print(f"   Total preguntas: {len(data.get('preguntas_vof', []))}")
        
        # Mostrar las preguntas
        print(f"\n   Preguntas:")
        for i, pregunta in enumerate(data.get('preguntas_vof', [])[:3], 1):
            resp = "✓" if pregunta['respuesta'] else "✗"
            print(f"   {i}. [{pregunta['dificultad']}] {resp} {pregunta['afirmacion'][:50]}...")
        
        if len(data.get('preguntas_vof', [])) > 3:
            print(f"   ... y {len(data.get('preguntas_vof', [])) - 3} preguntas más")
    else:
        print(f"❌ No se encontró la lectura '{nombre_lectura}'")

def ejemplo_3_filtrar_preguntas_por_dificultad(db, nombre_lectura, dificultad):
    """Ejemplo 3: Filtrar preguntas por dificultad"""
    print(f"\n\n🎯 EJEMPLO 3: Preguntas de nivel '{dificultad}' en '{nombre_lectura}'")
    print("="*60)
    
    doc_ref = db.collection(COLECCION).document(nombre_lectura)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        preguntas_filtradas = [
            p for p in data.get('preguntas_vof', [])
            if p['dificultad'] == dificultad
        ]
        
        print(f"\n✅ Se encontraron {len(preguntas_filtradas)} preguntas de nivel '{dificultad}':\n")
        for i, pregunta in enumerate(preguntas_filtradas, 1):
            resp = "Verdadero" if pregunta['respuesta'] else "Falso"
            print(f"{i}. {pregunta['afirmacion']}")
            print(f"   Respuesta: {resp}\n")
    else:
        print(f"❌ No se encontró la lectura '{nombre_lectura}'")

def ejemplo_4_obtener_todas_preguntas_nivel(db, dificultad):
    """Ejemplo 4: Obtener todas las preguntas de un nivel de todas las lecturas"""
    print(f"\n\n🌍 EJEMPLO 4: Todas las preguntas de nivel '{dificultad}'")
    print("="*60)
    
    lecturas_ref = db.collection(COLECCION)
    docs = lecturas_ref.stream()
    
    todas_preguntas = []
    
    for doc in docs:
        data = doc.to_dict()
        preguntas_filtradas = [
            {**p, 'origen': doc.id}
            for p in data.get('preguntas_vof', [])
            if p['dificultad'] == dificultad
        ]
        todas_preguntas.extend(preguntas_filtradas)
    
    print(f"\n✅ Se encontraron {len(todas_preguntas)} preguntas de nivel '{dificultad}':\n")
    for i, pregunta in enumerate(todas_preguntas[:5], 1):
        resp = "✓" if pregunta['respuesta'] else "✗"
        print(f"{i}. [{pregunta['origen']}] {resp} {pregunta['afirmacion'][:60]}...")
    
    if len(todas_preguntas) > 5:
        print(f"\n... y {len(todas_preguntas) - 5} preguntas más")

def ejemplo_5_estadisticas_globales(db):
    """Ejemplo 5: Obtener estadísticas globales"""
    print(f"\n\n📊 EJEMPLO 5: Estadísticas Globales")
    print("="*60)
    
    lecturas_ref = db.collection(COLECCION)
    docs = lecturas_ref.stream()
    
    total_lecturas = 0
    total_preguntas = 0
    preguntas_por_nivel = {"fácil": 0, "intermedia": 0, "difícil": 0}
    
    for doc in docs:
        total_lecturas += 1
        data = doc.to_dict()
        preguntas = data.get('preguntas_vof', [])
        total_preguntas += len(preguntas)
        
        for pregunta in preguntas:
            nivel = pregunta['dificultad']
            if nivel in preguntas_por_nivel:
                preguntas_por_nivel[nivel] += 1
    
    print(f"\n✅ Estadísticas:")
    print(f"   📚 Total de lecturas: {total_lecturas}")
    print(f"   ❓ Total de preguntas: {total_preguntas}")
    print(f"\n   Preguntas por nivel:")
    for nivel, cantidad in sorted(preguntas_por_nivel.items()):
        porcentaje = (cantidad / total_preguntas * 100) if total_preguntas > 0 else 0
        print(f"   • {nivel}: {cantidad} ({porcentaje:.1f}%)")

def main():
    print("🔥 EJEMPLOS DE LECTURA DESDE FIRESTORE 🔥")
    print("="*60 + "\n")
    
    # Inicializar Firebase
    db = inicializar_firebase()
    if db is None:
        return
    
    # Ejecutar ejemplos
    ejemplo_1_listar_todas_lecturas(db)
    
    # Cambia estos valores según las lecturas que tengas
    ejemplo_2_obtener_lectura_especifica(db, "Amoxcalli, la casa de los libros")
    ejemplo_3_filtrar_preguntas_por_dificultad(db, "Amoxcalli, la casa de los libros", "fácil")
    ejemplo_4_obtener_todas_preguntas_nivel(db, "difícil")
    ejemplo_5_estadisticas_globales(db)
    
    print("\n" + "="*60)
    print("✨ Ejemplos completados")

if __name__ == "__main__":
    main()
