from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def buscar_en_bing(parrafos):
    # Iniciar el navegador con el controlador adecuado
    driver = webdriver.Chrome()

    driver.get("https://www.bing.com")
    resultados_pagina = {}

    for parrafo in parrafos:
        try:
            # Esperar a que el campo de búsqueda esté disponible
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()  # Limpiar búsqueda anterior
            search_box.send_keys(parrafo)
            search_box.send_keys(Keys.RETURN)  # Presionar "Enter"

            # Esperar a que los resultados de búsqueda aparezcan
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h2 a"))
            )

            # Extraer los enlaces de los primeros resultados
            resultados = driver.find_elements(By.CSS_SELECTOR, "h2 a")  # Enlaces reales en <h2><a>
            enlaces = [r.get_attribute("href") for r in resultados if r.get_attribute("href")]

            # Filtrar enlaces no deseados y limitar a los primeros 5
            enlaces_filtrados = [link for link in enlaces if link and "bing" not in link][:5]
            
            resultados_pagina[parrafo] = enlaces_filtrados  

        except Exception as e:
            print(f"Error al buscar '{parrafo}': {e}")
            resultados_pagina[parrafo] = []  # Si ocurre un error, retornar lista vacía

    driver.quit()
    return resultados_pagina