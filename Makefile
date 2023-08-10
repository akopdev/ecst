.NOTPARALLEL: ;          # wait for this target to finish
.EXPORT_ALL_VARIABLES: ; # send all vars to shell
.PHONY: all build		 # All targets are accessible for user
.DEFAULT: help 			 # Running Make will run the help target

PY = .venv/bin/python
PYTHON = @$(PY) -m
APP = ecst

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

# -------------------------------------------------------------------------------------------------
# Install packages to current environment
# -------------------------------------------------------------------------------------------------
install:
	$(PYTHON) pip install -e .
	$(PYTHON) pip install -e .[dev]

# -------------------------------------------------------------------------------------------------
# test: @ Run tests using pytest
# -------------------------------------------------------------------------------------------------
test:
	$(PYTHON) pytest tests --cov=.

# -------------------------------------------------------------------------------------------------
# format: @ Format source code and auto fix minor issues
# -------------------------------------------------------------------------------------------------
format:
	$(PYTHON) black --line-length=100 $(APP)
	$(PYTHON) isort $(APP)


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
									 $(APP)


# -------------------------------------------------------------------------------------------------
# safety 
# -------------------------------------------------------------------------------------------------
lint.safety: 
	$(PYTHON) safety check

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
	@docker build -t $(APP):latest -t $(APP):$$($(PY) -m setup --version) .

# -------------------------------------------------------------------------------------------------
#  clean: @ Clean up local environment
#  -------------------------------------------------------------------------------------------------
clean:
	@rm -rf .venv/ dist/ build/ *.egg-info/ .pytest_cache/ .coverage coverage.xml
