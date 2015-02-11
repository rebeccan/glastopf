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
    encoding = Column(String(200))
    lang = Column(String(200))
    agent = Column(String(200))
    
    #attacker with ip address and passive fingerprinting
    def __init__(self,ip ='', encoding='', lang='', agent=''):
        self.ip = str(ip)
        self.encoding = str(encoding) #'HTTP_ACCEPT_ENCODING': 'gzip, deflate'
        self.lang = str(lang) #'HTTP_ACCEPT_LANGUAGE': 'de,en-US;q=0.7,en;q=0.3'
        self.agent = str(agent) # 'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'
        
    
    def __repr__(self):
        return "<Attacker('%s')>" % (self.ip)
    
    #""" returns the string of the path to the data-database copy owned by the attacker
    #"""    
    #def get_copy_conn(self, connection_string_data = 'sqlite:///db/data.db', work_dir = None):
    #    if(self.id == None):
    #        print "Insert Attacker into table before calling get_copy_conn(). No copy made!"
    #        return None
    #    #use same folder as original
    #    if(work_dir == None):
    #        return connection_string_data.replace('.db', '') + str(self.id) + '.db'
    #    split = connection_string_data.split('/')
    #    return 'sqlite:///' + work_dir + '/' + split[-1].replace('.db', '') + str(self.id) + '.db'
    
    
    """ returns the name of the data-database copy owned by the attacker
    """    
    def get_db_name(self, original_name = 'data.db'):
        if(self.id == None):
            print "Insert Attacker into table before calling get_copy_conn(). No copy made!"
            return None
        return original_name.replace('.db', '') + str(self.id) + '.db'
    
    @staticmethod
    def extract_attacker(attack_event):
        ip = str(attack_event.source_addr[0])
        encoding = str(attack_event.get_header_value('Accept-Encoding'))
        lang = str(attack_event.get_header_value('Accept-Language'))
        agent = str(attack_event.get_header_value('User-Agent'))
        print "extract_attacker in Fingerprinting module:  encoding: " + encoding + "lang: " + lang + "agent: " + agent
        attacker = Attacker(ip = ip, encoding = encoding, lang = lang, agent = agent)
        return attacker
    
    
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
    Returns the attacker given as parameter, if it was inserted
    Returns the attacker from the database, if attacker was not inserted
    """
    @staticmethod
    def insert_unique(attackerdb_session, attacker):
        attacker_existent = Attacker.find_equal(attackerdb_session, attacker)
        if attacker_existent != None :
            return attacker_existent
        attackerdb_session.add(attacker)
        attackerdb_session.commit()
        return attacker
    
    
    """finds the attacker in attacker-database equal to attacker-param
    returns an attacker or none
    
    Equal when ip AND encoding AND lang AND agent are same
    ->
        - differentiation of different attackers in the same subnet
        - false differentiation of one user, using random IP headers
        - false differentiation of one TOR user, changing the exit node frequently 
    """
    @staticmethod
    def find_equal(attackerdb_session, attacker):
        attacker_list = attackerdb_session.query(Attacker).filter_by(ip = attacker.ip, encoding=attacker.encoding,
        lang = attacker.lang, agent = attacker.agent)
        if attacker_list.count() > 0:
            assert attacker_list.count() == 1
            return attacker_list[0]
        return None
    
    
    """
    Does all:
    Extracts the attacker from attack_event, inserts the attacker if not present yet,
    closes the connection and returns the db_name for the attacker
    """
    @staticmethod
    def fingerprint(attacker_connection_string, attack_event):
        #attacker fingerprinting and insertion in attacker.db
        attacker_session = Attacker.connect(attacker_connection_string)
        attacker = Attacker.extract_attacker(attack_event)
        attacker = Attacker.insert_unique(attacker_session, attacker)
        db_name = attacker.get_db_name()
        attacker_session.close()
        return db_name