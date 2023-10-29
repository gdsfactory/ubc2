install:
	pip install -e .[dev]
	pre-commit install

dev: gmsh
	pip install -e .[dev,docs]

gmsh:
	sudo apt-get install -y python3-gmsh gmsh libglu1-mesa libxi-dev libxmu-dev libglu1-mesa-dev

test:
	pytest -s

update-pre:
	pre-commit autoupdate --bleeding-edge

git-rm-merged:
	git branch -D `git branch --merged | grep -v \* | xargs`

build:
	rm -rf dist
	pip install build
	python -m build

mask:
	python ubc2/test_masks.py

jupytext:
	jupytext docs/**/*.ipynb --to py

notebooks:
	jupytext docs/**/*.py --to ipynb

docs:
	jb build docs

.PHONY: drc doc docs
