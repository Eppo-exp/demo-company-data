from datetime import datetime

from src.helpers import date_to_string


class AnalysisSync:
    def __init__(self, config_parser, api_helper):
        self.config_parser = config_parser
        self.api_helper = api_helper
        self.experiment_payloads = None

    def _update_payload(self, experiment_config, experiment_payload):
        experiment_payload['assignments_start_date'] = experiment_config['start_date']
        experiment_payload['events_start_date'] = experiment_config['start_date']
        experiment_payload['assignments_end_date'] = experiment_config['end_date']
        experiment_payload['events_end_date'] = experiment_config['end_date']

        if experiment_payload['status'] == 'COMPLETED':
            experiment_payload['concluded_date'] = min(experiment_config['end_date'],
                                                       date_to_string(datetime.today()))

        experiment_payload['analysis_plan']['confidence_interval_method'] = 'SequentialFixedHybrid'
        experiment_payload['analysis_plan']['confidence_level'] = 0.9

        return experiment_payload

    def sync_one_experiment(self, experiment_config, experiment_payload):
        new_experiment_payload = self._update_payload(experiment_config, experiment_payload)
        self.api_helper.update_experiment(new_experiment_payload['id'], new_experiment_payload)
        self.api_helper.trigger_refresh(new_experiment_payload['id'])

    def sync_experiments(self):
        self.experiment_payloads = self.api_helper.get_all_experiments(self.config_parser.entity_name)
        for experiment_key, experiment_config in self.config_parser.config['assignments']['experiments'].items():
            for experiment_payload in self.experiment_payloads:
                if experiment_payload.get('experiment_key') == experiment_key:
                    self.sync_one_experiment(experiment_config, experiment_payload)
                    print(f"Synced experiment {experiment_payload['name']}")
