# Copyright (C) 2014  Rebecca Neigert
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 
import shutil
import os
import subprocess

def start_container():
    #start container
    subprocess.call(["sudo", "docker", "start", "glastopfinjectable_dbserver_container"])
        
    
def setup_docker(image = True, container = True):
    
    #TODO RN: create temporary folder under virtualization with all needed glastopf files
    #needed: injectable folder, data.db,
    base_dir = os.getcwd()
    temp_dir = base_dir + '/glastopf/virtualization/temp/'
    print temp_dir
    os.mkdir(temp_dir)
    try:
        src = base_dir + "/db/data.db"
        dst = temp_dir + "db/data.db"
        print src + " -> " + dst
        os.mkdir(temp_dir + "db")
        shutil.copyfile(src, dst)
        src = base_dir + "/glastopf/modules/injectable/"
        dst = temp_dir + "glastopf/modules/injectable/"
        print src + " -> " + dst
        shutil.copytree(src, temp_dir + "/glastopf/modules/injectable/")
        src = base_dir + "/glastopf/virtualization/docker_server.py"
        dst = temp_dir + "glastopf/virtualization/docker_server.py"
        print src + " -> " + dst
        os.mkdir(temp_dir + "glastopf/virtualization")
        shutil.copyfile(src, dst)
        
        error = False
        #create image from Dockerfile
        if(image):
            #sudo docker build -t my_application_img .
            error = subprocess.call(["sudo", "docker", "build", "-t", "glastopfinjectable_dbserver_img", "glastopf/virtualization"])
            #create container
            if(error):
                print "image not successfully built. container not created."
        #create container
        if(container and not error):
            #sudo docker run --name my_application_instance -P -i -t my_application_img
            error = subprocess.call(["sudo", "docker", "run", "--name", "glastopfinjectable_dbserver_container", "-P", "-i", "-t", "glastopfinjectable_dbserver_img"])
            if(error):
                print "container not successfully created"
    finally:        
        #TODO RN: delete temporary folder
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        


 
"""
remove all untagged images
"""
def cleanup_images():
    subprocess.call(["sudo", "docker", "rmi" "$(sudo docker images | grep \"^<none>\" | awk \"{print $3}\")"])

"""
starts the docker container
"""
def start():
    print "start container"
    subprocess.call(["sudo", "docker", "start", "-a", "glastopfinjectable_dbserver_container"])

def stop():
    print "stop container"
    subprocess.call(["docker", "stop", "glastopfinjectable_dbserver_container"])

