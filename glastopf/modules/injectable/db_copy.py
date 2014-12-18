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

import shutil
import os.path
import os

"""
Offers methods for copying the original database
"""

class DB_copy(object):
    
    """
    db_copy_name is the name of the attacker-data db
    """
    def __init__(self, db_copy_name, db_orig_name = 'data.db', work_dir = 'db'):
        self.db_copy_name = db_copy_name
        self.db_orig_name = db_orig_name
        self.work_dir = work_dir
        
    
    """create a copy of the original database
    does not overwrite a file, if already there"""
    def create_copy(self):
        src = self.get_db_orig_path()
        print 'src: ' + src
        dst = self.get_db_copy_path()
        print 'dst: ' + dst
        if os.path.isfile(dst):
            print 'destination file ' + dst + ' already exists. No copy made!'
            return False
        shutil.copyfile(src, dst)
        return True
        
        
    """
    returns the path to the copy db file
    e.g. "/db/data123.db"
    """
    def get_db_copy_path(self):
        join = os.path.join(self.work_dir, self.db_copy_name)
        if(os.path.isabs(join)):
            return join
        else: return os.path.abspath(join)
    
    """
    returns the path to the original db file
    e.g. "/db/data.db"
    """
    def get_db_orig_path(self):
        join = os.path.join(self.work_dir, self.db_orig_name)
        if(os.path.isabs(join)):
            return join
        else: return os.path.abspath(join)
    
    """
    returns the sqlite connection string to the original db
    e.g. "sqlite:///db/data.db"
    """
    def get_db_orig_conn_str(self):
        if(os.path.isabs(self.work_dir)):
            return "sqlite:////" + self.get_db_orig_path()
        else:
            return "sqlite:///" + self.get_db_orig_path()
    
    """
    returns the sqlite connection string to the original db
    e.g. "sqlite:///db/data123.db"
    """
    def get_db_copy_conn_str(self):
        if(os.path.isabs(self.work_dir)):
            return "sqlite:////" + self.get_db_copy_path()
        else:
            return "sqlite:///" + self.get_db_copy_path()
    
    
