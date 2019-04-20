__all__ = ['ModelBase']

from marshmallow.fields import Field


class ModelBase:
    def __init__(self):
        self._fields = {}
        for attr_str in dir(self):
            attr = getattr(self, attr_str)
            if issubclass(attr.__class__, Field):
                self._fields[attr_str] = attr
                setattr(self, attr_str, attr.default)
