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

class User(Base):
    """ Declarative mapping for the user table in the data.db
    The database data.db is used to be copied. The copies respond to unfiltered SQL injections.
    Should not contain real data, but honeytokens!
    """
    
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    email = Column(String(50))
    password = Column(String(50))
    
    def __init__(self, email, password):
        self.email = str(email)
        self.password = str(password)
        
    
    def __repr__(self):
        return "<User('%s')('%s')>" % (self.email, self.password)
    
    @staticmethod
    def connect(connection_string):
        engine = create_engine(connection_string)
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        return session
    
    @staticmethod
    def injection(session, query):
        result = session.execute(query)
        return result
    
    