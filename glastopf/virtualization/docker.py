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


def setup_docker(image = True, container = True):
    #cleanup before docker setup
    #cleanup_untagged_images()
    remove_container()
    
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
        #src = base_dir + "/glastopf/modules/injectable/"
        #dst = temp_dir + "glastopf/modules/injectable/"
        src = base_dir + "/glastopf/"
        dst = temp_dir + "glastopf/"
        print src + " -> " + dst
        #shutil.copytree(src, dst)
        shutil.copytree(src, dst, ignore=ignore_temp)
        src = base_dir + "/glastopf/virtualization/docker_server.py"
        dst = temp_dir + "docker_server.py"
        print src + " -> " + dst
        #os.mkdir(temp_dir + "glastopf/virtualization")
        shutil.copyfile(src, dst)
        
        error = False
        #create image from Dockerfile
        if(image):
            #sudo docker build -t my_application_img .
            error = subprocess.call(["sudo", "docker", "build", "-t", "glastopfinjectable_dbserver_img", "glastopf/virtualization"])
            #create container
            if(error):
                print "image not successfully built. container will not be created from image."
        #create container
        if(container and not error):
            #create container and run it
            #make container accessible from docker host machine only with 127.0.0.1 configuration over port 49153
            error = subprocess.call(["sudo", "docker", "run", "-p", "127.0.0.1:49153:49153", "-i", "-t", "--name", "glastopfinjectable_dbserver_container", "glastopfinjectable_dbserver_img"])
            if(error):
                print "container not successfully created"
            stop()
    finally:
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        


def ignore_temp(src_path,content):
    if ('temp' in content):
        return 'temp'
        #Here when test folder found it will passed 
        #to ignore list
    else:
        return []
    
    
 
"""
remove all untagged images, remove all containers
"""
def cleanup_untagged_images():
    print "cleanup untagged images"
    #sudo docker rmi $(sudo docker images -f "dangling=true" -q)
    subprocess.call(["sudo", "docker", "rmi " "$(sudo docker images | grep \"^<none>\" | awk \"{print $3}\")"])
    
def remove_all_containers():
    subprocess.call(["sudo", "docker", "rm", "-f", "$(sudo docker ps -a -q)"])
    
def remove_container():
    print "remove glastopfinjectable_dbserver_container"
    subprocess.call(["sudo", "docker", "rm", "-f", "glastopfinjectable_dbserver_container"])

"""
starts or restarts the docker container
"""
def start():
    print "start container"
    subprocess.call(["sudo", "docker", "-p", "127.0.0.1:49153:49153", "restart", "glastopfinjectable_dbserver_container"])


def stop():
    print "stop container"
    subprocess.call(["sudo" "docker", "stop", "glastopfinjectable_dbserver_container"])

