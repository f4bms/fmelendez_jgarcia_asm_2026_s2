PYTHON = python

MAIN = main.py

GRAPHICS = graphics


.PHONY: all run clean


all: run


run:
	@echo "Ejecutando experimento de deteccion de ecos..."
	$(PYTHON) $(MAIN)
	@echo "Experimento terminado."


clean:
	@echo "Eliminando graficas generadas..."
	rm -rf $(GRAPHICS)/*.png
	@echo "Limpieza completada."