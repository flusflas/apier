.PHONY: render gen_models

default: render gen_models

render:
	python build.py test/definitions/companies_api.yaml

gen_models:
	datamodel-codegen  --input test/definitions/companies_api.yaml --input-file-type openapi --output _build/models/models.py --base-class _build.models.basemodel.IterBaseModel

clean:
	rm -r _build
