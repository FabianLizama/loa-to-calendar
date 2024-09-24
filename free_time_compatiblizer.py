from main import *
import os

def extraer_bloques(horario):
    lista = []
    for ramo in horario:
        lista.append(ramo['horas'])
    return lista

def main():
    horarios_ocupados = []

    # Se crea el directorio horarios si no existe
    directorio = os.getcwd() + '/horarios'
    if not os.path.exists(directorio):
        os.mkdir(directorio)

    # Se recorre el directorio
    with os.scandir(directorio) as horarios:
        for archivo in horarios:
            print(archivo.name)

            # Se lee el pdf
            pdf = leer_pdf(archivo.name)
            if pdf == 1:
                return
            
            # Se procesa el pdf para extraer los datos relevantes
            horario = proces_pdf(pdf)
            if horario == 1:
                return
            
            # Se extraen los horarios relevantes
            horarios_ramos = extraer_bloques(horario)

            for lista_bloques in horarios_ramos:
                for bloque in lista_bloques:
                    if bloque not in horarios_ocupados:
                        horarios_ocupados.append(bloque)
            
        print(horarios_ocupados)
if __name__ == "__main__":
	main()