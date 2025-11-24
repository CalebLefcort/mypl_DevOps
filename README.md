Here is the video link https://youtu.be/KYNB7Dp5CGU

# mypl_DevOps  
Debian package for mypl deployment

## Table of Contents  
- [Overview](#overview)  
- [Prerequisites](#prerequisites)  
- [Repository Structure](#repository-structure)  
- [Setup Instructions](#setup-instructions)  
  - [Clone the Repo](#clone-the-repo)  
  - [Install Dependencies](#install-dependencies)  
  - [Run Locally](#run-locally)  
- [Testing](#testing)  
- [Examples](#examples)  


---

## Overview  
This project includes the implementation of the `mypl` service (as used in CPSC 334: Linux & DevOps) 

## Repository Structure  
Here’s a high‑level look at the contents:  
```
.github/                ← CI/CD workflow files  
bin/                    ← utility scripts  
examples/               ← example inputs, usage files  
old_tests/              ← previous test cases (archived)  
screenshots/            ← screenshots for documentation  
Makefile                ← convenience for build / run commands  
debian.sh               ← Linux setup script (e.g., for Debian‑based systems)  
README.md               ← this file  
…  
```  
## Setup Instructions  

### Clone the Repo  
```bash
git clone https://github.com/CalebLefcort/mypl_DevOps.git  
cd mypl_DevOps  
```  

### Install Dependencies  
If you are using the `debian.sh` to set up a Debian/Ubuntu system:  
```bash
chmod +x debian.sh  
./debian.sh  
```  

### Run Locally  
```bash
make deb_build
```
once installed call using
```bash
mypl program name
```


## Testing  
To execute unit tests:  
```bash
make test 
```  

## Examples  
In the `examples/` directory you’ll find sample input files and usage scenarios. For example:  
```bash
./examples/sample1.txt  
```  
Run the service with this example to verify correct behavior.



