<h1 align=center>
Loa To Calendar
</h1>
<p align=center>
<span>Herramienta para exportar el horario del loa a un archivo .ics</span>
<br>
</p>
<span>
Iba a agregar mi horario a <a href="https://calendar.google.com/">Google Calendar</a> pero me dio paja hacerlo a mano, así que gasté el triple del tiempo que me hubiera demorado haciéndolo para automatizarlo.
</span>


## Instalación
```console
# clonar el repositorio
$ git clone https://github.com/fabianlizama/loa-to-calendar

# cambiar el directorio a loa-to-calendar
$ cd loa-to-calendar

# instalar requerimientos
$ pip install -r requirements.txt
```
## Uso
Primero es necesario descargar el horario del loa y ponerlo en el mismo directorio del programa, luego ejecutar el siguiente comando:
```console
# con las fechas del semestre actual (por defecto)
$ python main.py ruta_al_horario.pdf

# con fechas de semestre personalizadas (DD-MM-AAAA)
$ python main.py ruta_al_horario.pdf --inicio 10-08-2026 --fin 04-12-2026
```
La fecha de `--inicio` debe ser el **lunes** de la primera semana de clases.
