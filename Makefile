

all:
	@echo "'make build' to build"

build: clean
	python3 setup.py py2app

clean:
	rm -rf build dist __pycache__ .eggs

alias:
	python setup.py py2app --alias

black:
	black *.py
