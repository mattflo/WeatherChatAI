## help:                  displays this help
.PHONY: help
help: Makefile
	@sed -n 's/^## \?//p' $<

## isort:                 run isort
.PHONY: isort
isort:
	@poetry run isort --profile black .
	@poetry run autoflake --remove-all-unused-imports --recursive --remove-unused --in-place .

## watch-focus:           run tests in watch mode with focus
.PHONY watch-focus:
watch-focus:
	poetry run ptw -- -- -rP -m focus

## watch:                 run tests in watch mode
.PHONY: watch
watch:
	poetry run ptw -- -- -rP

## test:                  run tests
.PHONY: test
test:
	poetry run pytest

## streamlit:              run the app
.PHONY: streamlit
streamlit:
	poetry run streamlit run streamlit_app.py

## lint:                  run linters
.PHONY: lint
lint:
	poetry run mypy .
	poetry run black . --check
	poetry run ruff .

## format:                run formatters
.PHONY: format
format:
	poetry run black .
	poetry run ruff --select I --fix .
