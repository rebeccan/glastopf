#!python
from glastopf.virtualization import docker
import sys

def _setup_docker():
    print "setup docker"
    docker.setup_docker()
    
def main():
    _setup_docker()

if __name__ == '__main__':
    sys.exit(main())