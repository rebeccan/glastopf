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
import ast

"DockerClient makes requests from Glastopf host to the DockerServer running on Docker container"
class DockerClient(object):
    
    def __init__(self):
        self.HOST, self.PORT = "127.0.0.1", 49153
        
        
    def manage_injection(self, db_name, table, query = ""):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            sock.connect((self.HOST, self.PORT))
            sock.sendall(db_name + "\n")
            sock.sendall(table + "\n")
            sock.sendall(query + "\n")
            # Receive data from the server and shut down
            rfile = sock.makefile(mode = 'rb')
            rows = []
            response = str(rfile.readline())
            while(response is not "" and not response.isspace()):
                rows.append(DockerClient.deserialze_row(response))
                response = rfile.readline()
        finally:
            sock.close()
        return rows
    
    
    @staticmethod
    def deserialze_row(row):
        try:
            d = ast.literal_eval(row)
            return d
        except:
            return {'error' : row}

   
"""runs the docker_client for testing"""
def main():
    client = DockerClient()
    client.manage_injection("data2.db", "select * from users")
    
if __name__ == "__main__":
    sys.exit(main())    