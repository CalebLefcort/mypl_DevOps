PYTHON = python3

SRC_DIR = .
TEST_DIR = ./bin/project_tests.py
LINT_DIR = ./bin

LINTER = pylint

TEST_CMD = pytest

APT_PACKAGES = pylint python3-pytest

install:
	apt update
	apt install -y $(APT_PACKAGES)

build:
	echo "Building"

lint:
	$(LINTER) $(LINTER_OPTS) $(LINT_DIR)

test:
	$(TEST_CMD) $(TEST_OPTS) $(TEST_DIR)
