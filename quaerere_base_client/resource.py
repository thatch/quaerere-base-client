__all__ = ['Resource']

import re

import requests

from .exceptions import APIStatusException

_default_good = [200, 201, ]


class Resource:
    """Class for defining a REST resource

    """
    resource_schema = None
    schema_new = None
    base_url = None
    model_class = None
    accessor_name = None
    name_suffix = 'Schema'

    def __init__(self):
        if self.resource_schema is None:
            raise NotImplementedError('resource_schema must be defined.')
        if self.accessor_name is not None:
            self._resource_name = self.accessor_name
        else:
            self._resource_name = None
        self._url_part = None
        self.schema_one = self.resource_schema(self.model_class)
        self.schema_many = self.resource_schema(self.model_class, many=True)
        if self.schema_new is None:
            self.schema_new = self.schema_one

    @property
    def resource_name(self):
        """Name used for referencing this resource

        Uses a regex to construct the name based on
        :py:const:`_class_pattern`

        :return: resource name
        :rtype: str
        """
        if self._resource_name is None:
            name = self.resource_schema.__name__
            if name.endswith(self.name_suffix):
                name = name[:-len(self.name_suffix)]
            first_cap_re = re.compile('(.)([A-Z][a-z]+)')
            all_cap_re = re.compile('([a-z0-9])([A-Z])')
            s1 = first_cap_re.sub(r'\1_\2', name)
            self._resource_name = all_cap_re.sub(r'\1_\2', s1).lower()

        return self._resource_name

    @property
    def url_part(self):
        if self._url_part is None:
            self._url_part = self.resource_name.replace('_', '-') + '/'

        return self._url_part

    def register(self, base_url):
        """Register the base URL for the resource object

        :param base_url: Base URL for the webapp
        :type base_url: str
        :return:
        """
        if self.base_url is None:
            self.base_url = base_url

    def _request(self, method, url_part,
                 good_status=None, json=None, params=None):
        url = self.base_url + '/' + url_part
        if good_status is None:
            good_status = _default_good
        resp = requests.request(method, url, json=json, params=params)
        if resp.status_code not in good_status:
            raise APIStatusException('Unexpected status_code {} from '
                                     'url {}'.format(resp.status_code, url))

        return resp.json()

    def all(self):
        """Get all objects of resource type

        :return: resource objects
        :rtype: list
        """
        raw = self._request('GET', self.url_part, [200])
        unmarshal = self.schema_many.load(raw)
        return unmarshal.data

    def get(self, id):
        """Get resource object by id

        :param id: Identifier of an object
        :return: resource object
        :rtype: dict
        """
        raw = self._request('GET', self.url_part + f'{id}', [200])
        unmarshal = self.schema_one.load(raw)
        return unmarshal.data

    def create(self, data):
        """Create a resource object

        :param data: Initialization data
        :type data: dict
        :return: Creation metadata
        """
        new_data = self.schema_one.dump(data)
        raw = self._request('POST', self.url_part, [201], json=new_data)
        unmarshal = self.schema_new.load(raw)
        return unmarshal.data

    def replace(self, id, data):
        """Replace all data on resource object

        :param id: Identifier of an object
        :param data: Data to replace on object
        :return:
        """
        new_data = self.schema_one.dump(data)
        raw = self._request('PUT', self.url_part + f'{id}', [201],
                            json=new_data)
        unmarshal = self.schema_new.load(raw)
        return unmarshal.data

    def update(self, id, data):
        """Update data on resource object

        :param id: Identifier of an object
        :param data: Data to update object with
        :return:
        """
        new_data = self.schema_one.dump(data)
        raw = self._request('PATCH', self.url_part + f'{id}', [201],
                            json=new_data)
        unmarshal = self.schema_new.load(raw)
        return unmarshal.data

    def delete(self, id):
        """Delete resource object

        :param id: Identifier of an object
        :return:
        """
        raw = self._request('DELETE', self.url_part + f'{id}', [202])
        unmarshal = self.schema_one.load(raw)
        return unmarshal.data

    def find(self, conditions, variables, _or=False, sort=None, limit=None):
        """Simple query interface

        :param conditions: List of conditions to search for
        :type conditions: list
        :param variables: Variables to bind in conditions
        :param _or: 'or' the conditions instead of 'and'
        :type _or: bool
        :param sort: Optional return sort
        :param limit: Optional limit of returned objects
        :return: Object matching criteria
        :rtype: dict
        """
        params = []
        for condition in conditions:
            params.append(('condition', condition))
        for k, v in variables.items():
            params.append((k, v))
        if _or is not False:
            params.append(('_or', True))
        if sort is not None:
            params.append(('sort', sort))
        if limit is not None:
            params.append(('limit', limit))
        raw = self._request('GET', self.url_part + 'find/', params=params)
        # TODO: Create/use query schema and load entire payload
        unmarshal = self.schema_many.load(raw['result'])
        return unmarshal.data
