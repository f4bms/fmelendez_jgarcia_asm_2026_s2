# Ejecutar make desde Files_ED. Puede elegirse otro intérprete con:
# make PYTHON=python3
PYTHON = python

# Punto de entrada del experimento de detección de ecos.
MAIN = main.py

# Carpeta relativa a Files_ED donde se guardan las gráficas del experimento.
GRAPHICS = graphics


# Estas reglas son acciones, aunque exista un archivo con el mismo nombre.
.PHONY: all run clean


# Ejecutar make sin argumentos inicia el experimento mediante la regla run.
all: run


# Genera las señales, estima los retardos y guarda las gráficas.
run:
	@echo "Ejecutando experimento de deteccion de ecos..."
	$(PYTHON) $(MAIN)
	@echo "Experimento terminado."


# Borra los PNG generados; no elimina la carpeta ni los archivos de código.
# La orden rm requiere una shell compatible, como la disponible en Git Bash.
clean:
	@echo "Eliminando graficas generadas..."
	rm -rf $(GRAPHICS)/*.png
	@echo "Limpieza completada."