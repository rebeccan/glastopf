# Copyright (C) 2013  Rebecca Neigert
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
from glastopf.modules.injectable.comment import Comment

from xml.etree import ElementTree
import os


class Injection(object):
    
    def __init__(self, attack_event, datadb_session_copy):
        self.attack_event = attack_event
        self.session = datadb_session_copy
        #variables for mapping tainted variables to database query
        self.login = None
        self.password = None
        self.comment = None

    """
    identifies and extracts user input from the request line
    (ignores non mapable user input)
    """
    def getTaintedVars(self):
        #TODO RN: parse stuff from request body as well
        query_dictionary = self.attack_event.http_request.request_query
        if(query_dictionary.has_key('login')):
            self.login = str(query_dictionary.get('login')[0])
        if(query_dictionary.has_key('password')):
            self.password = str(query_dictionary.get('password')[0])
        if(query_dictionary.has_key('comment')):
            self.comment = str(query_dictionary.get('comment')[0])
        return (self.login, self.password, self.comment)
        
    
    """
    injects the query accordingly to the user input and forms the response
    """
    def getResponse(self):
        #TODO RN: remove "SQL Injectable Handler... <br></br>" from payload
        payload = "SQL Injectable Handler... <br></br>"
        (login, password, comment) = self.getTaintedVars()
        
        #login stuff
        if(login is not None and password is not None):
            #query
            query = "SELECT * FROM users WHERE email = '" + login + "' AND password = '" + password + "'"
            injectionResult = User.injection(self.session, query)
            #response
            empty = True
            for row in injectionResult:
                empty = False
                payload = payload + "Logged in successfully as " + str(row['email'])
            if(empty):
                payload = payload + "Wrong username or password."
        if((login is None) != (password is None)):
            #response
            payload = payload + "Wrong username or password."
            
        #comment stuff
        if(comment is not None):
            #query
            query = "INSERT INTO comments (comment) VALUES ('" + comment + "');"
            injectionResult = Comment.injection(self.session, query)
            #response
            payload = payload + "Comment inserted successfully."
            
        return payload
