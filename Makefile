.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("  %-20s %s" % (target, help))
	
	match = re.match(r'^#>\s+([a-zA-Z_\s]+)$$', line)
	if match:
		print()
		section = match.group(1).strip()
		print("%-20s" % (section, ))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := @python3 -c "$$BROWSER_PYSCRIPT"



# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------
.PHONY: help

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

# ----------------------------------------------------------
#> Virtual Env
# ----------------------------------------------------------
.PHONY: create-venv activate-venv

create-venv: ## craeate virtual Environment
	virtualenv .venv


	
# ----------------------------------------------------------
# Coding Helpers
# ----------------------------------------------------------

clean: clean-build clean-pyc clean-test docker-clean ## remove all build, test, coverage and Python artifacts

# ----------------------------------------------------------
#> Docker
# ----------------------------------------------------------
.PHONY: docker-build docker-clean docker-run docker-test

docker-build: ## build the docker container
	docker compose build 

docker-run: docker-build ## build and execute server in a docker container
	docker compose up  --remove-orphans
	
docker-test: docker-build ## test server in a docker container
	docker compose run --rm aiml python -m pytest

docker-clean: ## clean container
	docker rm aiml --stop  --force

docker-cache-prune: ## clean all cache
	docker buildx prune -f

docker-mrproper: ## remove all unused containers, images, networks, and build cache
	# docker system prune -f
	docker image prune -a -f
	docker builder prune -a -f
	
docker-shell: ## open a bash to inspect the 'web' service container
	docker compose exec web bash

docker-exec-foo-bar:  ## example of executing a command in a running container using CLI 
	docker compose exec web aiml foo bar
	
# ----------------------------------------------------------
#> Sync with Cloud
# ----------------------------------------------------------
.PHONY: sync-cloud-code sync-cloud-db sync-cloud

SSH_SERVER := root@aiml
CODE_PATH:= /opt/aiml
CERT_PATH:= /opt/aiml/deploy/ssl

sync-cloud-code: ## sync code with cloud
	ssh $(SSH_SERVER) mkdir -p $(CODE_PATH)/aiml/
	rsync -azvP --exclude __pycache__  aiml/ $(SSH_SERVER):$(CODE_PATH)/aiml/
	rsync -azvP docker-compose.yml Dockerfile Makefile setup.py $(SSH_SERVER):$(CODE_PATH)/
	rsync -azvP requirements/ $(SSH_SERVER):$(CODE_PATH)/requirements/
	rsync -azvP deploy/ $(SSH_SERVER):$(CODE_PATH)/deploy/
	rsync -azvP *.rst .env $(SSH_SERVER):$(CODE_PATH)/
	ssh $(SSH_SERVER) chown -R 1000:1000 $(CERT_PATH)

sync-cloud-db: ## sync workspace with cloud
	ssh $(SSH_SERVER) mkdir -p $(CODE_PATH)/data/db/
	rsync -azvP ~/workspace/aiml/db/ $(SSH_SERVER):$(CODE_PATH)/data/db/
	ssh $(SSH_SERVER) chown -R 1000:1000 $(CODE_PATH)/data

sync-cloud: sync-cloud-code sync-cloud-db ## sync current dev environtment with cloud one
	@echo "sync done!"
			

# ----------------------------------------------------------
#> Kubernetes
# ----------------------------------------------------------
.PHONY: sync-cloud-code sync-cloud-db sync-cloud

kubernetes-konvert: ## Convert docker-compose.yaml files to K8 infra
	kompose convert --out aiml.kubernetes.yaml
	kompose convert --out helm -c
	

# ----------------------------------------------------------
#> Upgrading project layout from coockiecutter template
# ----------------------------------------------------------
.PHONY: template-cleaning template-upgrade

COOKIECUTTER_CONFIG := .cookiecutter.json
COOKIECUTTER_PACKAGE := cib_pypackage

template-cleaning: ## clean specific user data from template files
	@echo "- Cleaning: $(COOKIECUTTER_CONFIG)"
	sed -i  '/^\s*"_.*$\/d' $(COOKIECUTTER_CONFIG)

CURRENT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
TEMPLATE_BRANCH := "cookiecutter_template"

template-upgrade: ## upgrade code from template
	@echo "- Current branch: $(CURRENT_BRANCH)"
	@echo "- Stashing changes"
	@git stash
	@echo "- Switching to $(TEMPLATE_BRANCH)"
	@git checkout $(TEMPLATE_BRANCH) || git checkout -b $(TEMPLATE_BRANCH)
	@echo "- Now on branch: $(shell git rev-parse --abbrev-ref HEAD)"

	cookiecutter --replay-file  $(COOKIECUTTER_CONFIG) $(COOKIECUTTER_PACKAGE) -f --output-dir ..

	@git add *
	@git commit -m "template upgrade"

	@echo "- Switching back to the original branch..."
	@git checkout $(CURRENT_BRANCH)
	@echo "- Unstashing changes"
	@git stash pop
	@echo "- Now back on branch: $(shell git rev-parse --abbrev-ref HEAD)"

