PREFIX=/usr
DESTDIR=/

PY_SOURCES=dump.py module_name

update-docs:
	rm -f docs/source/schedsi.rst
	sphinx-apidoc -o docs/source schedsi

html: .PHONY
	$(MAKE) -C docs html

mypy: .PHONY
	mypy --strict $(PY_SOURCES)

flake8: .PHONY
	flake8 $(PY_SOURCES)

pylint: .PHONY
	pylint -r n $(PY_SOURCES)

pylint-disabled: .PHONY
	pylint -e fixme,locally-disabled $(PY_SOURCES)

lint:
	@$(MAKE) -ks $(firstword $(MAKEFILE_LIST)) _lint

_lint: mypy flake8 pylint .PHONY

build: .PHONY
	./setup.py build

install: .PHONY
	./setup.py install --prefix '$(PREFIX)' --root '$(DESTDIR)'

.PHONY:
