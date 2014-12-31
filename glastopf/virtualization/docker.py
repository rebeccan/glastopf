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

"""
Builts Glastopf image and container either for installation or VM cleanup.
"""
def setup_docker(image = True, container = True):
    print "Building image and container for Glastopf injectable feature. If you built the container before, all container changes will be lost."
    #cleanup before docker setup
    remove_container()
    cleanup_untagged_images()
    
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
        #make directories
        os.mkdir(temp_dir + "glastopf/")
        os.mkdir(temp_dir + "glastopf/modules/")
        os.mkdir(temp_dir + "glastopf/modules/injectable/")
        #copy needed files only...
        src = base_dir + "/glastopf/modules/injectable/comment.py"
        dst = temp_dir + "glastopf/modules/injectable/comment.py"
        print src + " -> " + dst
        shutil.copyfile(src, dst)
        src = base_dir + "/glastopf/modules/injectable/user.py"
        dst = temp_dir + "glastopf/modules/injectable/user.py"
        print src + " -> " + dst
        shutil.copyfile(src, dst)
        src = base_dir + "/glastopf/modules/injectable/db_copy.py"
        dst = temp_dir + "glastopf/modules/injectable/db_copy.py"
        print src + " -> " + dst
        shutil.copyfile(src, dst)
        #init stuff
        src = base_dir + "/glastopf/modules/injectable/__init__.py"
        dst = temp_dir + "glastopf/modules/injectable/__init__.py"
        print src + " -> " + dst
        shutil.copyfile(src, dst)
        src = base_dir + "/glastopf/modules/__init__.py"
        dst = temp_dir + "glastopf/modules/__init__.py"
        shutil.copyfile(src, dst)
        src = base_dir + "/glastopf/__init__.py"
        dst = temp_dir + "glastopf/__init__.py"
        shutil.copyfile(src, dst)
        src = base_dir + "/glastopf/virtualization/docker_server.py"
        dst = temp_dir + "docker_server.py"
        print src + " -> " + dst
        shutil.copyfile(src, dst)
        
        error = False
        #create image from Dockerfile
        if(image):
            error = subprocess.call(["sudo", "docker", "build", "-t", "glastopfinjectable_dbserver_img", "glastopf/virtualization"])
            if(error):
                print "image not successfully built. container will not be created from image."
        #create container
        if(container and not error):
            #make container accessible from docker host machine only over port 49153
            error = subprocess.call(["sudo", "docker", "run", "-p", "127.0.0.1:49153:49153", "-i", "-t", "--name", "glastopfinjectable_dbserver_container", "glastopfinjectable_dbserver_img"])
            if(error):
                print "container not successfully created"
    finally:
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
    
 
"""
remove all untagged images for prevention of storage waste
"""
def cleanup_untagged_images():
    print "cleanup untagged images"
    tcpd = subprocess.Popen(["bash", "-c", "sudo docker rmi $(sudo docker images -f \"dangling=true\" -q)"], stdout=subprocess.PIPE)
    output, err = tcpd.communicate()
    
    
def remove_all_containers():
    subprocess.call(["sudo", "docker", "rm", "-f", "$(sudo docker ps -a -q)"])
    
"""remove the container called glastopfinjectable_dbserver_container if it was built before.
all changes made in the container before are lost.
"""
def remove_container():
    print "remove glastopfinjectable_dbserver_container"
    subprocess.call(["sudo", "docker", "rm", "-f", "glastopfinjectable_dbserver_container"])

"""
restarts or starts the docker container
"""
def start():
    print "start container"
    error = False
    error = subprocess.call(["sudo", "docker", "-p", "127.0.0.1:49153:49153", "restart", "glastopfinjectable_dbserver_container"])
    if(error):
        print "Failed to start Docker container for SQL injectable feature"
        print "Try to run command for installation: sudo python setup_docker.py"

def stop():
    print "stop container"
    p = subprocess.call(["docker", "stop", "glastopfinjectable_dbserver_container"], shell=True)

