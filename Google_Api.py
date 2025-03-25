import requests

# Función para buscar en Google Custom Search
def buscar_google(query, clave_api, id_motor, num_resultados=5):
    """
    Realiza una búsqueda utilizando Google Custom Search API.
    """
    url_base = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": clave_api, "cx": id_motor, "num": num_resultados}
    respuesta = requests.get(url_base, params=params)
    
    if respuesta.status_code == 200:
        return respuesta.json().get("items", [])
    else:
        print(f"Error en la búsqueda de Google: {respuesta.status_code}")
        return []

# Ejemplo de uso dentro del módulo
if __name__ == "__main__":
    resultados = buscar_google(
        "tesis de inteligencia artificial",
        "TU_CLAVE_API",
        "TU_ID_DEL_MOTOR"
    )
    
    for resultado in resultados:
        print(resultado["title"], ":", resultado["link"])
