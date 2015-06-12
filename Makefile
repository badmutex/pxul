
APIDIR = docs/api

export PYTHONPATH += $(PWD)

.PHONY: help clean docs tests

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  clean    to remove artifacts"
	@echo "  docs     to make the documentation"
	@echo "  test     to run the unit tests"

clean:
	make -C docs clean
	rm -rf $(APIDIR)
	python setup.py clean

docs:
	sphinx-apidoc -o $(APIDIR) pxul
	make -C docs html

test:
	./runtests.sh
