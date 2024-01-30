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
	poetry run ptw -- -- -rP -x -m focus

## watch:                 run tests in watch mode
.PHONY: watch
watch:
	poetry run ptw -- -- -rP -x

## test:                  run tests
.PHONY: test
test:
	poetry run pytest

## chainlit:              run the app
.PHONY: chainlit
chainlit:
	poetry run chainlit run app.py -w

## fly-chainlit:          run the app in fly.io mode
.PHONY: fly-chainlit
fly-chainlit:
	poetry run chainlit run fly_app.py -w

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

## doctest:               run doctests
.PHONY: doctest
doctest:
	python -m doctest weather_chat_ai/nws_chain.py

## deploy:                deploy to fly.io
deploy:
	@poetry export -f requirements.txt --output requirements.txt

	@if [ -z "$$(git status --porcelain)" ]; then \
		flyctl deploy && git tag -f fly.io; \
	else \
	    git status --porcelain; \
	fi

## logs:                  watch the fly.io logs
logs:
	@flyctl logs

## ssh:                   ssh into the fly.io instance
ssh:
	@flyctl ssh console

## scale:                 show the fly.io instance scale info
scale:
	@echo https://fly.io/docs/apps/legacy-scaling/#viewing-the-current-vm-size
	@flyctl scale show