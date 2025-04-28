import re
import pdfplumber

def ignorar_paginas(pdf):
    texto_completo = ""  
    palabras_clave_ignorar = [
        "anexo", "república bolivariana de venezuela", "agradecimientos", "indice", "dedicatoria"
    ]

    for pagina in pdf.pages:
        texto = pagina.extract_text()
        if texto:
            texto_normalizado = texto.lower()
            lineas = texto_normalizado.splitlines()

            if any(palabra in linea for palabra in palabras_clave_ignorar for linea in lineas[:3]):
                continue
            
            if sum(texto_normalizado.count(palabra) for palabra in palabras_clave_ignorar) > 3:
                continue
            
            texto_completo += texto + "\n"  

    return texto_completo  

def normalizar_texto(texto):
    texto = texto.replace("“", "\"").replace("”", "\"")
    texto = texto.replace("‘", "'").replace("’", "'")
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def extraer_texto_en_comillas(texto_normalizado):
    """
    Extrae contenido entre comillas con filtros mejorados para:
    - Ignorar contracciones inglesas
    - Ignorar palabras sueltas muy cortas
    - Requerir mínimo 4 palabras
    """
    patron_comillas = r'''
        (?!\w)       # Negative lookahead para evitar palabras pegadas
        (["'])       # Comilla de apertura
        ((?:(?!\1|['´’]s\b|n't\b|\b\w{1,3}\b).)+?)  # Contenido (evita contracciones)
        \1           # Comilla de cierre
        (?!\w)       # Negative lookahead para evitar palabras pegadas
    '''
    
    contenido_comillas = re.findall(patron_comillas, texto_normalizado, re.VERBOSE | re.IGNORECASE)
    
    # Filtros adicionales
    contracciones_ingles = [
        "'s", "'ll", "'re", "'d", "'ve", "'m", "n't", 
        "don't", "can't", "won't", "isn't", "aren't"
    ]
    
    contenido_filtrado = [
        cita[1] for cita in contenido_comillas 
        if (len(cita[1].split()) >= 4 and  # 4+ palabras
           not any(cont in cita[1].lower() for cont in contracciones_ingles) and
           not re.search(r"\b[a-z]{1,3}\b", cita[1].lower()))  # Evita palabras muy cortas
    ]
    
    return list(dict.fromkeys(contenido_filtrado))  # Eliminar duplicados

def detectar_citas_largas(pdf):
    """
    Detecta citas largas basadas en sangrías (1.27 cm y 2.54 cm para párrafos subsiguientes).
    """
    citas_largas = []
    margen_cita = 50  # ≈1.27 cm (ajusta según tu PDF: 72 pt = 1 pulgada)
    margen_parrafo_secundario = 100  # ≈2.54 cm

    for pagina in pdf.pages:
        palabras = pagina.extract_words(keep_blank_chars=False, extra_attrs=["x0"])
        if not palabras:
            continue

        cita_actual = []
        en_cita = False

        for palabra in palabras:
            x0 = palabra["x0"]

            # Inicio de cita: palabra con sangría ≈1.27 cm
            if not en_cita and margen_cita - 5 <= x0 <= margen_cita + 5:
                en_cita = True
                cita_actual.append(palabra["text"])

            # Continuación de cita
            elif en_cita:
                if margen_cita - 5 <= x0 <= margen_cita + 5:
                    cita_actual.append(palabra["text"])
                # Párrafo secundario: sangría ≈2.54 cm
                elif margen_parrafo_secundario - 5 <= x0 <= margen_parrafo_secundario + 5:
                    cita_actual.append("\n    " + palabra["text"])  # Indentación visual
                else:
                    # Fin de la cita (solo añadir si tiene 4+ palabras)
                    if cita_actual:
                        texto_cita = " ".join(cita_actual)
                        if len(texto_cita.split()) >= 4:
                            citas_largas.append(texto_cita)
                    cita_actual = []
                    en_cita = False

        # Añadir la última cita de la página (si cumple requisitos)
        if cita_actual:
            texto_cita = " ".join(cita_actual)
            if len(texto_cita.split()) >= 4:
                citas_largas.append(texto_cita)

    return citas_largas

def procesar_pdf_en_lista(ruta_pdf):
    separaciones = []
    citas_comillas = []
    citas_sangradas = []

    with pdfplumber.open(ruta_pdf) as pdf:
        texto_completo = ignorar_paginas(pdf)
        texto_normalizado = normalizar_texto(texto_completo)
        
        # Citas entre comillas (mejorado)
        citas_comillas = extraer_texto_en_comillas(texto_normalizado)
        
        # Citas largas con sangría
        citas_sangradas = detectar_citas_largas(pdf)

        # Procesar párrafos generales
        bloques_punto_aparte = re.split(r"\.\s*\n", texto_completo)
        for bloque_aparte in bloques_punto_aparte:
            bloques_punto_seguido = re.split(r"(?<=\.)\s+(?=\w)", bloque_aparte)
            for separacion in bloques_punto_seguido:
                separacion = separacion.strip()
                lineas = separacion.split("\n")
                if len(lineas) >= 3 and len(separacion) >= 15:
                    separaciones.append(separacion)

    return separaciones, citas_comillas, citas_sangradas

# Ejemplo de uso
if __name__ == "__main__":
    ruta_pdf = "C:\\Users\\Octavio\\Desktop\\plagioprogram\\prueba1.pdf"
    parrafos, citas_comillas, citas_sangradas = procesar_pdf_en_lista(ruta_pdf)

    print(f"\n📜 Párrafos extraídos: {len(parrafos)}")
    print(f"🔎 Citas entre comillas válidas (4+ palabras, sin contracciones): {len(citas_comillas)}")
    print(f"📝 Citas largas válidas (4+ palabras): {len(citas_sangradas)}")

    print("\n=== Citas largas detectadas ===")
    for i, cita in enumerate(citas_sangradas, start=1):
        print(f"\nCita {i}:\n{cita}")

    print("\n=== Citas entre comillas detectadas ===")
    for i, cita in enumerate(citas_comillas, start=1):
        print(f"\nCita {i}: {cita}")