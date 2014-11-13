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

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Attacker(Base):
    """ Declarative mapping for an attacker.
    It represents characteristics of each attacker to distinguish them.
    """
    
    __tablename__ = 'attackers'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    ip = Column(String(50))
    #db_connection = Column(String(50))
    
    #create attacker with ip address
    def __init__(self,ip):
        #self.id = None
        self.ip = str(ip)
    
    def __repr__(self):
        return "<Attacker('%s')>" % (self.ip)
    
    """ returns the string of the path to the data-database copy owned by the attacker
    """    
    def get_copy_conn(self, connection_string_data = 'sqlite:///db/data.db'):
        if(self.id == None):
            print "Insert Attacker into table before calling get_copy_conn(). No copy made!"
            return None
        return connection_string_data.replace('.db', '') + str(self.id) + '.db'
    
    
    """ Connects to or creates the attacker database and its attacker table and gives back a session
    parameter: path of the SQLite DB with the attacker table, e.g. "sqlite:///db/attacker.db"
    """
    @staticmethod
    def connect(connection_string_attacker):
        engine = create_engine(connection_string_attacker)
        Base.metadata.create_all(engine)
        attackerdb_session = sessionmaker(bind=engine)()
        return attackerdb_session
    
    """ insert a new attacker, if not present yet.
    """
    @staticmethod
    def insert_unique(attackerdb_session, attacker):
        if Attacker.find_equal(attackerdb_session, attacker) != None :
            return False
        attackerdb_session.add(attacker)
        attackerdb_session.commit()
        return True
    
    """finds the attacker in attacker-database equal to attacker-param
    returns one or none"""
    @staticmethod
    def find_equal(attackerdb_session, attacker):
        attacker_list = attackerdb_session.query(Attacker).filter_by(ip=attacker.ip)
        if attacker_list.count() > 0:
            assert attacker_list.count() == 1
            return attacker_list[0]
        return None
    