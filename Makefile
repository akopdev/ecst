.NOTPARALLEL: ;          # wait for this target to finish
.EXPORT_ALL_VARIABLES: ; # send all vars to shell
.PHONY: all 			 			 # All targets are accessible for user
.DEFAULT: help 			 		 # Running Make will run the help target

PYTHON = @.venv/bin/python -m

# -------------------------------------------------------------------------------------------------
# help: @ List available tasks on this project
# -------------------------------------------------------------------------------------------------
help:
	@grep -oE '^#.[a-zA-Z0-9]+:.*?@ .*$$' $(MAKEFILE_LIST) | tr -d '#' |\
	awk 'BEGIN {FS = ":.*?@ "}; {printf "  make%-10s%s\n", $$1, $$2}'
	 
# -------------------------------------------------------------------------------------------------
# init: @ Setup local environment
# -------------------------------------------------------------------------------------------------
init: activate install

# -------------------------------------------------------------------------------------------------
# update: @ Update package dependencies and install them
# -------------------------------------------------------------------------------------------------
update: compile install

# -------------------------------------------------------------------------------------------------
# Activate virtual environment
# -------------------------------------------------------------------------------------------------
activate:
	@python3 -m venv .venv
	@. .venv/bin/activate 
	$(PYTHON) pip install pip-tools

# -------------------------------------------------------------------------------------------------
# Update package dependencies
# -------------------------------------------------------------------------------------------------
compile:
	$(PYTHON) piptools compile --upgrade requirements.in 
	$(PYTHON) piptools compile --upgrade requirements-dev.in
	
# -------------------------------------------------------------------------------------------------
# Install packages to current environment
# -------------------------------------------------------------------------------------------------
install:
	$(PYTHON) piptools sync requirements.txt requirements-dev.txt

# -------------------------------------------------------------------------------------------------
# test: @ Run tests using pytest
# -------------------------------------------------------------------------------------------------
test:
	$(PYTHON) pytest tests --cov=.

# -------------------------------------------------------------------------------------------------
# format: @ Format source code and auto fix minor issues
# -------------------------------------------------------------------------------------------------
format:
	$(PYTHON) black --line-length=100 app
	$(PYTHON) isort app


# -------------------------------------------------------------------------------------------------
# lint: @ Checks the source code against coding standard rules and safety
# -------------------------------------------------------------------------------------------------
lint: lint.flake8 lint.safety lint.docs

# -------------------------------------------------------------------------------------------------
# flake8 
# -------------------------------------------------------------------------------------------------
lint.flake8: 
	$(PYTHON) flake8 --exclude=.venv,.eggs,*.egg,.git,migrations \
									 --filename=*.py,*.pyx \
									 --config=.flake8 \
									 app


# -------------------------------------------------------------------------------------------------
# safety 
# -------------------------------------------------------------------------------------------------
lint.safety: 
	$(PYTHON) safety check --full-report -r requirements.txt

# -------------------------------------------------------------------------------------------------
# pydocstyle
# -------------------------------------------------------------------------------------------------
# Ignored error codes:
#   D100	Missing docstring in public module
#   D101	Missing docstring in public class
#   D102	Missing docstring in public method
#   D103	Missing docstring in public function
#   D104	Missing docstring in public package
#   D105	Missing docstring in magic method
#   D106	Missing docstring in public nested class
#   D107	Missing docstring in __init__
lint.docs: 
	$(PYTHON) pydocstyle --convention=numpy --add-ignore=D100,D101,D102,D103,D104,D105,D106,D107 .


# -------------------------------------------------------------------------------------------------
#  build: @ Build container
#  -------------------------------------------------------------------------------------------------
build:
	@docker build -t app:latest .

# -------------------------------------------------------------------------------------------------
#  clean: @ Clean up local environment
#  -------------------------------------------------------------------------------------------------
clean:
	@rm -rf .venv/ dist/ build/ *.egg-info/ .pytest_cache/ .coverage coverage.xml
