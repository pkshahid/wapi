-include .env
export

.PHONY: clean build check publish-test publish test lint

clean:
	rm -rf dist/ build/ src/*.egg-info

build: clean
	uv build

check: build
	uvx twine check dist/*

test:
	uv run pytest

lint:
	uv run ruff check src tests
	uv run mypy src

publish-test: check
	UV_PUBLISH_TOKEN="$${UV_PUBLISH_TOKEN_TEST:-$$UV_PUBLISH_TOKEN}" \
		uv publish --publish-url https://test.pypi.org/legacy/

publish: check
	uv publish
