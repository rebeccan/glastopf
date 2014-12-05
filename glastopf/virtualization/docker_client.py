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


class DockerClient(object):
    
    def __init__(self):
        ##client = Client(base_url='tcp://127.0.0.1:2375')
        ##instantiate Client object
        #client = Client(base_url='unix://var/run/docker.sock')
        ##create image from Dockerfile
        ##response = client.build(path='/opt/glastopf/glastopf/virtualization', tag='sqlsandbox_image') #TODO RN: remove hardcoded path
        #response = client.build('.', 'sqlsandbox_image')
        #print response
        #container = client.create_container(image = 'sqlsandbox_image', name='sqlsandbox_container', ports=[(1337, 'tcp')])
        #client.start(container=container.get('Id'), port_bindings={1337: ('0.0.0.0', 1338)})
        return
    

    
    
    
    
    