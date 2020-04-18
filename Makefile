install:
	pip install -r dev-requirements.txt
	pip install --editable .
	pre-commit install

test:
	pytest

coverage:
	coverage run euchre_env/bin/pytest; coverage report; coverage html

coverage-html: coverage
	open htmlcov/index.html