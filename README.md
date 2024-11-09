# Sonic PoC ![Version](https://img.shields.io/docker/v/thefueley/sonic-poc?style=for-the-badge&logo=python&logoColor=white&label=OlympiLearn&link=https%3A%2F%2Folympilearn.com)

## Overview

This project is a proof of concept for the Sonic application. It includes instructions on how to run the app using the Makefile, Docker container, and how to build the app. Additionally, it provides guidelines for using Git to check in changes.

## Prerequisites

- Python 3.x
- Virtual environment (venv)
- Docker
- Make

## Setup

### Virtual Environment

Create a virtual environment:

```sh
python -m venv venv
```

Activate the virtual environment:

```sh
source venv/bin/activate
```

Install the required dependencies:

```sh
pip install -r requirements.txt
```

## Running the App

### Using Makefile

Build the app:

```sh
make build
```

Run the app with Docker:

```sh
make run
```

Kill the app:

```sh
make stop
```

```sh
make clean
```

View Docker Logs:

```sh
make logs
```

## Development

Create a local branch:

```sh
git checkout -b <branch-name>
```

Make changes to the code.

Run the app to verify functionality.

Browse to `http://localhost:5000` to view the app.

If the app is already running in Docker and you want to view new changes you made, you can rerun the app: `make refresh`.

Then refresh the browser to view the changes.

Once you're done coding, push your changes to the remote repository.

### Git Workflow

Add changes to the staging area:

```sh
git add .
```

Commit changes:

```sh
git commit -m "Your commit message"
```

Push changes to the remote repository:

```sh
git push -u origin <branch-name>
```

## Linting

Every time you commit changes, the linter will run to ensure the code is clean.

Black is the linter used in this project.
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Pylint is also used to check for errors in the code.
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

Read the output of these tools and fix any issues before pushing your changes.
