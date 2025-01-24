import numpy as np


class BaseDistribution:
    _required_parameters = None

    def __init__(self, parameters):
        self.parameters = parameters
        self._validate_parameters()

    @staticmethod
    def _draw_function(parameters):
        raise NotImplementedError

    def _validate_parameters(self):
        if self._required_parameters is not None:
            is_valid = set(self.parameters.keys()) == set(self._required_parameters)
            message = (f"Required parameters for {type(self).__name__} are {', '.join(self._required_parameters)}, "
                       f"but got {', '.join(self.parameters.keys())}")
            assert is_valid, message

    def _get_distribution_parameters_from_config_inputs(self):
        raise NotImplementedError

    def draw(self):
        parameters = self._get_distribution_parameters_from_config_inputs()
        return self._draw_function(parameters)


class PoissonDistribution(BaseDistribution):
    _required_parameters = ('rate',)

    @staticmethod
    def _draw_function(parameters):
        return np.random.poisson(**parameters)

    def _get_distribution_parameters_from_config_inputs(self):
        return {'lam': self.parameters['rate']}


class ConstantDistribution(BaseDistribution):
    _required_parameters = ('value',)

    @staticmethod
    def _draw_function(parameters):
        return parameters['value']

    def _get_distribution_parameters_from_config_inputs(self):
        return {'value': self.parameters['value']}


class NormalDistribution(BaseDistribution):
    _required_parameters = ('average', 'standard_deviation')

    @staticmethod
    def _draw_function(parameters):
        return np.random.normal(**parameters)

    def _get_distribution_parameters_from_config_inputs(self):
        return {'loc': self.parameters['average'], 'scale': self.parameters['standard_deviation']}


class BernoulliDistribution(BaseDistribution):
    _required_parameters = ('rate',)

    @staticmethod
    def _draw_function(parameters):
        return np.random.binomial(**parameters)

    def _get_distribution_parameters_from_config_inputs(self):
        return {'n': 1, 'p': self.parameters['rate']}


class LogNormalDistribution(BaseDistribution):
    _required_parameters = ('average', 'standard_deviation')

    @staticmethod
    def _draw_function(parameters):
        return np.random.lognormal(**parameters)

    def _get_distribution_parameters_from_config_inputs(self):
        M2 = self.parameters['average'] ** 2
        S2 = self.parameters['standard_deviation'] ** 2

        # Calculate mu using the derived formula
        mu = np.log(M2 / np.sqrt(S2 + M2))

        # Calculate sigma using the derived formula
        sigma = np.sqrt(np.log(1 + S2 / M2))

        return {'mean': mu, 'sigma': sigma}


class CategoricalDistribution(BaseDistribution):
    @staticmethod
    def _draw_function(parameters):
        categories = list(parameters.keys())
        probabilities = np.array([parameters[cat] for cat in categories])
        
        # Normalize probabilities across categories
        normalized_probs = probabilities / np.sum(probabilities, axis=0)
        
        # Draw samples using normalized probabilities
        n_samples = len(probabilities[0])
        results = np.array([np.random.choice(categories, p=normalized_probs[:,i]) 
                          for i in range(n_samples)])
        return results

    def _get_distribution_parameters_from_config_inputs(self):
        return self.parameters


DISTRIBUTIONS = {
    'poisson': PoissonDistribution,
    'normal': NormalDistribution,
    'bernoulli': BernoulliDistribution,
    'lognormal': LogNormalDistribution,
    'constant': ConstantDistribution,
    'categorical': CategoricalDistribution
}
