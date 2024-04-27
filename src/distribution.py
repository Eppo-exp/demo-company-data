import numpy as np


class BaseDistribution:
    _required_parameters = None
    _draw_function = None

    def __init__(self, parameters):
        self.parameters = parameters
        self._validate_parameters()

    def _validate_parameters(self):
        is_valid = set(self.parameters.keys()) == set(self._required_parameters)
        message = (f"Required parameters for {type(self).__name__} are {', '.join(self._required_parameters)}, "
                   f"but got {', '.join(self.parameters.keys())}")
        assert is_valid, message

    def _get_distribution_parameters_from_config_inputs(self):
        raise NotImplementedError

    def draw(self):
        parameters = self._get_distribution_parameters_from_config_inputs()
        return self._draw_function(**parameters)


class PoissonDistribution(BaseDistribution):
    _required_parameters = ('rate',)
    _draw_function = np.random.poisson

    def _get_distribution_parameters_from_config_inputs(self):
        return {'lam': self.parameters['rate']}


class NormalDistribution(BaseDistribution):
    _required_parameters = ('average', 'standard_deviation')
    _draw_function = np.random.normal

    def _get_distribution_parameters_from_config_inputs(self):
        return {'loc': self.parameters['average'], 'scale': self.parameters['standard_deviation']}


class BernoulliDistribution(BaseDistribution):
    _required_parameters = ('rate',)
    _draw_function = np.random.binomial

    def _get_distribution_parameters_from_config_inputs(self):
        return {'n': 1, 'p': self.parameters['rate']}


class LogNormalDistribution(BaseDistribution):
    _required_parameters = ('average', 'standard_deviation')
    _draw_function = np.random.lognormal

    def _get_distribution_parameters_from_config_inputs(self):
        M2 = self.parameters['average'] ** 2
        S2 = self.parameters['standard_deviation'] ** 2

        # Calculate mu using the derived formula
        mu = np.log(M2 / np.sqrt(S2 + M2))

        # Calculate sigma using the derived formula
        sigma = np.sqrt(np.log(1 + S2 / M2))

        return {'mean': mu, 'sigma': sigma}


DISTRIBUTIONS = {
    'poisson': PoissonDistribution,
    'normal': NormalDistribution,
    'bernoulli': BernoulliDistribution,
    'lognormal': LogNormalDistribution
}
