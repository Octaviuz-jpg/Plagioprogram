import ProcesarTexto
import Buscar_google
from pprint import pprint

# 🔹 Desempaquetar las dos listas que devuelve la función
listaView, citas_extraidas = ProcesarTexto.procesar_pdf_en_lista("C:\\Users\\Octavio\\Desktop\\plagioprogram\\test2.pdf")

print(f"\nNúmero de párrafos extraídos: {len(listaView)}")
print(f"Número de citas extraídas: {len(citas_extraidas)}")

# 🔹 Buscar enlaces relacionados con los párrafos extraídos
#listalinks = Buscar_google.buscar_en_bing(listaView)

# 🔎 Imprimir párrafos procesados
#print("\n📜 Párrafos procesados:")
#pprint(listaView)

# Imprimir citas extraídas
print("\n🔎 Citas encontradas:")
for i, (cita, referencia) in enumerate(citas_extraidas, start=1):
   print(f"Cita {i}: {cita}")
   print(f"Referencia: {referencia}")
