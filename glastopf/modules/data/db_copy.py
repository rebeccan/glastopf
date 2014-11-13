# Copyright (C) 2014  Rebecca neigert
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
import os.path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from modules.data.user import User

Base = declarative_base()

class DB_copy(User):
    """
    Offers methods for copying the original database
    """
    connection_string_original = None
    
    def __init__(self, connection_string_original, connection_string_copy):
        if not DB_copy.connection_string_original:
            DB_copy.connection_string_original = str(connection_string_original)
        self.connection_string_copy = str(connection_string_copy)
    
    """make a copy of the original database"""
    def create_copy(self):
        #transform the connection string to a path string
        # e.g. src "sqlite:///db/data.db" to "/db/data.db"
        # e.g. dst "sqlite:///db/data123.db" to "/db/data123.db"
        src = str(DB_copy.connection_string_original).replace('sqlite:///', '')
        print 'cut src: ' + src
        dst = str(self.connection_string_copy).replace('sqlite:///', '')
        print 'cut dst: ' + dst
        if os.path.isfile(dst):
            print 'destination file ' + dst + ' already exists. No copy made!'
            return False
        shutil.copyfile(src, dst)
        return True
        
    
