# 🔥 Scripts para Firestore - Guía Rápida

## 📁 Archivos creados:

1. **`subir_a_firestore.py`** - Script principal para subir lecturas a Firestore
2. **`verificar_datos_firestore.py`** - Verifica los datos antes de subir
3. **`preview_firestore.py`** - Muestra un preview de cómo se verán los documentos
4. **`ejemplo_leer_firestore.py`** - Ejemplos de cómo leer datos desde Firestore
5. **`README_FIRESTORE.md`** - Documentación completa

## ⚡ Flujo de trabajo:

```bash
# Paso 1: Ver un preview
python3 preview_firestore.py

# Paso 2: Verificar datos
python3 verificar_datos_firestore.py

# Paso 3: Instalar Firebase (solo la primera vez)
pip install firebase-admin

# Paso 4: Configurar credenciales
# - Descarga firebase-credentials.json desde Firebase Console
# - Colócalo en este directorio

# Paso 5: Subir a Firestore
python3 subir_a_firestore.py

# Paso 6: Probar lectura (opcional)
python3 ejemplo_leer_firestore.py
```

## 📊 Estructura en Firestore:

```
lecturas/
├── Amoxcalli, la casa de los libros/
│   ├── texto: "Mucho antes de que llegaran..."
│   ├── autor: "Desconocido"
│   └── preguntas_vof: [
│       {
│         afirmacion: "Los amoxcalli eran casas de los libros.",
│         respuesta: true,
│         dificultad: "fácil"
│       },
│       ...
│     ]
├── Las Arañas/
│   └── ...
├── Leonardo Da Vinci: El gran imaginador/
│   └── ...
└── Alejandra en el cementerio/
    └── ...
```

## ✅ Verificaciones realizadas:

- ✅ 4 lecturas encontradas
- ✅ Todos los archivos tienen preguntas asociadas
- ✅ Búsqueda case-insensitive implementada
- ✅ 32 preguntas en total (16 fácil, 8 intermedia, 8 difícil)

## 🎯 Características implementadas:

- Extracción automática de título y autor
- Asociación automática de preguntas por lectura
- Conversión de niveles (básico→fácil, intermedio→intermedia, avanzado→difícil)
- Manejo robusto de errores
- Validación de datos antes de subir
- Reportes detallados

## 📱 Uso en aplicaciones:

Para leer datos desde tu app (JavaScript/TypeScript):

```javascript
import { getFirestore, collection, getDocs, doc, getDoc } from 'firebase/firestore';

// Obtener todas las lecturas
const lecturasRef = collection(db, 'lecturas');
const snapshot = await getDocs(lecturasRef);
snapshot.forEach(doc => {
  console.log(doc.id, doc.data());
});

// Obtener una lectura específica
const docRef = doc(db, 'lecturas', 'Amoxcalli, la casa de los libros');
const docSnap = await getDoc(docRef);
if (docSnap.exists()) {
  const data = docSnap.data();
  console.log('Texto:', data.texto);
  console.log('Autor:', data.autor);
  console.log('Preguntas:', data.preguntas_vof);
}
```

## 🔒 Seguridad:

⚠️ **IMPORTANTE**: No subas el archivo `firebase-credentials.json` a Git.
Agrégalo al `.gitignore`:

```bash
echo "firebase-credentials.json" >> .gitignore
```

## 📞 Soporte:

Si tienes problemas, ejecuta:
```bash
python3 verificar_datos_firestore.py
```

Este script te dirá exactamente qué está mal.
