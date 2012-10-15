# convenience makefile to boostrap & run buildout
# use `make options=-v` to run buildout with extra options

pep8_ignores = E501
buildout_options =

install:
	python bootstrap.py -c travis.cfg
	bin/buildout -c travis.cfg $(buildout_options)

tests:
	@bin/test
	@bin/pyflakes src/
	@bin/pep8 --ignore=$(pep8_ignores) src/
