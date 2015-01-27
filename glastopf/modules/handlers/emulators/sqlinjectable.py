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
from glastopf.modules.handlers.emulators.surface.template_builder import TemplateBuilder
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
        injection = Injection(DockerClient(), attack_event, db_name)
        payload = injection.getResponse()
        
        base_template = TemplateBuilder(self.data_dir)
        login_template = TemplateBuilder(self.data_dir, base_template.read_template("templates/login_form.html"))
        login_template.add_string("login_msg", "Please fill in your credentials")
        base_template.add_template_builder("login_form", login_template)
        base_template.add_string("comments", "comments")
        response = base_template.get_substitution()
        
        attack_event.http_request.set_response(response)
        return attack_event


