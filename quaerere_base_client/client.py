__all__ = ['Client']

class Client:

    def __init__(self, url_base):
        self.url_base = url_base

    def add_api(self, api):
        api.update(self.url_base)
        setattr(self, api.version, api)
