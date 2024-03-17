from PyPDF2 import PdfReader
from ics import Calendar, Event
from datetime import date, time, datetime
from zoneinfo import ZoneInfo
import tzdata

HORAS = {
	'1' : time(8, 15, tzinfo=ZoneInfo("America/Santiago")),
	'2' : time(9, 50, tzinfo=ZoneInfo("America/Santiago")),
	'3' : time(11, 25, tzinfo=ZoneInfo("America/Santiago")),
	'4' : time(13, 45, tzinfo=ZoneInfo("America/Santiago")),
	'5' : time(15, 20, tzinfo=ZoneInfo("America/Santiago")),
	'6' : time(16, 55, tzinfo=ZoneInfo("America/Santiago")),
	'7' : time(18, 45, tzinfo=ZoneInfo("America/Santiago")),
	'8' : time(20, 5, tzinfo=ZoneInfo("America/Santiago")),
	'9' : time(21, 25, tzinfo=ZoneInfo("America/Santiago"))
	}

def leer_pdf(nombre):
	reader = PdfReader(nombre)
	number_of_pages = len(reader.pages)
	page = reader.pages[0]
	text = page.extract_text()
	text = text.split('\n')
	return text

def proces_pdf(text):
	# En la linea 11 empiezan a salir los ramos
	rut = text[0]
	# Terminan de salir ramos cuando la linea que sigue es tres veces el rut
	i = 11
	asignaturas = []
	linea = text[i]
	while linea != rut*3:
		linea = linea[1:] # Eliminamos el indice de la lista
		linea = linea.split(' ')
		tipo = linea.pop()[:-1]
		horas = linea.pop()
		seccion = linea.pop()
		codigo = linea.pop(0)
		nombre = " ".join(linea)
		asignaturas.append({
			'codigo' : codigo,
			'tipo' : tipo,
			'horas' : format_horas(horas),
			'seccion' : seccion,
			'nombre' : nombre
			})
		i+=1
		linea = text[i]
	return asignaturas

def format_horas(horas):
	output = []
	for i in range(len(horas)):
		if i%2 == 0:
			output.append(horas[i]+horas[i+1])
	return output

#pendiente
def crear_evento(semana, ramo):
	for dia in semana:
		for hora in ramo['horas']:
			e = Event()
			e.name = ramo['nombre']
			e.begin = date(dia).HORAS[hora[1]]

pdf = leer_pdf('horario.pdf')

horario = proces_pdf(pdf)

for elemento in horario:
	print(elemento)


