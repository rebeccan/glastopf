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


from glastopf.modules.handlers import base_emulator
from glastopf.modules.fingerprinting.attacker import Attacker
from glastopf.modules.injectable.db_copy import DB_copy
from glastopf.modules.injectable.user import User
from glastopf.modules.injectable.injection import Injection
from glastopf.virtualization.docker_client import DockerClient


class SQLinjectableEmulator(base_emulator.BaseEmulator):
    """Emulates a SQL injection vulnerability and a successful attack.
    This is an alternate approach to SQLiEmulator class.
    The SQL injection is executed by a real, sandboxed, attacker-owned database."""

    def __init__(self, data_dir):
        super(SQLinjectableEmulator, self).__init__(data_dir)

    def handle(self, attack_event, attackerdb_session, connection_string_data, work_dir = None):
        payload = "Payload generated from SQLinjectableEmulator"
        value = ""
        #attacker fingerprinting and insertion in attacker.db
        attacker = Attacker(str(attack_event.source_addr[0]))
        attacker = Attacker.insert_unique(attackerdb_session, attacker)
        
        docker_client = DockerClient()
        
        #get dataxx.db for attacker xx, make copy if not present yet
        if(work_dir == None):
            copy_connection_string = attacker.get_copy_conn(connection_string_data)
        else: copy_connection_string = attacker.get_copy_conn(connection_string_data, work_dir)
        copy = DB_copy(connection_string_data, copy_connection_string)
        copy.create_copy()
        datadb_session_copy = User.connect(copy_connection_string)
        #inject, form response
        injection = Injection(attack_event, datadb_session_copy)
        payload = injection.getResponse()
        attack_event.http_request.set_response(payload)
        #close db connections
        datadb_session_copy.close()


