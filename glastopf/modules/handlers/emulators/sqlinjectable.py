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
from glastopf.modules.attacker.attacker import Attacker
from glastopf.modules.injectable.db_copy import DB_copy
from glastopf.modules.injectable.user import User


class SQLinjectableEmulator(base_emulator.BaseEmulator):
    """Emulates a SQL injection vulnerability and a successful attack.
    This is an alternate approach to SQLiEmulator class.
    The SQL injection is executed by a real, sandboxed, attacker-owned database."""

    def __init__(self, data_dir):
        super(SQLinjectableEmulator, self).__init__(data_dir)

    def handle(self, attack_event, attackerdb_session, connection_string_data):
        payload = "Payload generated from SQLinjectableEmulator"
        value = ""
        #attacker fingerprinting and insertion in attacker.db
        attacker = Attacker(str(attack_event.source_addr[0]))
        attacker = Attacker.insert_unique(attackerdb_session, attacker)
        #get dataxx.db for attacker xx, make copy if not present yet
        copy_conn_string = attacker.get_copy_conn(connection_string_data)
        copy = DB_copy('sqlite:///db/data.db', copy_conn_string)
        copy.create_copy()
        datadb_session_copy = User.connect(copy_conn_string)
        #identify and extract all user input
        #make query with user input
        login = ""
        password = ""
        comment = ""
        query_dictionary = attack_event.http_request.request_query
        if(query_dictionary.has_key('login')):
            login = str(query_dictionary.get('login')[0])
        if(query_dictionary.has_key('password')):
            password = str(query_dictionary.get('password')[0])
        query = "SELECT * FROM users WHERE email = '" + login + "' AND password = '" + password + "'"
        injectionResult = User.injection(datadb_session_copy, query)
        for row in injectionResult:
            payload = payload + str(row['email'])
            payload = payload + str(row['password'])
        #form response with response from DB
        #attack_event.http_request.set_raw_response(payload)
        attack_event.http_request.set_response(payload)
        #close db connections
        #attackerdb_session.close() # <-- TODO: when to close this?
        datadb_session_copy.close()