setup-workspace: template-cleaning create-venv ## prepare workspace to be ready for team collaboration
	@echo "- Checking Git Repository"
	@git status  || git init --initial-branch=main && git add . && git commit -m "Initial commit"
	
soft-reset-workspace:  ## soft reset workspace to initial state (replacing all known files)
	@echo "------------------------------------------------------------------"
	@echo "WARNING: Creating Missing Files from Template to Initial State"
	@echo "------------------------------------------------------------------"
	@printf "Are you sure? (y/n): " && read REPLY && [ $$REPLY = "y" ]  || (echo "Execution Aborted" ; exit 0)
	@echo "- Soft Reseting Workspace ..."
	cookiecutter --replay-file  $(COOKIECUTTER_CONFIG) $(COOKIECUTTER_PACKAGE) -f -s --output-dir ..
	make template-cleaning

reset-workspace:  ## reset workspace to initial state (replacing all known files)
	@echo "********************************************************"
	@echo "WARNING: Replacing Files from Template to Initial State"
	@echo "WARNING: .git repository will be preserved"
	@echo "********************************************************"
	@printf "Are you sure? (y/n): " && read REPLY && [ $$REPLY = "y" ]  || (echo "Execution Aborted" ; exit 0)
	@echo "- Reseting Workspace ..."
	cookiecutter --replay-file  $(COOKIECUTTER_CONFIG) $(COOKIECUTTER_PACKAGE) -f --output-dir ..
	make template-cleaning

	


# ----------------------------------------------------------
#> Testing
# ----------------------------------------------------------
.PHONY: test test-parallel test-all clean-test ptw

test: ## run tests quickly with the default Python
	pytest

test-parallel: ## run parallel pytests with the default Python
	@python3 -n 5

test-all: ## run tests on every Python version with tox
	tox

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

ptw: ## pytest-watch
	ptw -- -s -n 2


# ----------------------------------------------------------
#> Code Quality
# ----------------------------------------------------------
.PHONY: coverage lint lint/pylint lint/flake8 lint/black

coverage: ## check code coverage quickly with the default Python
	coverage run --source aiml -m pytest
	coverage run -a --source tests -m pytest

	# coverage combine
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

lint/pylint: ## pylint checker
	pylint aiml tests

lint/flake8: ## check style with flake8
	flake8 aiml tests
lint/black: ## check style with black
	black --check aiml tests

lint: lint/pylint lint/flake8 lint/black ## check style

# ----------------------------------------------------------
#> Documentation
# ----------------------------------------------------------
.PHONY: docs livehtml #servedocs

# ----------------------------------------------------------
# Sphinx Parameters
# ----------------------------------------------------------
# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = @python3 -m sphinx
SPHINXPROJ    = python-coding-challenge
SOURCEDIR     = docs
BUILDDIR      = docs/_build
AUTODIR       = docs/_autosummary
PORT          = 18086
IGNORE        = ".* *.log *.json $(AUTODIR) $(BUILDDIR)"

# seconds before opening the browser
AUTODELAY     = 0

# a sleep to avoid too much CPU use while typing documentation
# and the system is rebuilind too fast
AUTOOPS       = --pre-build "sleep 5"

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/aiml.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ aiml
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

livehtml:
	nice -n 20 sphinx-autobuild -b html $(ALLSPHINXOPTS) --open-browser --port $(PORT) --watch . --re-ignore "\.git/" $(SOURCEDIR) $(BUILDDIR)/html --ignore $(IGNORE) --delay $(AUTODELAY) $(AUTOOPS)

clean-doc: ## remove docs artifacts
	rm -fr docs/_build

# ----------------------------------------------------------
#> Project Initial Setup
# ----------------------------------------------------------
.PHONY: develop-setup install-testing-requisites

develop-setup: install-testing-requisites ## install module as developer
	@python3 setup.py develop 

install-testing-requisites: ## install testing requisites
	@pip install -U -r requirements/base.txt
	@pip install -U -r requirements/testing.txt

# ----------------------------------------------------------
#> Deployment 
# ----------------------------------------------------------
.PHONY: release dist install clean-build clean-pyc

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	@python3 setup.py sdist
	@python3 setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	@python3 setup.py install

clean-build: ## remove build artifacts
	rm -fr .surmlcache
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +


clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

