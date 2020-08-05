from omi_async_http_client import APIClient as OmiAPIClientBuilder


def mock_rpc_api_client_builder(model,
                                app=None,
                                http_backend="omi_async_http_client.fastapi_testclient_backend.FastAPITestClientBackend",
                                resource_endpoint="/mock",
                                client_id="client_id",
                                client_secret="client_secret"
                                ):
    return OmiAPIClientBuilder(
        model=model,
        app=app,
        http_backend=http_backend,
        resource_endpoint=resource_endpoint,
        client_id=client_id,
        client_secret=client_secret,
    )


APIClient = mock_rpc_api_client_builder
