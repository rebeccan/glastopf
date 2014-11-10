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

import uuid
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Attacker(Base):
    
    __tablename__ = 'attackers'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    ip = Column(String(50))
    #db_connection = Column(String(50))
    
    #create attacker with ip address, data-connection
    def __init__(self,ip):
        #self.id = None
        self.ip = str(ip)
    
    def __repr__(self):
        return "<Attacker('%s')>" % (self.ip)
    
    #an attacker is the same individual, when his ip address is the same
    #TODO: other fingerprinting techniques than the ip adress
    def __eq__(self, other):
        return self.ip == other.ip
        
    def get_db_conn(self):
        return 'sqlite:///db/data.db' + self.id
    
    def __ne__(self, other):
        return self.ip != other.ip
    
    
    @staticmethod
    def connect(connection_string_attacker):
        engine = create_engine(connection_string_attacker)
        Base.metadata.create_all(engine)
        attackerdb_session = sessionmaker(bind=engine)()
        return attackerdb_session
    
    @staticmethod
    def insert_unique(attackerdb_session, attacker):
        attacker_list = attackerdb_session.query(Attacker).filter_by(ip=attacker.ip)
        if attacker_list.count() > 0:
            return False
        attackerdb_session.add(attacker)
        attackerdb_session.commit()
        return True
    
    