PYTHON ?= python3

.PHONY: all graphics comp_time files_ed

all: graphics comp_time files_ed

graphics:
	cd 'FFT&DFT' && $(PYTHON) graphics.py

comp_time:
	cd 'FFT&DFT' && $(PYTHON) comp_time.py

files_ed:
	cd 'Files_ED' && $(PYTHON) main.py