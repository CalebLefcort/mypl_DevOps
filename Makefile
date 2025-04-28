# Python-related settings
PYTHON = python3

# Directories
SRC_DIR = .
TEST_DIR = .
LINT_DIR = .

# Linting
LINTER = pylint

# Testing
TEST_CMD = pytest

# Packages to install using apt
APT_PACKAGES = pylint pytest

# Targets
.PHONY: all lint test install clean

# Default target (runs everything)
all: lint test

# Install dependencies using apt
install:
	apt update
	apt install -y $(APT_PACKAGES)

# Run linting
lint:
	$(LINTER) $(LINTER_OPTS) $(LINT_DIR)

# Run tests
test:
	$(TEST_CMD) $(TEST_OPTS) $(TEST_DIR)

# Clean up (remove .pyc files)
clean:
	find $(SRC_DIR) -name "*.pyc" -exec rm -f {} \;
