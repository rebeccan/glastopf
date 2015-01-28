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


"""
The TemplateBuilder is a class for dynamic HTML page building.
TemplateBuilder helps with reading files and nesting.
It is mainly used by emulators. Read files are dork pages or html templates.

Why is this class needed?
Dork_pages are generated frequently, but are static, as soon as generated, if not modified.
Modification works through Template classes and the python method safe_substitute, that
substitues keywords beginning with the character $ with given text.
TemplateBuilder uses Templates and recursive safe_substitute to nest Templates.
"""
class TemplateBuilder(object):
    
    """
    Creates a TemplateBuilder with the given base_template.
    base_template: Has to be a Template, a path to a template (.e.g 'dork_pages/pagexy') or None.
    If None, the base_template is read from the first dork_page.
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
        if(not isinstance(self.base_template, Template)):
            self.base_template = self.read_template(self.base_template)
        
    """
    Reads a template file and returns a Template.
    template_path: The path of the template file.
    """
    def read_template(self, template_path):
        template_file = os.path.join(self.data_dir, template_path)
        if os.path.isfile(template_file):
            with codecs.open(template_file, "r", "utf-8") as template_txt:
                template = Template(template_txt.read())
        else:
            template = ''
        return template
    
    """
    Adds the substitution-pair to the children of the base_template.
    Reads the template file from the template_path and wraps it into a TemplateBuilder.
    substitue_name, e.g. 'login_form' for subsitution at $login_form
    template_path, e.g. 'templates/login_form.html'
    """
    def add_template(self, substitue_name, template_path):
        template = read_template(template_path)
        self.children[substitue_name] = TemplateBuilder(self.data_dir, template)
    
    """
    Adds the substitution-pair to the children of the base_template.
    Wraps the string substitute value into a Template and a TemplateBuilder.
    substitue_name, e.g. "login_msg"
    subsitute_value, e.g. "Please fill in your credentials"
    """
    def add_string(self, substitue_name, subsitute_value):
        self.children[substitue_name] = TemplateBuilder(self.data_dir, Template(subsitute_value))
    
    """
    Adds the substitution-pair to the children of the base_template,
    without wraping template_builder into a TemplateBuilder.
    """
    def add_template_builder(self, substitue_name, template_builder):
        self.children[substitue_name] = template_builder
       
    def has_children(self):
        if(len(self.children) < 1):
            return False
        return True
    
    def get_children(self):
        return self.children
    
    def get_base_template(self):
        return self.base_template


    """
    Performs recursive substitution for the base template and its children and their children...
    Returns the result string.
    """
    def get_substitution(self):
        d = {}
        for key in self.children:
            d[key] = self.children[key].get_substitution()
            print key
            print d[key]
        return self.base_template.safe_substitute(d)



