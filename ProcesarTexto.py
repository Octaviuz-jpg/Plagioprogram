import re
import pdfplumber

def ignorar_paginas(pdf):
    texto_completo = ""  
    titulos_guardados = []  # Lista para almacenar los títulos
    palabras_clave_ignorar = [
        "anexo", "república bolivariana de venezuela", "agradecimientos", "indice", "dedicatoria, abstract" 
    ]

    for pagina in pdf.pages:
        texto = pagina.extract_text()
        if texto:
            texto_normalizado = texto.lower()
            lineas = texto_normalizado.splitlines()
            
            if lineas:  # Verificar que haya líneas antes de acceder a ellas
                titulo = lineas[0]  # Extraer el título como primera línea
                titulos_guardados.append(titulo)  # Guardar el título sin afectarlo
                
                # Aplicar filtro basado en las palabras clave en el título
                if any(palabra in titulo.lower() for palabra in palabras_clave_ignorar):
                    continue  # Ignorar la página si el título coincide
            
            # Aplicar filtro basado en palabras clave en el contenido
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
    Extrae contenido entre comillas, ignorando citas con menos de 4 palabras
    """
    patron_comillas = r'["\'](.+?)["\']'
    contenido_comillas = re.findall(patron_comillas, texto_normalizado)
    
    # Filtrar citas con 4 o más palabras
    contenido_filtrado = [
        cita for cita in contenido_comillas 
        if len(cita.split()) >= 4
    ]
    
    return list(dict.fromkeys(contenido_filtrado))  # Eliminar duplicados

def detectar_citas_largas(pdf):
    """
    Detecta citas largas, ignorando las que tienen menos de 4 palabras
    """
    citas_largas = []
    margen_cita = 50  # ≈1.27 cm
    margen_parrafo_secundario = 100  # ≈2.54 cm

    for pagina in pdf.pages:
        palabras = pagina.extract_words(keep_blank_chars=False, extra_attrs=["x0"])
        if not palabras:
            continue

        cita_actual = []
        en_cita = False

        for palabra in palabras:
            x0 = palabra["x0"]

            if not en_cita and margen_cita - 5 <= x0 <= margen_cita + 5:
                en_cita = True
                cita_actual.append(palabra["text"])

            elif en_cita:
                if margen_cita - 5 <= x0 <= margen_cita + 5:
                    cita_actual.append(palabra["text"])
                elif margen_parrafo_secundario - 5 <= x0 <= margen_parrafo_secundario + 5:
                    cita_actual.append("\n    " + palabra["text"])
                else:
                    if cita_actual:
                        texto_cita = " ".join(cita_actual)
                        # Solo añadir si tiene 4+ palabras
                        if len(texto_cita.split()) >= 4:
                            citas_largas.append(texto_cita)
                    cita_actual = []
                    en_cita = False

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
        
        citas_comillas = extraer_texto_en_comillas(texto_normalizado)
        citas_sangradas = detectar_citas_largas(pdf)

        bloques_punto_aparte = re.split(r"\.\s*\n", texto_completo)
        for bloque_aparte in bloques_punto_aparte:
            bloques_punto_seguido = re.split(r"(?<=\.)\s+(?=\w)", bloque_aparte)
            for separacion in bloques_punto_seguido:
                separacion = separacion.strip()
                lineas = separacion.split("\n")
                if len(lineas) >= 3 and len(separacion) >= 15:
                    separaciones.append(separacion)

    return separaciones, citas_comillas, citas_sangradas

if __name__ == "__main__":
    ruta_pdf = "C:\\Users\\Octavio\\Desktop\\plagioprogram\\prueba1.pdf"
    parrafos, citas_comillas, citas_sangradas = procesar_pdf_en_lista(ruta_pdf)

    print(f"\n📜 Párrafos extraídos: {len(parrafos)}")

    if parrafos:  # Verificar que haya al menos un párrafo
        print(f"\n📜 Primer párrafo extraído:\n{parrafos[0]}")
    else:
     print("\n⚠️ No se encontraron párrafos extraídos.")

  #  print(f"🔎 Citas entre comillas (4+ palabras): {len(citas_comillas)}")
   # print(f"📝 Citas largas (4+ palabras): {len(citas_sangradas)}")

  #  print("\n=== Citas largas detectadas ===")
   # for i, cita in enumerate(citas_sangradas, start=1):
    #    print(f"\nCita {i}:\n{cita}")

    #print("\n=== Citas entre comillas ===")
    #for i, cita in enumerate(citas_comillas, start=1):
     #   print(f"\nCita {i}: {cita}")