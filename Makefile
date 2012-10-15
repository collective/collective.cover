# convenience makefile to boostrap & run buildout
# use `make options=-v` to run buildout with extra options

pep8_ignores = E501
options = -N -q -t 3

install:
	python bootstrap.py -c travis.cfg
	bin/buildout -c travis.cfg $(options)

tests:
	@bin/test
	@bin/pyflakes src/
	@bin/pep8 --ignore=$(pep8_ignores) src/
