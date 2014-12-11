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
import SocketServer

from glastopf.modules.injectable.db_copy import DB_copy
from glastopf.modules.injectable.user import User
from glastopf.modules.injectable.injection import Injection

#TODO: SocketServer handles requests synchronously
# -> implement threading with workers
class DockerServer(SocketServer.StreamRequestHandler):
    
    """
    reads 2 from connections (one with database name, one with query string)
    and answers with line, containing the response from the db
    """
    def handle(self):
        db_name = self.rfile.readline().strip()
        query = self.rfile.readline()
        print "{} wrote:".format(self.client_address[0])
        print db_name
        print query
        response = self.handle_query(db_name, query)
        print response
        self.wfile.writeline(reponse)
        self.wfile.flush()
            
            

    def handle_query(self, db_name, query):
        #create copy
        copy = DB_copy(db_name).create_copy()
        #create session
        conn_str = copy.get_db_copy_conn_str()
        session = User.connect(conn_str)
        #make injection
        injectionResult = User.injection(session, query)
        #close db connection
        #session.close()
        return injectionResult


"""runs the docker_server"""
def main():
    HOST, PORT = "localhost", 3066

    server = SocketServer.TCPServer((HOST, PORT), DockerServer)

    server.serve_forever()
    

if __name__ == "__main__":
    sys.exit(main())