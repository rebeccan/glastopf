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

import sys
import os
import os.path
import SocketServer

from glastopf.modules.injectable.db_copy import DB_copy
from glastopf.modules.injectable.user import User
from glastopf.modules.injectable.comment import Comment

#TODO RN: SocketServer handles requests synchronously
# -> implement threading with workers
"DockerServer is running on Docker container. It receives and handles requests from DockerClient Glastopf host."
class DockerServer(SocketServer.StreamRequestHandler):
    
    """
    reads 2 lines from connections (one with database name, one with query string)
    and answers with lines, containing the response from the db
    """
    def handle(self):
        db_name = self.rfile.readline().strip()
        table = self.rfile.readline().strip()
        query = self.rfile.readline()
        print "{} wrote:".format(self.client_address[0])
        print db_name
        print table
        print query
        result = self.handle_query(db_name, table, query)
        for r in result:
            self.wfile.write(str(r) + "\n")
            self.wfile.flush()
        self.wfile.write("\n")
        self.wfile.flush()
            

    def handle_query(self, db_name, table, query):
        #create copy
        db_dir = os.getcwd() + '/db'
        copy = DB_copy(db_name, work_dir = db_dir)
        copy.create_copy()
        #create session
        conn_str = copy.get_db_copy_conn_str()
        if(table == "comments"):
            session = Comment.connect(conn_str)
            #make injection
            injectionResult = Comment.injection(session, query)
        elif(table == "users"):
            session = User.connect(conn_str)
            #make injection
            injectionResult = User.injection(session, query)
        session.commit()
        #close db connection
        session.close()
        return injectionResult


"""runs the docker_server"""
def main():
    HOST, PORT = "0.0.0.0", 49153
    
    print "start docker_server on host " + str(HOST) + " port " + str(PORT)
    
    server = SocketServer.TCPServer((HOST, PORT), DockerServer)

    server.serve_forever()
    

if __name__ == "__main__":
    sys.exit(main())