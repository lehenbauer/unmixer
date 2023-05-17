

all:
	@echo "'make build' to build"

build:
	python3 setup.py py2app

clean:
	rm -rf build dist

alias:
	python setup.py py2app --alias
