
# Definir funcion que quita los dobles espacios y lineas en blanco extras
with open("lecturas_finales/Leonardo Da Vinci.txt", "r", encoding="utf-8") as f:
    contenido = f.read()
    contenido = contenido.replace("  ", " ").strip()
    # Solo eliminar los dobles saltos de linea
    contenido = contenido.replace("\n\n", "\n")
    with open("lecturas_finales/Leonardo Da Vinci.txt", "w", encoding="utf-8") as f2:
        f2.write(contenido)