__all__ = ['API']

class API:
    def __init__(self, version):
        self.base_url = None
        self.version = version
        self._resources = []

    def add_resource(self, resource_class):
        """

        :param resource_class:
        :type resource_class:
        :return:
        """
        resource = resource_class()
        setattr(self, resource.resource_name, resource)
        self._resources.append(resource)

    def update(self, base_url):
        self.base_url = base_url
        for resource in self._resources:
            resource.register(base_url + '/' + self.version)
