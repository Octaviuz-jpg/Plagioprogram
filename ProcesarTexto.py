import re
import pdfplumber

def ignorar_paginas(pdf):
    """
    Filtra las páginas del PDF que contienen ciertas palabras clave o que están
    en posiciones específicas (como portadas, índices, bibliografía, etc.).

    Args:
        pdf (pdfplumber.PDF): Objeto PDF abierto con pdfplumber.

    Returns:
        list: Lista de páginas válidas para procesar.
    """
    paginas_validas = []
    palabras_clave_ignorar = [
        
        "anexo", "república bolivariana de venezuela", 
    ]

    for i, pagina in enumerate(pdf.pages):
        texto = pagina.extract_text()
        if texto:
            texto_normalizado = texto.lower()
            lineas = texto_normalizado.splitlines()
            # Verifica si las palabras clave están presentes en cualquier parte de las primeras 3 líneas
            if any(palabra in linea for palabra in palabras_clave_ignorar for linea in lineas[:3]):
                continue
            # Ignora si las palabras clave aparecen varias veces en toda la página
            if sum(texto_normalizado.count(palabra) for palabra in palabras_clave_ignorar) > 3:
                continue
            paginas_validas.append(pagina)

    return paginas_validas


def procesar_pdf_en_lista(ruta_pdf):
    """
    Lee un archivo PDF, extrae texto, divide el contenido por punto y aparte
    y punto y seguido, ignora bloques irrelevantes con "_________", y guarda cada
    separación individual en la lista.

    Args:
        ruta_pdf (str): Ruta al archivo PDF.

    Returns:
        list: Lista de separaciones procesadas.
    """
    separaciones = []

    # Abrir y leer el PDF
    with pdfplumber.open(ruta_pdf) as pdf:
        # Filtrar páginas según contenido o número
        paginas_filtradas = ignorar_paginas(pdf)
        
        for pagina in paginas_filtradas:
            texto = pagina.extract_text()

            if texto:
                # Eliminar citas comunes
                texto = re.sub(r"\[\d+\]", "", texto)  # Citas como [1], [12]
                texto = re.sub(r"\(\w+,\s?\d{4}\)", "", texto)  # Citas como (Smith, 2020)
                texto = re.sub(r"\s\d+\s*", "", texto)  # Citas como " 12 "

                # Separar el texto por puntos y aparte primero
                bloques_punto_aparte = re.split(r"\.\s*\n", texto)

                # Dentro de cada bloque separado por puntos y aparte, dividir por puntos y seguidos
                for bloque_aparte in bloques_punto_aparte:
                    bloques_punto_seguido = re.split(r"(?<=\.)\s+(?=\w)", bloque_aparte)  # Divide por punto y seguido

                    for separacion in bloques_punto_seguido:
                        separacion = separacion.strip()  # Eliminar espacios al inicio y al final

                        # Ignorar separaciones con menos de 15 caracteres
                        if len(separacion) < 15:
                            continue

                        # Ignorar separaciones que contengan "_________"
                        if "_________" in separacion:
                            continue

                        # Añadir cada separación a la lista si no está vacía
                        if separacion:
                            separaciones.append(separacion)

    return separaciones



# Ejemplo de uso
if __name__ == "__main__":
    ruta_pdf = "ejemplo_tesis.pdf"  # Ruta al archivo PDF
    parrafos = procesar_pdf_en_lista(ruta_pdf)
    print("Párrafos extraídos y procesados:")
    for i, parrafo in enumerate(parrafos, start=1):
        print(f"Párrafo {i}: {parrafo}")
