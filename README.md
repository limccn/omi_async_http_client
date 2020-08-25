# omi_async_http_client



### Description 
An async http client implemented with asyncio and backends


### Usage
1.Install omi_async_http_client from `pip`

```shell script
$pip install omi_async_http_client
```
or install from source code
```shell script
$python setup.py install
```
 
2.Install backend for omi_async_http_client, both sync and async are supported

use an async backend, eg. [aiohttp](https://github.com/aio-libs/aiohttp) or [httpx](https://github.com/encode/httpx/)

```shell script
 # use aiohttp as backend, async only
 $pip install aiohttp
```

```shell script
 # use httpx as backend, support both sync and async
 $pip install httpx
```  
or use a traditional sync backends [requests](https://github.com/psf/requests)

```shell script
 # use requests as backend, sync only
 $pip install requests
```  

Backend support list

| Backend Name | Async/Sync | Module | Class | Alias |
|-|-|-|-|
|[requests](https://github.com/psf/requests) | Sync | omi_async_http_client.requests_backend | RequestsClientBackend | requests |
|[aiohttp](https://github.com/aio-libs/aiohttp) | Async | omi_async_http_client.aiohttp_backend | AioHttpClientBackend | aiohttp |
|[httpx](https://github.com/encode/httpx/) | Async/Sync | omi_async_http_client.httpx_backend | HttpxClientBackend | httpx |
|[FastAPI](https://github.com/tiangolo/fastapi) | Async/Sync | omi_async_http_client.fastapi_testclient_backend | FastAPITestClientBackend | fastapi_test_client |


3.Apply to your project.

Set up a TEMPLATE APIClient builder function from `omi_async_http_client.APIClient`, 

omi_async_http_client will automatically fill backend parameters for execute a http request when use your TEMPLATE APIClient.

```python
from omi_async_http_client import APIClient as APIClientBuilder
from app.config import settings


def my_api_client_builder(model):
    return APIClientBuilder(
        model=model, # None is OK
        app=None, # app context to bind, None is OK
        # choose aiohttp as backend
        # use backend alias AioHttpClientBackend, or aiohttp
        http_backend="AioHttpClientBackend", # will convert to "omi_async_http_client.AioHttpClientBackend"
        resource_endpoint=settings.get("API_ENDPOINT_URL", ""),
        client_id=settings.get("API_ENDPOINT_CLIENT_ID", ""),
        client_secret=settings.get("API_ENDPOINT_CLIENT_SECRET", ""),
        config=None,  # extra config, # None is OK
    )
MyAPIClient = my_api_client_builder
```
Define a user model for request, use `@RequestModel` decorator to define your API, alias `@api_request_model` will take same effort when using `@RequestModel`.
```python
from pydantic import BaseModel
from typing import  List
from omi_async_http_client import RequestModel


@RequestModel(api_name="/staff/{id}", api_prefix="", api_suffix="")
class Staff(BaseModel):
    id:int
    name:str = ""
    age:int = 0
    gender:str = "F"

class PagedStaff(BaseModel):
    page:int
    offset:int
    limit:int
    staffs:List[Staff]
```
4.Test HTTP Client if is work, and enjoy omi_async_http_client.
```python
client = APIClient(Staff) # user Staff to create a Apiclient
# to retrieve some datas from a Restful API
response = await client.retrieve(
    condition={  # extra_params for pageing
        'id':123, # will fill {id} placeholder, change /staff/{id} to /staff/123.
        'name': 'python'
    },
    extra_params={  # extra_params for pageing
        'page': 1,
        'offset': 1,
        'limit': 10
    },
    paging_model=PagedStaff
)

```

5.We implemented a demo api provider use [FastAPI](https://github.com/tiangolo/fastapi) to show How to use this library. and testing is included.

@See [mock_fastapi.py](https://github.com/limccn/omi_async_http_client/blob/master/mock_fastapi.py) for detail


### License

##### omi_async_http_client is released under the Apache License 2.0.

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