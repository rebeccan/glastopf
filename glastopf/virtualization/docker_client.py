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

import socket
import sys

class DockerClient(object):
    
    def __init__(self):
        self.HOST, self.PORT = "localhost", 3066
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        
    def manage_injection(self, db_name = "", query = ""):
        try:
            # Connect to server and send data
            self.sock.connect((self.HOST, self.PORT))
            self.sock.sendall(db_name + "\n")
            self.sock.sendall(query + "\n")
            # Receive data from the server and shut down
            rfile = self.sock.makefile(mode = 'rb')
            response = rfile.readline()
        finally:
            self.sock.close()
        return response

   
"""runs the docker_client for testing"""
def main():
    client = DockerClient()
    client.manage_injection("data2.db", "select * from users")
    
if __name__ == "__main__":
    sys.exit(main())    