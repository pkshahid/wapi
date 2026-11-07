-include .env
export

.PHONY: clean build check publish-test publish test lint version set-version bump-major bump-minor bump-patch

VERSION := $(shell grep -m1 '^version' pyproject.toml | cut -d'"' -f2)

version:
	@echo $(VERSION)

set-version:
ifndef V
	$(error usage: make set-version V=1.2.3)
endif
	sed -i 's/^version = ".*"/version = "$(V)"/' pyproject.toml
	@echo "version = $(V)"

bump-major bump-minor bump-patch:
	@NEW=$$(echo "$(VERSION)" | awk -F. -v part=$(@:bump-%=%) '{ \
		if (part == "major") { $$1++; $$2=0; $$3=0 } \
		else if (part == "minor") { $$2++; $$3=0 } \
		else { $$3++ } \
		print $$1"."$$2"."$$3 }'); \
	sed -i "s/^version = \".*\"/version = \"$$NEW\"/" pyproject.toml; \
	echo "version: $(VERSION) -> $$NEW"

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
