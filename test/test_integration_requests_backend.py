"""
Copyright 2020 limc.cn All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import sys
import os
from typing import Optional

import pytest
from pydantic import BaseModel

sys.path.append("../")

from omi_async_http_client.async_http_client import APIClient
from omi_async_http_client._model import RequestModel
from omi_async_http_client._exceptions import HTTPException
from omi_async_http_client._status_code import status_codes

from omi_async_http_client.requests_backend import RequestsClientBackend

# =======================================
# install nest_asyncio for unit test when
# RuntimeError: This event loop is already running
# pip install nest_asyncio
# import nest_asyncio
# nest_asyncio.apply()
# =======================================


@RequestModel(api_name="/resources", api_prefix="/mock", api_suffix="")
class Resource(BaseModel):
    name: Optional[str]
    description: Optional[str]

@RequestModel(api_name="/resources/{id}", api_prefix="/mock", api_suffix="")
class ResourceID(Resource):
    id: Optional[str]

httpclient = APIClient(model=Resource,
            app=None,
            http_backend="omi_async_http_client.requests_backend.RequestsClientBackend",
            client_id="client_id",
            client_secret="client_secret",
            resource_endpoint="http://localhost:8003") 

httpclientid = APIClient(model=ResourceID,
            app=None,
            http_backend="omi_async_http_client.requests_backend.RequestsClientBackend",
            client_id="client_id",
            client_secret="client_secret",
            resource_endpoint="http://localhost:8003") 

@pytest.fixture(scope='function')
def setup_function(request):
    def teardown_function():
        print("teardown_function called.")

    request.addfinalizer(teardown_function)
    print('setup_function called.')


@pytest.fixture(scope='module')
def setup_module(request):
    def teardown_module():
        print("teardown_module called.")

    request.addfinalizer(teardown_module)
    print('setup_module called.')


@pytest.mark.asyncio
async def test_get_all(event_loop):
    resp = await httpclientid.retrieve(
        extra_params={"id": "all"}
    )
    assert getattr(resp, "code") == 100
    assert getattr(resp, "message") == "success"
    detail = getattr(resp, "detail")
    assert len(detail) == 5


@pytest.mark.asyncio
async def test_get_by_id_full(event_loop):
    resp = await httpclientid.retrieve(
        opt_id={"id": "1"},
        condition={"param_foo": "bar"},
        extra_headers={"head_foo": "bar"},
        extra_params={"foo": "bar"},
        extra_auths={"username": "foo"}
    )
    assert getattr(resp, "name") == "alpha"
    assert getattr(resp, "description") == "alpha is A"


@pytest.mark.asyncio
async def test_get_filter(event_loop):
    resp = await httpclient.retrieve(
        condition={"name": "al"},
        extra_params={"something": "nothing"}
    )
    assert getattr(resp, "code") == 100
    assert getattr(resp, "message") == "success"
    detail = getattr(resp, "detail")
    assert len(detail) == 1
    resource = detail[0]
    assert resource.get("name") == "alpha"
    assert resource.get("description") == "alpha is A"


@pytest.mark.asyncio
async def test_get_by_id(event_loop):
    resp = await httpclientid.retrieve(
        opt_id={"id": "1"}
    )
    assert getattr(resp, "name") == "alpha"
    assert getattr(resp, "description") == "alpha is A"


@pytest.mark.asyncio
async def test_get_404(event_loop):
    try:
        resp = await httpclientid.retrieve(
            extra_params={"id": "8"}
        )
    except HTTPException as ex:
        assert ex.status_code == 404

@pytest.mark.asyncio
async def test_get_500(event_loop):
    try:
        resp = await httpclientid.retrieve(
            opt_id={"id": "500"},
            extra_params={"id": "500"}
        )
    except HTTPException as ex:
        assert ex.status_code == 500

@pytest.mark.asyncio
async def test_create_422(event_loop):
    try:
        resp = await httpclient.create(
            obj_in=ResourceID(id="66666666",
                name="fox",
                description="fox is F").dict()
        )
    except HTTPException as ex:
        assert ex.status_code == 422


@pytest.mark.asyncio
async def test_create(event_loop):
    resp = await httpclientid.retrieve(
        extra_params={"id": "all"}
    )
    assert getattr(resp, "code") == 100
    assert getattr(resp, "message") == "success"
    detail = getattr(resp, "detail")
    assert len(detail) == 5

    resp = await httpclient.create(
        obj_in=ResourceID(id="6", name="fox", description="fox is F").dict()
    )

    resp = await httpclientid.retrieve(
        extra_params={"id": "all"}
    )
    assert getattr(resp, "code") == 100
    assert getattr(resp, "message") == "success"
    detail = getattr(resp, "detail")
    assert len(detail) == 6

    resp = await httpclientid.retrieve(
        opt_id={"id": "6"},
        extra_params={"id": "6"}
    )

    assert getattr(resp, "name") == "fox"
    assert getattr(resp, "description") == "fox is F"

    # clean up
    resp = await httpclientid.delete(
        opt_id={"id": "6"}
    )


@pytest.mark.asyncio
async def test_delete(event_loop):
    try:
        resp = await httpclient.create(
            obj_in=ResourceID(id="6", name="fox", description="fox is F").dict()
        )
        resp = await httpclientid.delete(
            opt_id={"id": "6"}
        )
        resp = await httpclientid.retrieve(
            opt_id={"id": "6"},
            extra_params={"id": "6"}
        )
        resp = await httpclientid.delete(
            opt_id={"id": "6"}
        )
    except HTTPException as httpex:
        assert httpex.status_code == 404

@pytest.mark.asyncio
async def test_delete_twice():
    try:
        resp = await httpclient.create(
            obj_in=ResourceID(id="6", name="fox", description="fox is F").dict()
        )
        resp = await httpclientid.delete(
            opt_id={"id": "6"}
        )
        resp = await httpclientid.delete(
            opt_id={"id": "6"}
        )
    except HTTPException as ex:
        assert ex.status_code == 404


@pytest.mark.asyncio
async def test_crud(event_loop):
    resp = await httpclientid.retrieve(
        extra_params={"id": "all"}
    )
    assert getattr(resp, "code") == 100
    assert getattr(resp, "message") == "success"
    detail = getattr(resp, "detail")
    assert len(detail) == 5

    resp = await httpclient.create(
        obj_in=ResourceID(id="6", name="fox", description="fox is F").dict()
    )

    resp = await httpclientid.retrieve(
        extra_params={"id": "all"}
    )
    assert getattr(resp, "code") == 100
    assert getattr(resp, "message") == "success"
    detail = getattr(resp, "detail")
    assert len(detail) == 6

    resp = await httpclientid.retrieve(
        opt_id={"id": "6"},
        extra_params={"id": "6"}
    )

    assert getattr(resp, "name") == "fox"
    assert getattr(resp, "description") == "fox is F"

    resp = await httpclientid.update(
        opt_id={"id": "6"},
        obj_in=Resource(name="firefox", description="firefox is FF").dict(),
        extra_params={"id": "6"}
    )

    resp = await httpclientid.retrieve(
        opt_id={"id": "6"},
        extra_params={"id": "6"}
    )

    assert getattr(resp, "name") == "firefox"
    assert getattr(resp, "description") == "firefox is FF"

    # clean up
    resp = await httpclientid.delete(
        opt_id={"id": "6"}
    )


if __name__ == '__main__':
    pytest.main([os.path.basename(__file__)])
