# 📚 Subir Lecturas a Firestore

Script para subir lecturas y preguntas de verdadero/falso a Firebase Firestore.

## � Inicio Rápido

```bash
# 1. Ver un preview de los datos
python3 preview_firestore.py

# 2. Verificar que todo esté correcto
python3 verificar_datos_firestore.py

# 3. Instalar Firebase Admin SDK
pip install firebase-admin

# 4. Descargar credenciales de Firebase (ver instrucciones abajo)

# 5. Subir a Firestore
python3 subir_a_firestore.py
```

## �📋 Requisitos Previos

### 1. Instalar Firebase Admin SDK

```bash
pip install firebase-admin
```

### 2. Obtener Credenciales de Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto (o crea uno nuevo)
3. Ve a **Project Settings** (⚙️ > Configuración del proyecto)
4. Navega a la pestaña **Service Accounts**
5. Click en **Generate new private key** (Generar nueva clave privada)
6. Descarga el archivo JSON
7. Guárdalo como `firebase-credentials.json` en este directorio

### 3. Estructura de Archivos Requerida

Asegúrate de tener:
- ✅ `lecturas_finales/` - Carpeta con archivos .txt de las lecturas
- ✅ `banco_verdadero_falso.json` - Archivo con las preguntas
- ✅ `firebase-credentials.json` - Credenciales de Firebase
- ✅ `subir_a_firestore.py` - Este script

## 🚀 Uso

```bash
python3 subir_a_firestore.py
```

## 📊 Estructura en Firestore

El script creará la siguiente estructura:

```
lecturas (colección)
│
├── Nombre de Lectura 1 (documento)
│   ├── texto: "Contenido completo de la lectura..."
│   ├── autor: "Nombre del autor"
│   └── preguntas_vof: [
│       {
│         afirmacion: "Pregunta en forma de afirmación",
│         respuesta: true/false,
│         dificultad: "fácil" | "intermedia" | "difícil"
│       },
│       ...
│     ]
│
├── Nombre de Lectura 2 (documento)
│   └── ...
```

## 📝 Formato de Archivos de Lectura

Los archivos `.txt` en `lecturas_finales/` deben tener el siguiente formato:

```
Título de la Lectura
Autor: Nombre del Autor

Texto de la lectura...
```

## ⚙️ Configuración

Puedes modificar estas variables en `subir_a_firestore.py`:

```python
LECTURAS_DIR = "lecturas_finales"          # Carpeta con las lecturas
BANCO_PREGUNTAS_JSON = "banco_verdadero_falso.json"  # Archivo JSON con preguntas
COLECCION = "lecturas"                      # Nombre de la colección en Firestore
FIREBASE_CREDENTIALS = "firebase-credentials.json"   # Archivo de credenciales
```

## 🔍 Características

- ✅ Extrae automáticamente título y autor de cada lectura
- ✅ Asocia preguntas con sus lecturas correspondientes
- ✅ Organiza preguntas por nivel de dificultad
- ✅ Manejo de errores y reportes detallados
- ✅ Validación de nombres de archivos
- ✅ Resumen de subida al finalizar

## 🛠️ Solución de Problemas

### Error: "No module named 'firebase_admin'"
```bash
pip install firebase-admin
```

### Error: "No se encontró el archivo de credenciales"
Asegúrate de haber descargado las credenciales de Firebase y guardado el archivo como `firebase-credentials.json`.

### Error: "No se encontraron preguntas"
Verifica que los nombres de los archivos `.txt` coincidan con los nombres en el campo `"origen"` del archivo `banco_verdadero_falso.json`.

## 📧 Soporte

Si encuentras algún problema, verifica:
1. Que todas las dependencias estén instaladas
2. Que el archivo de credenciales sea válido
3. Que los nombres de las lecturas coincidan entre archivos
