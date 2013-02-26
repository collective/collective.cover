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

nodejs-install:
	sudo apt-add-repository ppa:chris-lea/node.js -y
	sudo apt-get update 1>/dev/null
	sudo apt-get install nodejs npm -y

csslint-install: nodejs-install
	npm install csslint -g

jshint-install: nodejs-install
	npm install jshint -g

python-validation:
	@echo Validating Python files
	bin/flake8 --ignore=$(pep8_ignores) --max-complexity=$(max_complexity) $(src)

css-validation: ack-install csslint-install
	@echo Validating CSS files
	find $(src) -type f -name *.css $(css_ignores) | xargs csslint | ack-grep --passthru error

js-validation: ack-install jshint-install
	@echo Validating JavaScript files
	find $(src) -type f -name *.js $(js_ignores) -exec jshint {} ';' | ack-grep --passthru error

quality-assurance: python-validation css-validation js-validation
	@echo Quality assurance
	./coverage.sh $(minimum_coverage)

install:
	mkdir -p buildout-cache/downloads
	python bootstrap.py -c travis.cfg
	bin/buildout -c travis.cfg $(options)

tests:
	bin/test
