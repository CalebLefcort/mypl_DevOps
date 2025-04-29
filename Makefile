APT_PACKAGES = python3 pylint python3-pytest lintian

install:
	apt update
	apt install -y $(APT_PACKAGES)

build:
	echo "Building"

lint:
	pylint --exit-zero ./bin

test:
	pytest ./bin/project_tests.py

deb_build:
	bash debian.sh

lint_deb:
	lintian mypl_*.deb || true

clean_deb:
	rm -rf mypl_*.deb pkg


