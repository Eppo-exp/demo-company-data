import os
from typing import Optional, Dict, Any, List

import requests


class EppoAPIHelper:
    def __init__(self, base_url: str = "https://eppo.cloud/api/v1", limit: int = 10):
        """
        Initialize the Eppo API client.
        
        Args:
            base_url (str): Base URL for the API
            limit (int): Number of results per page for paginated requests (defaults to 10)
        """
        self.base_url = base_url
        self.limit = limit
        self.headers = {
            'accept': 'application/json',
            'X-Eppo-Token': os.environ['EPPO_API_KEY']
        }

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Make a request to the Eppo API.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters
            json (dict, optional): JSON body for the request
            
        Returns:
            dict: JSON response from the API
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=json
        )
        response.raise_for_status()
        return response.json()

    def _get_entity_id_by_name(self, entity_name: str) -> str:
        """
        Get the ID of an entity by its name.
        
        Args:
            entity_name (str): Name of the entity to look up
            
        Returns:
            str: ID of the entity
            
        Raises:
            ValueError: If no entity with the given name exists
        """
        entities = self._make_request('GET', 'definitions/entities')
        for entity in entities:
            if entity['name'] == entity_name:
                return entity['id']

        raise ValueError(f"No entity with name '{entity_name}'")

    def _make_paginated_requests(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Make paginated requests to an API endpoint.
        
        Args:
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters
            
        Returns:
            list: Combined results from all pages
        """
        if params is None:
            params = {}

        all_results = []
        offset = 0

        while True:
            params['offset'] = offset
            params['limit'] = self.limit

            response = self._make_request('GET', endpoint, params=params)

            all_results.extend(response)

            # Check if we've reached the end
            if len(response) < self.limit:
                break

            offset += self.limit

        return all_results

    def delete_experiment(self, experiment_id: str) -> Dict:
        """
        Delete an experiment.
        
        Args:
            experiment_id (str): ID of the experiment to delete
            
        Returns:
            dict: Response from the API
        """
        return self._make_request('DELETE', f'/experiments/{experiment_id}')

    def get_experiment_by_name(self, experiment_name: str, entity_name: str) -> Dict:
        """
        Get an experiment by its name.
        
        Args:
            experiment_name (str): Name of the experiment to find
            entity_name (str): Name of the entity the experiment belongs to
            
        Returns:
            dict: Experiment data
            
        Raises:
            ValueError: If no experiment with the given name exists
        """
        for experiment in self.get_all_experiments(entity_name):
            if experiment['name'] == experiment_name:
                return experiment

        raise ValueError(f"No experiment with name '{experiment_name}'")

    def trigger_refresh(self, experiment_id: str, full_refresh: bool = True) -> Dict:
        """
        Trigger a refresh of experiment results.
        
        Args:
            experiment_id (str): ID of the experiment to refresh
            full_refresh (bool): Whether to perform a full refresh (defaults to True)
            
        Returns:
            dict: Response from the API
        """
        params = {
            'full_refresh': str(full_refresh).lower()
        }
        return self._make_request('POST', f'/experiment-results/update/{experiment_id}/', params=params)

    def update_experiment(self, experiment_id: str, payload: Dict) -> Dict:
        """
        Update an experiment with the given payload.
        
        Args:
            experiment_id (str): ID of the experiment to update
            payload (dict): JSON payload containing experiment updates
            
        Returns:
            dict: Updated experiment data
        """
        return self._make_request('PUT', f'/experiments/{experiment_id}', json=payload)

    def get_all_experiments(self, entity_name: str) -> List[Dict]:
        """
        Get all experiments for a given entity.
        
        Args:
            entity_name (str): Name of the entity to get experiments for
            
        Returns:
            list: List of all experiments for the entity
        """
        params = {
            'entity_id': self._get_entity_id_by_name(entity_name)
        }
        return self._make_paginated_requests('experiments', params=params)

    def get_experiment_names(self, entity_name: str) -> List[str]:
        """
        Get names of all experiments for a given entity.
        
        Args:
            entity_name (str): Name of the entity to get experiment names for
            
        Returns:
            list: List of experiment names
        """
        experiments = self.get_all_experiments(entity_name)
        return [experiment['name'] for experiment in experiments]
