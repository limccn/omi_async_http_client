import sys

sys.path.append("../")
# to find top level mock_fastapi
sys.path.append("../../")

from omi_async_http_client import APIClient as OmiAPIClientBuilder

from fastapi.testclient import TestClient

from .mock_test_client_backend import MockTestClientBackend


def mock_rpc_api_client_builder(model,
                                http_backend=None,
                                resource_endpoint="/mock",
                                client_id="",
                                client_secret=""
                                ):
    if isinstance(http_backend, str):
        pass
    else:
        from mock_fastapi import app
        http_backend = MockTestClientBackend(TestClient(app))

    return OmiAPIClientBuilder(
        model=model,
        http_backend=http_backend,
        resource_endpoint=resource_endpoint,
        client_id=client_id,
        client_secret=client_secret,
    )


APIClient = mock_rpc_api_client_builder
