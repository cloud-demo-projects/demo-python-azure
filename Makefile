BIN=venv/bin/
PYTHON=.$(BIN)/python
BASE_REQUIREMENTS = requirements.txt
ENV_NAME = python_azure

venv:
	python -m venv venv

clean:
	rm -rf venv
	find . -name "*.pyc" -exec rm -f {} \;

install_requirements:
	$(BIN)pip install -r $(BASE_REQUIREMENTS)

# Run unittests and generate html coverage report
test:
	coverage run --source=./src -m pytest tests
	coverage html

# Run linters check only
lint:
	$(BIN)isort . --check --skip venv
	$(BIN)black . --check --exclude venv

# Run linters and try to fix the errors
format:
	$(BIN)isort . --skip venv
	$(BIN)black . --exclude venv

# Update all libraries required to run this application
requirements_txt:
	sort -u $(BASE_REQUIREMENTS) -o $(BASE_REQUIREMENTS)
	pip-compile --output-file=requirements.txt $(BASE_REQUIREMENTS)

# Re/install the virtual environment with all requirements
install: clean venv install_requirements

# Do all checks
build: install lint test


