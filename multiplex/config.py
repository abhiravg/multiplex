from configurator import Config
from configurator.node import ConfigNode


class DotListConfig(Config):
    def __init__(self, data=None, dotlist_sep='.'):
        if type(data) is ConfigNode or type(data) is DotListConfig:
            super().__init__(data=data.data)
        else:
            super().__init__(data=data)
        self.dotlist_sep = dotlist_sep

    def __getitem__(self, item):
        value = super()
        for part in item.split(self.dotlist_sep):
            value = value.__getitem__(part)
        return value

    def __add__(self, other):
        other = DotListConfig(other.data)
        new_conf = super().__add__(other)
        return DotListConfig(new_conf.data)

    def keys(self):
        return self._find_keys(self.data, '', [])

    def items(self):
        return ((k, self[k]) for k in self.keys())

    def _find_keys(self, d, key, keys):
        if isinstance(d, dict):
            for k in d:
                self._find_keys(d[k], key + self.dotlist_sep + k if key else k, keys)
        else:
            keys.append(key)
        return keys
