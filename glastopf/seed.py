# Copyright (C) 2015  Rebecca Neigert
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

import os

from modules.injectable.user import User
from modules.injectable.comment import Comment
from sqlalchemy import create_engine

"""
sets up the data database, if not present yet.
"""
def seed(connection_string_data):
    #TODO RN: more rows, filled with honeytokens
    path_to_sqlitefile = str(connection_string_data).replace('sqlite:///', '')
    if not os.path.isfile(path_to_sqlitefile):
        print "Setting up data database with path: " + path_to_sqlitefile
        sqla_engine = create_engine(connection_string_data)
        datadb_session = User.connect(connection_string_data)
        
        #--------------add users----------------------------
        datadb_session.add(User('blub@example.com', 'blub'))
        datadb_session.add(User('bla@example.com', 'bla'))
        
        for i in range(0,1000):
            datadb_session.add(User(str(i) + '@example.com', str(i)))
        
        Comment.connect(connection_string_data)
        #--------------add comments-------------------------
        datadb_session.add(Comment('This is a comment.'))
        datadb_session.add(Comment('Another comment.'))
        
        datadb_session.commit()
        datadb_session.close()
        return True
    return False