import yaml


class ConfigParser:
    def __init__(self, config):
        self.config = config

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as file:
            config = yaml.safe_load(file)
            return cls(config)

    @property
    def fact_entity(self):
        if self.config['assignments'].get('subentity_name'):
            return self.config['assignments']['subentity_name']
        return self.config['assignments']['entity_name']
