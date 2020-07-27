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
from typing import Optional

import pytest
from pydantic import BaseModel

sys.path.append("../")

from omi_async_http_client.async_http_client import APIClient
from omi_async_http_client._model import RequestModel
from omi_async_http_client._exceptions import HTTPException
from omi_async_http_client._status_code import status_codes
from omi_async_http_client.aiohttp_backend import AioHttpClientBackend

@RequestModel(api_name="/resources", api_prefix="/mock", api_suffix="")
class Resource(BaseModel):
    name: Optional[str]
    description: Optional[str]


@RequestModel(api_name="/resources/{id}", api_prefix="/mock", api_suffix="")
class ResourceID(Resource):
    id: Optional[str]


httpclient = APIClient(model=Resource,
                       http_backend="omi_async_http_client.aiohttp_backend.AioHttpClientBackend",
                       resource_endpoint="http://localhost:8003")

httpclientid = APIClient(model=ResourceID,
                         http_backend="omi_async_http_client.aiohttp_backend.AioHttpClientBackend",
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


def test_builder(setup_module):
    try:
        client_for_test = APIClient(model=Resource,
                                    http_backend="SomeHttpClientBackend",
                                    resource_endpoint="http://localhost:8003")
    except ValueError as err:
        assert str(err) == 'Cannot resolve http_backend type SomeHttpClientBackend'

    try:
        client_for_test = APIClient(model=Resource,
                                    http_backend="SomeHttpClientBackend")
    except AssertionError as err:
        assert str(err) == 'resource_endpoint can not be empty'

    client_for_test = APIClient(model=Resource,
                                http_backend="omi_async_http_client.aiohttp_backend.AioHttpClientBackend",
                                resource_endpoint="http://localhost:8003/")  # end with slash
    assert isinstance(client_for_test.http_backend, AioHttpClientBackend)

    client_for_test = APIClient(model=Resource,
                                http_backend=AioHttpClientBackend(),
                                resource_endpoint="http://localhost:8003")
    assert isinstance(client_for_test.http_backend, AioHttpClientBackend)


def test_enum(setup_module):
    assert status_codes.is_client_error(404)
    assert status_codes.is_client_error(500) is False
    assert status_codes.is_server_error(501)
    assert status_codes.is_server_error(404) is False
    assert status_codes.is_redirect(301)
    assert status_codes.is_redirect(200) is False
    assert status_codes.is_error(500)
    assert status_codes.is_error(200) is False

    assert status_codes.get_reason_phrase(800) == ""
    assert status_codes.get_reason_phrase(200) == "OK"

    assert str(status_codes.OK) == "200"


def test_exception(setup_module):
    try:
        raise HTTPException(status_code=status_codes.OK, trace_code=111)
    except HTTPException as e:
        assert e.status_code == status_codes.OK
        assert e.trace_code == 111
        assert repr(e) == "HTTPException(status_code=<StatuCode.OK: 200>,trace_code=111,detail='OK')"

    try:
        raise HTTPException(status_code=status_codes.OK, trace_code=111, detail="something detail")
    except HTTPException as e:
        assert e.status_code == status_codes.OK
        assert e.trace_code == 111
        assert e.detail == "something detail"
        assert repr(e) == "HTTPException(status_code=<StatuCode.OK: 200>,trace_code=111,detail='something detail')"


@pytest.mark.asyncio
async def test_get_all():
    resp = await httpclientid.retrieve(
        extra_params={"id": "all"}
    )
    assert getattr(resp, "code") == 100
    assert getattr(resp, "message") == "success"
    detail = getattr(resp, "detail")
    assert len(detail) == 5


@pytest.mark.asyncio
async def test_get_by_id_full():
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
async def test_get_filter():
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
async def test_get_by_id():
    resp = await httpclientid.retrieve(
        opt_id={"id": "1"}
    )
    assert getattr(resp, "name") == "alpha"
    assert getattr(resp, "description") == "alpha is A"


@pytest.mark.asyncio
async def test_get_404():
    try:
        resp = await httpclientid.retrieve(
            extra_params={"id": "8"}
        )
    except HTTPException as ex:
        assert ex.status_code == 404


@pytest.mark.asyncio
async def test_create():
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
async def test_delete():
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
    except HTTPException as ex:
        assert ex.status_code == 404


@pytest.mark.asyncio
async def test_crud():
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
    pytest.main(['test_integration_client_and_mock.py'])
