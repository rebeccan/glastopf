
from string import Template
from glastopf.modules.handlers import base_emulator
from glastopf.modules.fingerprinting.attacker import Attacker
from glastopf.modules.injectable.injection import Injection
from glastopf.modules.injectable.local_client import LocalClient
from glastopf.virtualization.docker_client import DockerClient
from glastopf.modules.handlers.emulators.surface import create_surface
from glastopf.modules.handlers.emulators.surface.template_builder import TemplateBuilder



class CommentPoster(base_emulator.BaseEmulator):

    def __init__(self, data_dir):
        super(CommentPoster, self).__init__(data_dir)

    def handle(self, attack_event, attacker_connection_string, connection_string_data):
        
        surface_creator = create_surface.SurfaceCreator(self.data_dir)
        surface = surface_creator.get_index("Comments",
            "/comments", " ", "Footer Powered By", " ")
        template = TemplateBuilder(self.data_dir, Template(surface))
        
        #attacker fingerprinting and insertion in attacker.db
        db_name = Attacker.fingerprint(attacker_connection_string, attack_event)
        
        #inject, form response
        injection = Injection(self.data_dir, DockerClient(), attack_event, db_name)
        payload = injection.getResponse(template)
        
        attack_event.http_request.add_response(payload)
        return attack_event

