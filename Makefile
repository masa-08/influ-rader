TARGET ?= influ_rader

lint:
	poetry run black \
		--exclude ".venv" \
		.
	poetry run isort --atomic .
	poetry run autoflake \
		-r --in-place \
		--exclude ".venv" \
		--remove-all-unused-imports \
		--remove-unused-variables \
		.
	poetry run flake8 .

lint-nofix:
	poetry run black --check \
		--exclude ".venv" \
		.
	poetry run isort --check .
	poetry run autoflake \
		-r --check \
		--exclude ".venv" \
		--remove-all-unused-imports \
		--remove-unused-variables \
		.
	poetry run flake8

type:
	poetry run mypy ${TARGET} --no-incremental --cache-dir=nul

test:
	poetry run pytest ${TARGET}

deploy-dev:
	git push heroku-dev main

env-dev:
	heroku config:push -r heroku-dev --overwrite --file=.env.staging
