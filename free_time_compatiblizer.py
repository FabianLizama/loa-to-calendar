from main import *
import os

PRIORIDAD_LETRAS = {'L': 1, 'M': 2, 'W': 3, 'J': 4, 'V': 5, 'S': 6}

def extraer_nombre(datos):
    # Unir todos los elementos de la lista en un solo string
    texto = ' '.join(datos)
    
    # Dividir el texto en la frase "Horario de clases informativo del estudiante" y "para el"
    try:
        # Buscar el texto entre esas dos frases
        nombre = texto.split("Horario de clases informativo  del  estudiante")[1].split("para el")[0].strip()
        return nombre
    except IndexError:
        return "No se pudo encontrar el nombre en el formato esperado."

def extraer_bloques(horario):
    lista = []
    for ramo in horario:
        print("Ramo:", ramo)
        lista.append(ramo['horas'])
    return lista

# Función para extraer la clave de ordenación para ordenar los bloques
def clave_orden(elemento):
    letra = elemento[0]
    numero = int(elemento[1:])
    return (PRIORIDAD_LETRAS[letra], numero)

def ordenar_lista(lista):
    return sorted(lista, key=clave_orden)


def main():
    consolidado_horarios = []
    '''
    consolidado_horarios será una lista de la siguiente forma:
    [
        {
            nombre: "John Doe",
            bloques: [L1, M2, W3]
        },
        {
            nombre: "Juan Perez",
            bloques: [L2, M2, W3]
        }
    ]
    '''

    # Se crea el directorio horarios si no existe
    directorio = os.getcwd() + '/horarios'
    if not os.path.exists(directorio):
        os.mkdir(directorio)

    # Se recorre el directorio
    with os.scandir(directorio) as horarios:
        for archivo in horarios:

            # Se lee el pdf
            pdf = leer_pdf(directorio + '/' + archivo.name)
            if pdf == 1:
                return

            # Se procesa el pdf para extraer los datos relevantes
            horario = proces_pdf(pdf, archivo.name)
            if horario == 1:
                return
            
            # Se extraen los horarios relevantes
            horarios_ramos = extraer_bloques(horario)
            
            # Se eliminan duplicados y se guardan solo los horarios
            # sin información de los ramos
            horarios_ocupados = []
            for lista_bloques in horarios_ramos:
                for bloque in lista_bloques:
                    if bloque not in horarios_ocupados:
                        horarios_ocupados.append(bloque)
            
            # Se agrega al consolidado
            consolidado_horarios.append({
                "nombre": extraer_nombre(pdf),
                "horarios": ordenar_lista(horarios_ocupados)
            })

        # Se ordena la lista
        print(consolidado_horarios)
if __name__ == "__main__":
	main()