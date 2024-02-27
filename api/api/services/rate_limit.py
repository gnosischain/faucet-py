from enum import Enum


class Strategy(Enum):
    ip = 'IP'
    address = 'ADDRESS'
    ip_and_address = 'IP_AND_ADDRESS'


class RateLimitStrategy:
    _strategies = set([Strategy.ip.value, Strategy.address.value, Strategy.ip_and_address.value])
    _strategy = None
    _default_strategy = Strategy.address.value

    @property
    def default_strategy(self):
        return self._default_strategy

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, value):
        if value not in self._strategies:
            raise ValueError('Invalid strategy value', value, 'Expected one of', self._strategies)
        self._strategy = value
