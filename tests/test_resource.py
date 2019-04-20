from unittest.mock import MagicMock

from marshmallow import Schema

import quaerere_base_client

resource_schema = MagicMock(Schema)
model_class = MagicMock()


class TestResource:
    class MockResource(quaerere_base_client.Resource):
        resource_schema = resource_schema
        model_class = model_class

    def test_instantiation(self):
        resource = self.MockResource()
        assert resource.schema_one == resource.schema_new
