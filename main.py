from PyPDF2 import PdfReader  # librería para leer pdfs
from ics import Calendar, Event  # librería para manejo de archivos .ics
from ics.grammar.parse import ContentLine
from datetime import date, time, datetime, timedelta  # librería para manejo de tiempo
from zoneinfo import ZoneInfo  # librería para manejo de zonas horarias
from dateutil.rrule import *
import tzdata  # librería con las zonas horarias
import sys

# Inicio y fin del semestre actual (2024-1)
INICIO_SEM = date(2024, 3, 18)
FIN_SEM = date(2024, 7, 20)

# Si llegan a cambiar la duración de los bloques como en el semestre 2022-2
# Basta con cambiar la duración aquí
DURACION_BLOQ = {"horas": 1, "minutos": 20}

# Lo mismo corre para los inicios de los bloques
HORAS = {
    "1": time(8, 15, tzinfo=ZoneInfo("America/Santiago")),
    "2": time(9, 50, tzinfo=ZoneInfo("America/Santiago")),
    "3": time(11, 25, tzinfo=ZoneInfo("America/Santiago")),
    "4": time(13, 45, tzinfo=ZoneInfo("America/Santiago")),
    "5": time(15, 20, tzinfo=ZoneInfo("America/Santiago")),
    "6": time(16, 55, tzinfo=ZoneInfo("America/Santiago")),
    "7": time(18, 45, tzinfo=ZoneInfo("America/Santiago")),
    "8": time(20, 5, tzinfo=ZoneInfo("America/Santiago")),
    "9": time(21, 25, tzinfo=ZoneInfo("America/Santiago")),
}

DIAS = {"L": MO, "M": TU, "W": WE, "J": TH, "V": FR, "S": SA}


def leer_pdf(nombre):
    try:
        # Lee el pdf y lo transforma a texto
        reader = PdfReader(nombre)
        number_of_pages = len(reader.pages)
        page = reader.pages[0]
        text = page.extract_text()
        text = text.split("\n")
        return text
    except:
        print("Error al abrir el archivo pdf")
        return 1


def proces_pdf(text):
    try:
        # Recolecta la información necesaria para el funcionamiento del programa
        # En la linea 11 empiezan a salir los ramos
        rut = text[0]
        # Terminan de salir ramos cuando la linea que sigue es tres veces el rut
        i = 11
        asignaturas = []
        linea = text[i]
        while linea != rut * 3:
            linea = linea[1:]  # Eliminamos el indice de la lista
            linea = linea.split(" ")
            tipo = linea.pop()[:-1]
            horas = linea.pop()
            seccion = linea.pop()
            codigo = linea.pop(0)
            nombre = " ".join(linea).title()
            asignaturas.append(
                {
                    "codigo": codigo,
                    "tipo": tipo,
                    "horas": format_horas(horas),
                    "seccion": seccion,
                    "nombre": nombre,
                }
            )
            i += 1
            linea = text[i]
        return asignaturas
    except:
        print("Pdf ingresado inválido")
        return 1


def format_horas(horas):
    # Transforma un string del tipo 'M2V1V2'
    # en una lista del tipo ['M2', 'V1', 'V2']
    output = []
    for i in range(len(horas)):
        if i % 2 == 0:
            output.append(horas[i] + horas[i + 1])
    return output


def format_bloq_hor(bloque):
    # Recibe un bloque horario tipo 'L2'
    # devuelve una lista con el horario formateado ['MO', time(9, 50, tzinfo=ZoneInfo("America/Santiago"))]
    return {"dia": DIAS[bloque[0]], "hora": HORAS[bloque[1]]}


def calc_dia_inicio_sem(dia):
    if dia == MO:
        return INICIO_SEM
    elif dia == TU:
        return INICIO_SEM + timedelta(days=1)
    elif dia == WE:
        return INICIO_SEM + timedelta(days=2)
    elif dia == TH:
        return INICIO_SEM + timedelta(days=3)
    elif dia == FR:
        return INICIO_SEM + timedelta(days=4)
    elif dia == SA:
        return INICIO_SEM + timedelta(days=5)


def crear_evento(ramo, calendario):
    for bloque in ramo["horas"]:
        horario = format_bloq_hor(bloque)
        evento = Event()
        evento.name = ramo["seccion"] + " " + ramo["nombre"] + " " + ramo["tipo"]
        evento.description = "Código " + ramo["codigo"]
        evento.begin = datetime.combine(
            calc_dia_inicio_sem(horario["dia"]), horario["hora"]
        )
        evento.end = evento.begin + timedelta(
            hours=DURACION_BLOQ["horas"], minutes=DURACION_BLOQ["minutos"]
        )
        evento.extra.append(
            ContentLine(
                name="RRULE",
                value=f"FREQ=WEEKLY;INTERVAL=1;WKST=MO;BYDAY={horario['dia']};UNTIL={FIN_SEM.strftime('%Y%m%dT%H%M%S')}",
            )
        )
        calendario.events.add(evento)
    return calendario


def crear_calendario(horario):
	# Crea el calendario
    calendario = Calendar()
    for ramo in horario:
        calendario = crear_evento(ramo, calendario)
    return calendario

def crear_archivo(calendario):
    try:
        with open("horario.ics", "w") as f:
                f.writelines(calendario.serialize_iter())
        print("Horario exportado exitosamente como horario.ics")
    except:
        print("Error al crear el archivo")
        return 1

def main():
    if len(sys.argv) == 2:
        pdf = leer_pdf(sys.argv[1])
        if pdf == 1:
            return
        horario = proces_pdf(pdf)
        if horario == 1:
            return
        calendario = crear_calendario(horario)
        crear_archivo(calendario)
    else:
        print("Opción inválida")

if __name__ == "__main__":
	main()