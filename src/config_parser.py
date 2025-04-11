from datetime import timedelta

import yaml

from src.helpers import string_to_date, date_to_string


class ConfigParser:
    def __init__(self, config, start_date_override):
        self.config = self._process_config(config, start_date_override)

    def _shift_dates(self, config, start_date_override):
        earliest_start_date = min(e['start_date'] for e in config['assignments']['experiments'].values())
        date_offset = (string_to_date(start_date_override) - string_to_date(earliest_start_date)).days
        for experiment_key in config['assignments']['experiments'].keys():
            initial_start_date = config['assignments']['experiments'][experiment_key]['start_date']
            new_start_date = string_to_date(initial_start_date) + timedelta(days=date_offset)
            config['assignments']['experiments'][experiment_key]['start_date'] = date_to_string(new_start_date)

            initial_end_date = config['assignments']['experiments'][experiment_key]['end_date']
            new_end_date = string_to_date(initial_end_date) + timedelta(days=date_offset)
            config['assignments']['experiments'][experiment_key]['end_date'] = date_to_string(new_end_date)

        return config

    def _process_config(self, config, start_date_override):
        processed_config = config
        processed_config = self._shift_dates(processed_config, start_date_override)
        return processed_config

    @classmethod
    def from_file(cls, filename, start_date_override=None):
        with open(filename, 'r') as file:
            config = yaml.safe_load(file)
            return cls(config, start_date_override)

    def _earliest_start_date(self):
        experiments = self.config['assignments']['experiments']
        return min(e['start_date'] for e in experiments.values())

    @property
    def experiments(self):
        return list(self.config['assignments']['experiments'].keys())

    @property
    def entity_name(self):
        return self.config['assignments']['entity_name']

    @property
    def fact_entity(self):
        if self.config['assignments'].get('subentity_name'):
            return self.config['assignments']['subentity_name']
        return self.config['assignments']['entity_name']
