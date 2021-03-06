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
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class Comment(Base):
    """ Declarative mapping for the user comment in the data.db
    The database data.db is used to be copied. The copies respond to unfiltered SQL injections.
    Should not contain real data, but honeytokens!
    """
    
    __tablename__ = 'comments'
    id = Column(Integer, Sequence('comment_id_seq'), primary_key=True)
    comment = Column(String(50))
    
    def __init__(self, comment):
        self.comment = str(comment)
    
    def __repr__(self):
        return "<Comment('%s')>" % (self.comment)
    
    @staticmethod
    def connect(connection_string):
        engine = create_engine(connection_string)
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        return session
    
    @staticmethod
    def injection(session, query):
        try:
            result = session.execute(query)
            return Comment.serialize_rows(result)
        except (SQLAlchemyError) as e:
            print "SQLAlchemyError: " + str(e)
            error = "error: " + str(e)
            return [error]
        except Exception as e:
            print "Any Exception: " + str(e)
            error = "error: any exception occured"
            return [error]
    
    @staticmethod
    def serialize_rows(rows):
        l = []
        try:
            for row in rows:
                l.append(repr(Comment.row2dict(row)))
        finally:
            return l
   

    @staticmethod
    def row2dict(row):
        d = {}
        d['id'] = str(row.id)
        d['comment'] = str(row.comment)
        return d