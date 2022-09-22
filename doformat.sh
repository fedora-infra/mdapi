#!/bin/sh

black --line-length=100 mdapi/ tests/
isort --profile=black mdapi/ tests/
flake8 --max-line-length=100 mdapi/ tests/
