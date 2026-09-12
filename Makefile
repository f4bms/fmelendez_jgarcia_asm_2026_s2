PYTHON ?= python3

.PHONY: all graphics comp_time

all: graphics comp_time

graphics:
	cd 'FFT&DFT' && $(PYTHON) graphics.py

comp_time:
	cd 'FFT&DFT' && $(PYTHON) comp_time.py