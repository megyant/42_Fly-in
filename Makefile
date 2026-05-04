VENV    = venv
PYTHON  = $(VENV)/bin/python3
PIP     = $(VENV)/bin/pip
SRC 	= src
MODULE	= src.fly-in

.PHONY: install run debug clean fclean lint flake8 mypy lint-strict mypy-strict

all: install run

all_clean: install run clean

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy pydantic

run:
	$(PYTHON) -m $(MODULE)

debug:
	$(PYTHON) -m pdb $(MODULE)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

fclean: clean
	rm -rf $(VENV)

lint: flake8 mypy

flake8:
	-$(PYTHON) -m flake8 .

mypy:
	-$(PYTHON) -m mypy $(SRC) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: flake8 mypy-strict

mypy-strict:
	-$(PYTHON) -m mypy $(SRC) --strict
