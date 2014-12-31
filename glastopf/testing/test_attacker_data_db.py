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

import unittest
import tempfile
import shutil
import os

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.fingerprinting.attacker import Attacker
from modules.injectable.db_copy import DB_copy
from modules.injectable.user import User


class TestAttackerDataDB(unittest.TestCase):
    
    #initialization
    def setUp(self):
        #setup a temp work directory with extra databases, so that existing DBs are not messed up by tests
        self.work_dir = tempfile.mkdtemp(dir=os.getcwd())
        self.attacker_connection_string = 'sqlite:///' + self.work_dir + '/attackerunittest.db'
        self.data_connection_string = 'sqlite:///' + self.work_dir + '/dataunittest.db'
        print self.attacker_connection_string
        print self.data_connection_string

    #cleanup
    def tearDown(self):
        # remove temp work dir
        if os.path.isdir(self.work_dir):
            shutil.rmtree(self.work_dir)
        return

    
    def test_createAttackers(self):
        attackerdb_sess = Attacker.connect(self.attacker_connection_string)
        #test if insertion works
        Attacker.insert_unique(attackerdb_sess, Attacker('127.0.0.1'))
        Attacker.insert_unique(attackerdb_sess, Attacker('192.168.32.1'))
        Attacker.insert_unique(attackerdb_sess, Attacker('192.168.32.1'))
        Attacker.insert_unique(attackerdb_sess, Attacker('192.168.32.2'))
        self.assertEqual(attackerdb_sess.query(Attacker).count(), 3)
        attackerdb_sess.close()
        
    def test_delAttackers(self):
        attackerdb_sess = Attacker.connect(self.attacker_connection_string)
        attacker =  Attacker('127.0.0.1')
        Attacker.insert_unique(attackerdb_sess, attacker)
        attackerdb_sess.delete(attacker)
        attackerdb_sess.commit()
        self.assertEqual(attackerdb_sess.query(Attacker).count(), 0)
        attackerdb_sess.close()
        

    def test_updateAttackers(self):
        attackerdb_sess = Attacker.connect(self.attacker_connection_string)
        attacker =  Attacker('127.0.0.1')
        Attacker.insert_unique(attackerdb_sess, attacker)
        attacker = Attacker.find_equal(attackerdb_sess, attacker)
        attacker.ip = u"136.144.27.1"
        attackerdb_sess.commit()
        self.assertEqual(Attacker.find_equal(attackerdb_sess, attacker).ip, "136.144.27.1")
        attackerdb_sess.close()

    def test_createUsersInOriginal(self):
        datadb_session = User.connect(self.data_connection_string)
        datadb_session.add(User('bla@example.com', 'bla'))
        datadb_session.add(User('blub@example.com', 'blub'))
        datadb_session.add(User('blob@example.com', 'blob'))
        datadb_session.commit()
        self.assertEqual(datadb_session.query(User).count(), 3)
        datadb_session.close()
        
    #TODO RN: Fix me
    #def test_createDbCopy(self):
    #    datadb_session = User.connect(self.data_connection_string)
    #    datadb_session.add(User('bla@example.com', 'bla'))
    #    datadb_session.commit()
    #    attackerdb_session = Attacker.connect(self.attacker_connection_string)
    #    attacker = Attacker('127.0.0.1')
    #    Attacker.insert_unique(attackerdb_session, attacker)
    #    copy_conn_string = attacker.get_copy_conn(connection_string_data = self.data_connection_string)
    #    print 'dst: ' + copy_conn_string
    #    copy = DB_copy(self.data_connection_string, copy_conn_string)
    #    copy.create_copy()
    #    datadb_session_copy = User.connect(copy_conn_string)
    #    datadb_session.close()
    #    attackerdb_session.close()
    #    datadb_session_copy.close()
    
    
    def test_userInjection(self):
        datadb_session = User.connect(self.data_connection_string)
        User.injection(datadb_session, "INSERT INTO users (email, password) VALUES ('hick@example.de', 'hack');")
        self.assertEqual(datadb_session.query(User)[0].email, "hick@example.de")
        datadb_session.close()
    
   
if __name__ == '__main__':
    unittest.main(verbosity=2)