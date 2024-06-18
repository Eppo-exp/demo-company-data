import numpy as np

from src.distribution import DISTRIBUTIONS


class EffectCalculator:
    def __init__(self, df, effects):
        self.df = df
        self.effects = effects

    def _evaluate_one_effect(self, effect):
        raise NotImplementedError

    def get_effects(self):
        effects = np.zeros(len(self.df))
        for effect in self.effects:
            effects += self._evaluate_one_effect(effect)

        return effects


class ConditionalEffectCalculator(EffectCalculator):
    def _evaluate_one_effect(self, conditional_effect):
        # Initially assume everyone is included, exclude them if they fail to meet a condition
        included = np.ones(len(self.df), dtype=bool)
        for condition in conditional_effect['conditions']:
            included &= (self.df[condition['column']] == condition['value']).values
        try:
            return conditional_effect['effect'] * included
        except:
            pass


class RandomEffectCalculator(EffectCalculator):
    def _evaluate_one_effect(self, effect):
        unique_values = self.df[effect['column']].unique()
        parameters = {
            key: np.ones(len(unique_values)) * value['baseline_value']
            for key, value in effect['parameters'].items()
        }
        random_effects = DISTRIBUTIONS[effect['type']](parameters).draw()
        mapping_dict = {value: effect for value, effect in zip(unique_values, random_effects)}

        return self.df[effect['column']].map(mapping_dict).values
