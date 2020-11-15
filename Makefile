test:
	PYTHONPATH=./src python -m unittest discover test

docs: clean
	pip freeze > requirements.txt
	cd docs/ && $(MAKE) html && firefox _build/html/index.html

clean:
	cd docs/ && $(MAKE) clean

run:
	PYTHONPATH=/.src python src/main.py

.PHONY: test docs clean run
