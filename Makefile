# convenience makefile to boostrap & run buildout
# use `make options=-v` to run buildout with extra options

options = -N -q -t 3
pep8_ignores = E501
src = src/collective/cover/
minimum_coverage = 70

nodejs:
	sudo apt-get install python-software-properties
	sudo apt-add-repository ppa:chris-lea/node.js
	sudo apt-get update
	sudo apt-get install nodejs npm -y

jshint: nodejs
	npm install jshint -g

prerequisites: jshint
	sudo apt-get install -q pep8 pyflakes
	pip install -q createzopecoverage
	mkdir -p buildout-cache/downloads

install: prerequisites
	python bootstrap.py -c travis.cfg
	bin/buildout -c travis.cfg $(options)

tests:
	pep8 --ignore=$(pep8_ignores) $(src)
	pyflakes $(src)
	bin/test
	./coverage.sh $(minimum_coverage)
	find $(src) -name '*.js' -exec jshint {} ';'
