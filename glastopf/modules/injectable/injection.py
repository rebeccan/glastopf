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


from glastopf.modules.injectable.local_client import LocalClient
from glastopf.virtualization.docker_client import DockerClient

from glastopf.modules.handlers.emulators.surface.template_builder import TemplateBuilder

from glastopf.modules.handlers.emulators.session import set_logged_in, get_sid, is_logged_in, is_valid, get_logged_in

import sqlparse
from urlparse import parse_qs
from xml.etree import ElementTree
from time import sleep
import os
import cgi
import re

class Injection(object):
    
    def __init__(self, data_dir, client, attack_event, db_name):
        self.data_dir = data_dir
        self.client = client
        self.attack_event = attack_event
        self.db_name = db_name
        #variables for mapping tainted variables to database query
        self.login = None
        self.password = None
        self.comment = None

    """
    identifies and extracts user input from the request line
    (ignores non mapable user input)
    """
    def getTaintedVars(self):
        #TODO RN: parse form fields
        url_dict = parse_qs(self.attack_event.http_request.request_body)
        if ('login' in url_dict):
            self.login = url_dict['login'][0]
        if ('password' in url_dict):
            self.password = url_dict['password'][0]
        if ('comment' in url_dict):
            self.comment = self.html_escape(url_dict['comment'][0])
        
        #parse URL
        query_dictionary = self.attack_event.http_request.request_query
        if(query_dictionary.has_key('login')):
            self.login = str(query_dictionary.get('login')[0])
        if(query_dictionary.has_key('password')):
            self.password = str(query_dictionary.get('password')[0])
        if(query_dictionary.has_key('comment')):
            self.comment = self.html_escape(str(query_dictionary.get('comment')[0]))
            
        return (self.login, self.password, self.comment)
    
    
    def html_escape(self, comment):
        return cgi.escape(comment) 
    
    
    """
    injects the query accordingly to the user input and forms the response and embedds it into a template
    """
    def getResponse(self, base_template = None):
        reponse = ""
        if(base_template is None):
            base_template = TemplateBuilder(self.data_dir)
        
        (login, password, comment) = self.getTaintedVars()
        sid = get_sid(self.attack_event)
        
        #login stuff
        if(login is not None and password is not None):
            #query
            query = "SELECT * FROM users WHERE email = '" + login + "' AND password = '" + password + "'"
            self.check_and_emulate_sleep(query)
            injectionResult = self.split_and_execute(query, 'users')
            #response
            empty = True
            for row in injectionResult:
                empty = False
                success_msg = ""
                if(row.has_key('email')):
                    success_msg = "Logged in as " + str(row['email'])
                    #authenticate session
                    sid = get_sid(self.attack_event)
                    set_logged_in(sid, success_msg)
                elif(row.has_key('error')):
                    #db error -> set error response immediately
                    error_msg = self.char_unescape(row['error'])
                    self.attack_event.http_request.add_response(error_msg, http_code =400)
                    return ""
                base_template.add_string("login_form", success_msg)
            if(empty):
                #fancy response
                #login_template = TemplateBuilder(self.data_dir, "templates/login_form.html")
                #login_template.add_string("login_msg", "Wrong username or password.")
                #base_template.add_template_builder("login_form", login_template)
                #non fancy response for better sqlmap boolean-based blind differentiation
                return "Wrong username or password. Forgot credentials?"
        elif((login is None) != (password is None)):
            #non fancy response for better sqlmap boolean-based blind differentiation
            return "Wrong username or password. Forgot credentials?"
        elif(is_valid(sid) and is_logged_in(sid)):
            base_template.add_string("login_form", get_logged_in(sid))
        else:
            login_template = TemplateBuilder(self.data_dir, "templates/login_form.html")
            login_template.add_string("login_msg", "Please fill in your credentials")
            base_template.add_template_builder("login_form", login_template)
            
        #comment stuff
        #FIX RN: make comment section work
        if(comment is not None):
            #query
            query = "INSERT INTO comments (comment) VALUES ('" + comment + "')"
            self.check_and_emulate_sleep(query)
            injectionResult = self.split_and_execute(query, 'comments')
            #response: comment shows up, but insertion is blind, because no result is returned
        #retrieve comments
        query = "SELECT * from comments"
        self.check_and_emulate_sleep(query)
        injectionResult = self.split_and_execute(query, 'comments')
        commentsResponse = ""
        for item in injectionResult:
            commentsResponse = commentsResponse +  "<br/><br/>" + item['comment']
        base_template.add_string("comments", commentsResponse)
        #TODO RN: modify comments emulator?
        
        response = base_template.get_substitution()
        return response


    """
    For ERROR BASED attacks:
    unescape a string of the form "stringCHAR(97)+CHAR(98)+CHAR(99)string" to "stringabcstring"
    used to adapt to sqlmap error-based HTTP-response
    """
    def char_unescape(self, op_err_string):
        all_chars = re.findall('CHAR\(\d+\)', op_err_string)
        for char in all_chars:
            number = int(re.findall('\d+', char)[0])
            char_unescape = chr(number)
            op_err_string = op_err_string.replace(char, char_unescape)
        op_err_string = op_err_string.replace('+', '')
        return op_err_string
        
    """
    For TIME BASED attacks:
    emulates sleep if found in query
    """
    def check_and_emulate_sleep(self, query):
        sleep_cmd = re.findall('sleep\(\d+\)', query.lower())
        print query
        print sleep_cmd
        if(len(sleep_cmd) > 0):
            seconds = int(re.findall(r'\d+', sleep_cmd[0])[0])
            sleep(seconds)
            return True
        return False
    
    
    """
    For STACKED QUERY attacks:
    splits and executes statements
    returns the result from the first stmt
    """
    def split_and_execute(self, statements, table =''):
        queries = sqlparse.split(statements)
        injectionResults = []
        for query in queries:
            injectionResults.append(self.client.manage_injection(self.db_name, table, query))
        return injectionResults[0]
        

    def emulate_sqlite_blobs(self):
        pass

