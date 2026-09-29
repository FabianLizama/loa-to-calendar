from pypdf import PdfReader  # librería para leer pdfs
from ics import Calendar, Event  # librería para manejo de archivos .ics
from ics.grammar.parse import ContentLine
from datetime import date, time, datetime, timedelta  # librería para manejo de tiempo
from zoneinfo import ZoneInfo  # librería para manejo de zonas horarias
from dateutil.rrule import *
import tzdata  # librería con las zonas horarias
import argparse
import re

# Inicio y fin del semestre actual (2026-2)
# Se pueden sobrescribir con --inicio y --fin (formato DD-MM-AAAA)
INICIO_SEM = date(2026, 9, 21)  # lunes
FIN_SEM = date(2027, 1, 16)

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


# Línea de un ramo en el pdf: índice, código, nombre, sección,
# horario (ej: M2J2V2), tipo y un número final que se ignora
RAMO_RE = re.compile(
    r"^(\d+)\s+(\d{5}-[A-Z0-9])\s+(.+?)\s+([A-Z]-\d+)\s+((?:[LMWJVS]\d)+)([A-Z]+)(?:\s+(\d+))?$"
)


def proces_pdf(text):
    try:
        # Recolecta la información necesaria para el funcionamiento del programa
        # Cada ramo es una línea que calza con el patrón, el resto se ignora
        asignaturas = []
        for linea in text:
            ramo = RAMO_RE.match(linea.strip())
            if ramo is None:
                continue
            asignaturas.append(
                {
                    "codigo": ramo.group(2),
                    "tipo": ramo.group(6),
                    "horas": format_horas(ramo.group(5)),
                    "seccion": ramo.group(4),
                    "nombre": ramo.group(3).title(),
                }
            )
        if not asignaturas:
            print("Pdf ingresado inválido")
            return 1
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

def parse_fecha(s):
    # Acepta fechas en formato DD-MM-AAAA o AAAA-MM-DD
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"fecha inválida: {s} (usa DD-MM-AAAA)")


def main():
    global INICIO_SEM, FIN_SEM
    parser = argparse.ArgumentParser(
        description="Exporta el horario de la LOA a un archivo .ics"
    )
    parser.add_argument("pdf", help="ruta al horario PDF descargado de la LOA")
    parser.add_argument(
        "--inicio",
        type=parse_fecha,
        default=INICIO_SEM,
        help=f"lunes de la primera semana de clases (DD-MM-AAAA, por defecto {INICIO_SEM.strftime('%d-%m-%Y')})",
    )
    parser.add_argument(
        "--fin",
        type=parse_fecha,
        default=FIN_SEM,
        help=f"último día de clases (DD-MM-AAAA, por defecto {FIN_SEM.strftime('%d-%m-%Y')})",
    )
    args = parser.parse_args()
    INICIO_SEM = args.inicio
    FIN_SEM = args.fin
    if INICIO_SEM.weekday() != 0:
        print("La fecha de inicio debe ser un lunes")
        return
    pdf = leer_pdf(args.pdf)
    if pdf == 1:
        return
    horario = proces_pdf(pdf)
    if horario == 1:
        return
    calendario = crear_calendario(horario)
    crear_archivo(calendario)

if __name__ == "__main__":
	main()
