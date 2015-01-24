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


from glastopf.modules.handlers import base_emulator
from glastopf.modules.fingerprinting.attacker import Attacker
from glastopf.modules.injectable.injection import Injection
from glastopf.modules.injectable.local_client import LocalClient
from glastopf.virtualization.docker_client import DockerClient

import os
from random import choice
import codecs
from urlparse import parse_qs
from string import Template

class SQLinjectableEmulator(base_emulator.BaseEmulator):
    """Emulates a SQL injection vulnerability and a successful attack.
    This is an alternate approach to SQLiEmulator class.
    The SQL injection is executed by a real, sandboxed, attacker-owned database."""

    def __init__(self, data_dir):
        super(SQLinjectableEmulator, self).__init__(data_dir)


    def handle(self, attack_event, attackerdb_session, connection_string_data):
        #attacker fingerprinting and insertion in attacker.db
        attacker = Attacker.extract_attacker(attack_event)
        attacker = Attacker.insert_unique(attackerdb_session, attacker)
        db_name = attacker.get_db_name()
        
        #inject, form response
        injection = Injection(LocalClient(), attack_event, db_name)
        payload = injection.getResponse()
        
        #attack_event.http_request.set_response(payload)
        
        pages_dir = os.path.join(self.data_dir, 'dork_pages')
        dork_page_list = os.listdir(pages_dir)
        dork_page = dork_page_list[0]
        with codecs.open(os.path.join(pages_dir, dork_page), "r", "utf-8") as dork_page:
            login_msg = payload
            template = Template(dork_page.read())
            response = template.safe_substitute(
                login_msg="")
            response2 = response.replace('Please fill in your credentials', payload)
        attack_event.http_request.set_response(response2)
        return attack_event


