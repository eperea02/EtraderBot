.DEFAULT_GOAL:=help
.PHONY: build run


SHELL := /bin/bash

FLASK_APP := "ETradeBot:app"
FLASK_ENV := development
FLASK_DEBUG := True
DEV_ARGS= FLASK_APP=${FLASK_APP} FLASK_ENV=${FLASK_ENV} FLASK_DEBUG=${FLASK_DEBUG}
BUILD_ARGS := --build-arg TOKEN=${ONE_SOURCE_TOKEN}
IMAGE_NAME := etradebot


install:					## Clean Install of Dependencies and Env variables
	@./tools/clean_install.sh
	@make activate

activate:
	source ./.venv/bin/activate

dev:						## Run site in Dev Mode
	${DEV_ARGS} flask run -h localhost -p 8000

dockerDev:					## Run site in Dev Mode
	${DEV_ARGS} flask run -h "0.0.0.0" -p 8000

dd:							## Run site in Dev Mode
	${DEV_ARGS} flask run -h "0.0.0.0" -p 8000
test: 						## Run Unit Tests
	@coverage run -m pytest

fixlf: 						## Lint/Format code and push to branch
	@make format
	@make fixlint

checkformat:				## Chceck formatting of code using black 
	black --check .

format:						## Format code using black
	black .

lint:						## Lint code using flake
	flake8 .

fixlint:					## Autofix linting with autoflake8
	autoflake8 -r -i  --exit-zero-even-if-changed --remove-duplicate-keys --remove-unused-variables .

docker:						## Build and run Docker Image
	make buildImage
	make runImage

buildImage: 				## Build Current Image
	@docker build ${BUILD_ARGS} -t ecservicecheck:latest . 

buildImageNoCache: 				## Build Current Image
	@docker build ${BUILD_ARGS} --no-cache -t ecservicecheck:latest . 

buildSlim: 				## Build Current Image
	@docker build ${BUILD_ARGS} -f ./.docker/slim.dockerfile -t ecservicecheck:latest . 

runImage: 					## Build Current Image
	docker run -it -p 8000:8000 --env-file .env ecservicecheck:latest 

shellDev:					## [Dev] - Bring up shell of devservice container for checking environment
	docker run -it --entrypoint /bin/bash --env-file .env -p 8000:8000 ecservicecheck:latest

bindShell: 
	docker run -it --entrypoint /bin/bash -v /$(shell pwd):/app --env-file .env  -p 8000:8000 ecservicecheck:latest

pamvault: 
	curl -X POST -H "Content-Type: application/json"  http://localhost:8000/pamvault

logintest: 
	curl -X GET --negotiate -u eperea https://login.swiss.intel.com/login

itest:						## Interactively test a command, will rerun command on save
	ptw --runner "pytest -v -s ./tests/test_query_request.py"

help:						## Show this help.
	@echo "EC Service Check Commands"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m (default: help)\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
