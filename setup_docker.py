#!python
from glastopf.virtualization import docker
import sys

import glastopf.seed

def _setup_docker():
    print "setup docker"
    docker.setup_docker()
    
def main():
    glastopf.seed.seed('sqlite:///db/data.db')
    _setup_docker()

if __name__ == '__main__':
    sys.exit(main())