.PHONY: render gen_models

default: build

build:
	python build.py test/definitions/companies_api.yaml

clean:
	rm -r _build
