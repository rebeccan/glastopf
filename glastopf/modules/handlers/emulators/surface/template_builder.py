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

import os
import codecs
from string import Template

class TemplateBuilder(object):
    
    """
    base_template_path, e.g. 'dork_pages/pagexy'
    """
    def __init__(self, data_dir, base_template = None):
        self.data_dir = data_dir
        self.children = {}
        self.base_template = base_template
        if(self.base_template is None):
            pages_dir = os.path.join(self.data_dir, 'dork_pages')
            dork_page_list = os.listdir(pages_dir)
            dork_page = dork_page_list[0]
            with codecs.open(os.path.join(pages_dir, dork_page), "r", "utf-8") as dork_page:
                self.base_template = Template(dork_page.read())
        
    def read_template(self, template_path):
        template_file = os.path.join(self.data_dir, template_path)
        if os.path.isfile(template_file):
            with codecs.open(template_file, "r", "utf-8") as template_txt:
                template = Template(template_txt.read())
        else:
            template = ''
        return template
    
    """
    substitue_name, e.g. 'login_form' for subsitution at $login_form
    template_path, e.g. 'templates/login_form.html'
    """
    def add_template(self, substitue_name, template_path):
        template = read_template(template_path)
        self.children[substitue_name] = TemplateBuilder(self.data_dir, template)
    
    """
    substitue_name, e.g. login_msg
    subsitute_value, e.g. "Please fill in your credentials"
    """
    def add_string(self, substitue_name, subsitute_value):
        self.children[substitue_name] = TemplateBuilder(self.data_dir, Template(subsitute_value))
        
    def add_template_builder(self, substitue_name, template_builder):
        self.children[substitue_name] = template_builder
       
    def has_children(self):
        if(len(self.template_children) < 1 and len(self.string_children) < 1):
            return False
        return True
    
    def get_children(self):
        return self.children
    
    def get_base_template(self):
        return self.base_template

    def get_substitution(self):
        d = {}
        for key in self.children:
            d[key] = self.children[key].get_substitution()
            print key
            print d[key]
        return self.base_template.safe_substitute(d)



