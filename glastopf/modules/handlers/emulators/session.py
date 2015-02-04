# Copyright (C) 2015  Rebecca Neigert
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

from glastopf.modules.handlers import base_emulator
from Cookie import SimpleCookie
import threading
from datetime import datetime, timedelta


lock = threading.RLock()

#datastructure for storing cookies
#e.g. {1:{'cookie':SimpleCookie, 'logged_in': False}, 2:{'cookie':SimpleCookie, 'logged_in': 'Logged in as bla@emxample.com'}}
sessions = {}

#for sids
counter = 1

"""
Provides insecure session ids and non persistent session management.
Emulator should be used cascaded prior other Emulator to set cookie.
Insecure sessions, because sids are guessable vulnerable to session fixation, session stealth, etc...
"""
class SessionEmulator(base_emulator.BaseEmulator):
    
    def __init__(self, data_dir):
        super(SessionEmulator, self).__init__(data_dir)


    def handle(self, attack_event):
        global sessions
        global lock
        global counter
        
        invalid = False
        not_stored = False
        #check received cookie for existance in sessions and expiration
        received = str(attack_event.get_header_value('Cookie'))
        if received:
            received_cookie = SimpleCookie(received)
            print "got cookie from client: " + received_cookie.output()
            received_sid = received_cookie['sid'].value
            if(sessions.has_key(received_sid)):
                stored_cookie_dict = sessions[received_sid]
                stored_cookie = stored_cookie_dict['cookie']
                #check if cookie is expired
                if((stored_cookie is not None) and
                    (datetime.strptime(stored_cookie['sid']['expires'],'%a, %d %b %Y %H:%M:%S')
                    < datetime.now())):
                    invalid = True
            else: not_stored = True
        #create new cookie
        if not received or invalid or not_stored:
            cookie = SimpleCookie()
            with lock:
                #cookie creation
                cookie['sid'] = counter
                #cookie['sid']['path'] = '/login'
                #cookie['sid']['domain'] = '192.168.56.101'
                cookie['sid']['max-age'] = 1800 # seconds
                expires = datetime.now() + timedelta(minutes=30)
                cookie['sid']['expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S') # Wdy, DD-Mon-YY HH:MM:SS GMT
                #add cookie to sessions
                if invalid:
                    sessions[str(counter)] = {'cookie': cookie, 'logged_in': sessions[received_cookie['sid'].value]['logged_in']}
                else:
                    sessions[str(counter)] = {'cookie': cookie, 'logged_in': False}
                counter = counter + 1
            #add cookie to response headers
            cookie_str = cookie.output().replace('Set-Cookie: ', '')
            print "send cookie to client" + cookie_str
            attack_event.http_request.set_response(body ='', http_code=0, headers=(
                ('Set-Cookie', cookie_str),
            ))
        return attack_event
    
    
def is_valid(sid):
    return sessions[sid]['cookie']['expires'] < datetime.now()

def set_logged_in(sid, logged_in_msg):
    sessions[sid]['logged_in'] = logged_in_msg
    
def is_logged_in(sid):
    return sessions[sid]['logged_in'] is not False


