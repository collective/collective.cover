# convenience Makefile to run tests and QA tools
# options: zc.buildout options
# src: source path
# minimum_coverage: minimun test coverage allowed
# pep8_ignores: ignore listed PEP 8 errors and warnings
# max_complexity: maximum McCabe complexity allowed
# css_ignores: skip file names matching find pattern (use ! -name PATTERN)
# js_ignores: skip file names matching find pattern (use ! -name PATTERN)

SHELL = /bin/sh

options = -N -q -t 3
src = src/collective/cover/
minimum_coverage = 73
pep8_ignores = E501
max_complexity = 12
css_ignores = ! -name bootstrap\* ! -name jquery\*
js_ignores = ! -name bootstrap\* ! -name jquery\*

ack-install:
	sudo apt-get install ack-grep

python-validation:
	@echo Validating Python files
	bin/flake8 --ignore=$(pep8_ignores) --max-complexity=$(max_complexity) $(src)

css-validation: ack-install
	@echo Validating CSS files
	npm install csslint -g
	find $(src) -type f -name *.css $(css_ignores) | xargs csslint | ack-grep --passthru error

js-validation: ack-install
	@echo Validating JavaScript files
	npm install jshint -g
	find $(src) -type f -name *.js $(js_ignores) -exec jshint {} ';' | ack-grep --passthru error

quality-assurance: python-validation css-validation js-validation
	@echo Quality assurance
	bin/coverage.sh $(minimum_coverage)

install:
	mkdir -p buildout-cache/downloads
	python bootstrap.py -c travis.cfg
	bin/buildout -c travis.cfg $(options)

tests:
	bin/test
