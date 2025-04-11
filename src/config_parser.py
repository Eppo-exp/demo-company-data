from datetime import timedelta
from typing import Dict, Any, List, Optional

import yaml

from src.helpers import string_to_date, date_to_string


class ConfigParser:
    """
    Parser for experiment configuration files that handles date shifting and config processing.
    """

    def __init__(self, config: Dict[str, Any], start_date_override: Optional[str]) -> None:
        """
        Initialize the ConfigParser with a config dictionary and optional start date override.

        Args:
            config: Dictionary containing experiment configuration
            start_date_override: Optional date string to override experiment start dates
        """
        self.config = self._process_config(config, start_date_override)

    def _shift_dates(self, config: Dict[str, Any], start_date_override: str) -> Dict[str, Any]:
        """
        Shift all experiment dates based on a new start date.

        Args:
            config: Dictionary containing experiment configuration
            start_date_override: Date string to shift experiment dates to

        Returns:
            Config dictionary with shifted dates
        """
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

    def _process_config(self, config: Dict[str, Any], start_date_override: Optional[str]) -> Dict[str, Any]:
        """
        Process the configuration by applying any necessary transformations.

        Args:
            config: Dictionary containing experiment configuration
            start_date_override: Optional date string to override experiment start dates

        Returns:
            Processed config dictionary
        """
        processed_config = config
        if start_date_override is not None:
            processed_config = self._shift_dates(processed_config, start_date_override)
        return processed_config

    @classmethod
    def from_file(cls, filename: str, start_date_override: Optional[str] = None) -> 'ConfigParser':
        """
        Create a ConfigParser instance from a YAML file.

        Args:
            filename: Path to the YAML config file
            start_date_override: Optional date string to override experiment start dates

        Returns:
            ConfigParser instance initialized with the file contents
        """
        with open(filename, 'r') as file:
            config = yaml.safe_load(file)
            return cls(config, start_date_override)

    def _earliest_start_date(self) -> str:
        """
        Get the earliest start date among all experiments.

        Returns:
            Date string of the earliest experiment start date
        """
        experiments = self.config['assignments']['experiments']
        return min(e['start_date'] for e in experiments.values())

    @property
    def experiments(self) -> List[str]:
        """
        Get list of experiment keys.

        Returns:
            List of experiment identifier strings
        """
        return list(self.config['assignments']['experiments'].keys())

    @property
    def entity_name(self) -> str:
        """
        Get the entity name from the config.

        Returns:
            Entity name string
        """
        return self.config['assignments']['entity_name']

    @property
    def fact_entity(self) -> str:
        """
        Get the fact entity name, falling back to entity_name if not specified.

        Returns:
            Fact entity name string
        """
        if self.config['assignments'].get('subentity_name'):
            return self.config['assignments']['subentity_name']
        return self.config['assignments']['entity_name']
