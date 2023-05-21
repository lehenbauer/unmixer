

all:
	@echo "'make build' to build"

build: clean
	python3 setup.py py2app

clean:
	rm -rf build dist __pycache__ .eggs UnMixer.dmg

alias:
	python setup.py py2app --alias

black:
	black *.py

commit: black
	git commit -a

dmg: unmount
	@echo "...assuming your build is current."
	rm -rf UnMixer.dmg
	create-dmg --volname "UnMixer" --window-pos 200 120 --window-size 800 400 --icon-size 100 --icon support/icon.jpeg 200 190 --app-drop-link 600 185 "UnMixer.dmg" dist/

unmount:
	@if [ -d /Volumes/UnMixer ]; then \
		hdiutil detach /Volumes/UnMixer; \
	fi

