__all__ = ['Resource']

import re

import requests

from .exceptions import APIStatusException

_class_pattern = r'^(([A-Z][a-z]+)+)Schema$'
_name_pattern = r'([A-Z][a-z]+)'
_class_regex = re.compile(_class_pattern)
_name_regex = re.compile(_name_pattern)

_default_good = [200, 201, ]


class Resource:
    resource_schema = None
    schema_new = None
    base_url = None
    model_class = None

    def __init__(self):
        if self.resource_schema is None:
            raise NotImplementedError('resource_schema must be defined.')
        self._resource_name = None
        self._url_part = None
        self.schema_one = self.resource_schema(self.model_class)
        self.schema_many = self.resource_schema(self.model_class, many=True)
        if self.schema_new is None:
            self.schema_new = self.schema_one

    @property
    def resource_name(self):
        if self._resource_name is None:
            name_match = _class_regex.fullmatch(self.resource_schema.__name__)
            if name_match is None:
                raise RuntimeError('class name "{}" does not match naming '
                                   'requirements'.format(
                    self.resource_schema.__name__))
            self._resource_name = '_'.join(_name_regex.findall(
                name_match.group(1))).lower()

        return self._resource_name

    @property
    def url_part(self):
        if self._url_part is None:
            self._url_part = self.resource_name.replace('_', '-')

        return self._url_part

    def register(self, base_url):
        if self.base_url is None:
            self.base_url = base_url

    def request(self, method, url_part, good_status=None, json=None):
        url = self.base_url + '/' + url_part
        if good_status is None:
            good_status = _default_good
        resp = requests.request(method, url, json=json)
        if resp.status_code not in good_status:
            raise APIStatusException('Unexpected status_code {} from '
                                     'url {}'.format(resp.status_code, url))

        return resp.json()

    def all(self):
        raw = self.request('GET', self.url_part + '/', [200])
        unmarshal = self.schema_many.load(raw)
        return unmarshal.data

    def get(self, id):
        raw = self.request('GET', self.url_part + f'/{id}', [200])
        unmarshal = self.schema_one.load(raw)
        return unmarshal.data

    def create(self, data):
        new_data = self.schema_one.dump(data)
        raw = self.request('POST', self.url_part + '/', [201], json=new_data)
        unmarshal = self.schema_new.load(raw)
        return unmarshal.data
