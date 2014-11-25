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


class Mappings(object):
    def __init__(self):
        file_dir = os.path.dirname(os.path.abspath(__file__))
        queries_file = os.path.join(file_dir, "queries.xml")
        tree = ElementTree.parse(queries_file)
        doc = tree.getroot()
        self.mapping_list = []
        self.tainted_vars = []
        for mapping in doc.findall('mapping'):
            database = mapping.find('database').text
            dorks = mapping.find('dorks').text
            tainted_variables = mapping.find('tainted_variables').text
            query = mapping.find('query').text
            response = mapping.find('response').text
            self.tainted_vars.append(tainted_variables)
            self.mapping_list.append(Mapping(database, dorks, tainted_variables, query, response))
    
    def find(self, tainted_variables, database = "sqlite", dorks = "default"):
        for mapping in mapping_list:
            cond1 = mapping.database == database
            cond2 = dorks in mapping.dorks
            cond3 = mapping.tainted_variables == tainted_variables
            if(cond1 and cond2 and cond3):
                return (mapping.query, mapping.response)
        return None
    
    """
    identifies and extracts user input from the request line
    (ignores non mapable user input)
    """
    @staticmethod
    def getTaintedVarsFromRequ(attack_event):
        #TODO RN: parse stuff from request body as well
        login = None
        password = None
        comment = None
        query_dictionary = attack_event.http_request.request_query
        if(query_dictionary.has_key('login')):
            login = str(query_dictionary.get('login')[0])
        if(query_dictionary.has_key('password')):
            password = str(query_dictionary.get('password')[0])
        if(query_dictionary.has_key('comment')):
            comment = str(query_dictionary.get('comment')[0])
        return (login, password, comment)
        
    
    """
    injects the query accordingly to the user input and forms the response
    """
    def getResponseForRequ(self, attack_event, datadb_session_copy):
        payload = "SQL Injectable Handler... <br></br>"
        (login, password, comment) = self.getTaintedVarsFromRequ(attack_event)
        
        #login stuff
        if(login is not None and password is not None):
            #query
            query = "SELECT * FROM users WHERE email = '" + login + "' AND password = '" + password + "'"
            injectionResult = User.injection(datadb_session_copy, query)
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
            injectionResult = Comment.injection(datadb_session_copy, query)
            #response
            payload = payload + "Comment inserted successfully."
            
        return payload
        

class Mapping(object):
    def __init__(self, database, dorks, tainted_variables, query, response):
        self.database = database
        self.dorks = dorks
        self.tainted_variables = tainted_variables
        self.query = query
        self.response = response
    
    
