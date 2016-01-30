all: docs upload

upload:
	python setup.py bdist upload

docs:
	pandoc --from=markdown --to=rst --output=README.rst README.md

.PHONY: docs
