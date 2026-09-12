PYTHON ?= python3

.PHONY: all graphics comp_time

all: graphics comp_time

graphics:
	$(PYTHON) graphics.py

comp_time:
	$(PYTHON) comp_time.py