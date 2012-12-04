# convenience makefile to boostrap & run buildout
# use `make options=-v` to run buildout with extra options

SHELL = /bin/sh

options = -N -q -t 3
src = src/collective/cover/
minimum_coverage = 70
pep8_ignores = E501
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
	bin/pep8 --ignore=$(pep8_ignores) $(src)
	bin/pyflakes $(src)

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
