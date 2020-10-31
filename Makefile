test:
	PYTHONPATH=./src python -m unittest discover -v test

docs: clean
	pip freeze > requirements.txt
	cd docs/ && $(MAKE) html && firefox _build/html/index.html

clean:
	cd docs/ && $(MAKE) clean

.PHONY: test docs clean
