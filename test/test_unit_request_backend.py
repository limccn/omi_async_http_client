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

import asyncio
import os
import sys

import pytest
from requests.auth import HTTPBasicAuth

sys.path.append("../")

from omi_async_http_client._exceptions import HTTPException
from omi_async_http_client.requests_backend import RequestsClientBackend

# =======================================
# install nest_asyncio for unit test when 
# RuntimeError: This event loop is already running
# pip install nest_asyncio
# import nest_asyncio
# nest_asyncio.apply()
# =======================================

BASE_URL = "http://localhost:8003"

backend = RequestsClientBackend()

backend_event_loop = RequestsClientBackend(event_loop=asyncio.new_event_loop())


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
async def test_event_loop(event_loop):
    event_loop = backend.get_event_loop()
    assert event_loop is not None
    event_loop = backend_event_loop.get_event_loop()
    assert event_loop is not None


@pytest.mark.asyncio
async def test_send(event_loop):
    try:
        resp = await backend.send(
            url=BASE_URL + "/mock/users/me",
            data={},
            header={},
            auth=HTTPBasicAuth("client_id", "client_secret"),
            timeout=60)
    except Exception as err:
        assert isinstance(err, NotImplementedError)


@pytest.mark.asyncio
async def test_head(event_loop):
    resp = await backend.head(
        url=BASE_URL + "/mock/users/me",
        header={},
        auth=HTTPBasicAuth("client_id", "client_secret"),
        timeout=60)
    assert resp.status_code == 405  # filtered by server config ,return 405


@pytest.mark.asyncio
async def test_head_dict_auth(event_loop):
    resp = await backend.head(
        url=BASE_URL + "/mock/users/me",
        header={},
        auth={"username": "client_id", "password": "client_secret"},
        timeout=60)
    assert resp.status_code == 405  # filtered by server config ,return 405


@pytest.mark.asyncio
async def test_get_dict_auth(event_loop):
    resp = await backend.get(
        url=BASE_URL + "/mock/users/me",
        data={},
        header={},
        auth={"username": "client_id", "password": "client_secret"},
        timeout=60)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_post_dict_auth(event_loop):
    data = {"id": "6", "name": "fox", "description": "fox is F"}
    resp = await backend.post(
        url=BASE_URL + "/mock/resources",
        data=data,
        header={"Content-Type": "application/json"},
        auth={"username": "client_id", "password": "client_secret"},
        timeout=60)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_put_dict_auth(event_loop):
    data = {"name": "firefox", "description": "firefox is FF"}
    resp = await backend.put(
        url=BASE_URL + "/mock/resources/6",
        data=data,
        header={"Content-Type": "application/json"},
        auth={"username": "client_id", "password": "client_secret"},
        timeout=60)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_dict_auth(event_loop):
    try:
        resp = await backend.delete(
            url=BASE_URL + "/mock/resources",
            data=None,
            header={"Content-Type": "application/json"},
            auth={"username": "client_id", "password": "client_secret"},
            timeout=60)
        assert resp.status_code == 200
    except HTTPException as httpex:
        assert httpex.status_code == 405


@pytest.mark.asyncio
async def test_get_basic_auth(event_loop):
    resp = await backend.get(
        url=BASE_URL + "/mock/users/me",
        data={},
        header={},
        auth=HTTPBasicAuth("client_id", "client_secret"),
        timeout=60)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_post_basic_auth(event_loop):
    data = {"id": "6", "name": "fox", "description": "fox is F"}
    resp = await backend.post(
        url=BASE_URL + "/mock/resources",
        data=data,
        header={"Content-Type": "application/json"},
        auth=HTTPBasicAuth("client_id", "client_secret"),
        timeout=60)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_put_basic_auth(event_loop):
    data = {"name": "firefox", "description": "firefox is FF"}
    resp = await backend.put(
        url=BASE_URL + "/mock/resources/6",
        data=data,
        header={"Content-Type": "application/json"},
        auth=HTTPBasicAuth("client_id", "client_secret"),
        timeout=60)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_basic_auth(event_loop):
    try:
        resp = await backend.delete(
            url=BASE_URL + "/mock/resources",
            data=None,
            header={"Content-Type": "application/json"},
            auth=HTTPBasicAuth("client_id", "client_secret"),
            timeout=60)
        assert resp.status_code == 200
    except HTTPException as httpex:
        assert httpex.status_code == 405


if __name__ == '__main__':
    pytest.main([os.path.basename(__file__)])
