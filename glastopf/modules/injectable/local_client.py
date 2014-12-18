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

from glastopf.modules.injectable.user import User
from glastopf.modules.injectable.db_copy import DB_copy

import ast

class LocalClient(object):
    
    def __init__(self):
        return
    
    def manage_injection(self, db_name, query = ""):
        #create copy
        copy = DB_copy(db_name)
        copy.create_copy()
        #create session
        conn_str = copy.get_db_copy_conn_str()
        session = User.connect(conn_str)
        #make injection
        injectionResult = User.injection(session, query)
        session.close()
        rows = []
        for row in injectionResult:
            rows.append(LocalClient.deserialze_row(row))
        return rows
    
    
    @staticmethod
    def deserialze_row(row):
        d = ast.literal_eval(row)
        return d
