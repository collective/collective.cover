# convenience makefile to boostrap & run buildout
# use `make options=-v` to run buildout with extra options

options = -N -q -t 3
src = src/collective/cover/
minimum_coverage = 70
pep8_ignores = E501
css_ignores = ! -name bootstrap* ! -name jquery*
js_ignores = ! -name bootstrap* ! -name jquery*

nodejs:
	sudo apt-add-repository ppa:chris-lea/node.js -y
	sudo apt-get update
	sudo apt-get install nodejs npm -y

csslint: nodejs
	npm install csslint -g

jshint: nodejs
	npm install jshint -g

install:
	mkdir -p buildout-cache/downloads
	python bootstrap.py -c travis.cfg
	bin/buildout -c travis.cfg $(options)

quality_assurance: csslint jshint
	bin/pep8 --ignore=$(pep8_ignores) $(src)
	bin/pyflakes $(src)
	find $(src) -name *.css $(css_ignores) -exec csslint {} ';'
	find $(src) -name *.js $(js_ignores) -exec jshint {} ';'

tests: quality_assurance
	bin/test
	./coverage.sh $(minimum_coverage)
