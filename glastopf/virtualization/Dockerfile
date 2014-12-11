# Install a sqlite db included in the default ubuntu repositories.

FROM ubuntu:14.04
MAINTAINER Rebecca Neigert



# Update the sources list
RUN apt-get update

# Install Python, Basic Python Tool and other stuff
RUN sudo apt-get install -y python2.7 python-openssl python-gevent libevent-dev python2.7-dev build-essential make
RUN sudo apt-get install -y python-chardet python-requests python-sqlalchemy python-lxml
RUN sudo apt-get install -y python-beautifulsoup mongodb python-pip python-dev python-setuptools
RUN sudo apt-get install -y g++ git php5 php5-dev liblapack-dev gfortran libmysqlclient-dev
RUN sudo apt-get install -y libxml2-dev libxslt-dev

#open port 3066
EXPOSE 3066

#copy original data.db
#copy docker-server.py
#ADD docker_server.py /glastopf/
ADD temp /glastopf/

# Set the default directory where CMD will execute
WORKDIR /glastopf

# Set the default command to execute
# when creating a new container
CMD ["python", "/glastopf/virtualization/docker_server.py"]