# convenience makefile to boostrap & run buildout
# use `make options=-v` to run buildout with extra options

SHELL = /bin/sh

options = -N -q -t 3
src = src/collective/cover/
minimum_coverage = 70
pep8_ignores = E501
css_ignores = ! -name bootstrap\* ! -name jquery\*
js_ignores = ! -name bootstrap\* ! -name jquery\*

ack:
	sudo apt-get install ack-grep

nodejs:
	sudo apt-add-repository ppa:chris-lea/node.js -y
	sudo apt-get update 1>/dev/null
	sudo apt-get install nodejs npm -y

csslint: nodejs
	npm install csslint -g 1>/dev/null

jshint: nodejs
	npm install jshint -g 1>/dev/null

install:
	mkdir -p buildout-cache/downloads
	python bootstrap.py -c travis.cfg
	bin/buildout -c travis.cfg $(options)

quality_assurance: ack csslint jshint
	bin/pep8 --ignore=$(pep8_ignores) $(src)
	bin/pyflakes $(src)
	find $(src) -type f -name *.css $(css_ignores) | xargs csslint | ack-grep --passthru error
	find $(src) -type f -name *.js $(js_ignores) -exec jshint {} ';'

tests: quality_assurance
	bin/test
	./coverage.sh $(minimum_coverage)
