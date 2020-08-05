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

import logging
import random
import string
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar, Generic, Union
from urllib.parse import urlencode

from pydantic import BaseModel, PositiveInt, ValidationError

from ._exceptions import HTTPException
from ._model import MessageModel, PagedModel
from ._status_code import status_codes

ModelType = TypeVar("ModelType", bound=BaseModel)

logger = logging.getLogger(__name__)


class ClientBackendResponse(BaseModel):
    status_code: PositiveInt
    response: Dict


class AsyncHTTPClientContext:
    __metaclass__ = ABCMeta

    @abstractmethod
    def create(self):
        """
        Proxy function for internal cache object.
        @See CacheContext.create
        """

    @abstractmethod
    def destroy(self):
        """
        Proxy function for internal cache object.
        @See CacheContext.destroy
        """


class AsyncHttpClientSession(AsyncHTTPClientContext):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._client_or_session = None

    def __enter__(self):
        if not self._client_or_session:
            self.create()
        return self._client_or_session

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.destroy()

    async def __aenter__(self):
        if not self._client_or_session:
            await self.create()
        return self._client_or_session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.destroy()

    @abstractmethod
    def create(self):
        """
        Proxy function for internal cache object.
        @See CacheContext.create
        """

    @abstractmethod
    def destroy(self):
        """
        Proxy function for internal cache object.
        @See CacheContext.destroy
        """


class AsyncHTTPClientBackend:
    __metaclass__ = ABCMeta

    def __init__(self, client=None, config=None):
        super().__init__()
        self._client_ref = client
        self._config = config

        self.setup_config()

    @property
    def config(self):
        return self._config

    @property
    def client_ref(self):
        return self._client_ref

    def set_client_ref(self, value):
        self._client_ref = value

    def setup_config(self, config=None):
        if not config:
            return
        self._config = config

    @abstractmethod
    def send(self, url, data, header, auth, timeout) -> Any:
        """
        AsyncHTTPClientBackend执行DELETE操作，使用异步方式实现，返回ClientBackendResponse或 Dict
        SEND请求不要求服务器完成响应即可结束请求，即请求发送完成后直接结束操作，不用等待服务器Response。
        此类操作类似于浏览器的HTTP信标（HTTP Beacon）操作。

        url - URL, HTTP请求的URL
        data - (Optional) Dictionary, 异步HTTP请求的BODY内容，使用字典参数
        header - (Optional) Dictionary, 异步HTTP请求的HEADER内容，使用字典参数
        auth - (Optional) Dictionary, 异步HTTP请求的AUTH内容，使用字典参数
        timeout - int, 异步HTTP请求的超时设置，单位：秒

        Memo::

        """

    @abstractmethod
    def head(self, url, header, auth, timeout) -> Any:
        """
        AsyncHTTPClientBackend执行HEAD操作，使用异步方式实现，返回ClientBackendResponse或 Dict
        HEAD请求不要求服务器完成响应即可结束请求，即请求获得Response的Header以后完成本次操作，不用等待服务器Response

        url - URL, HTTP请求的URL
        data - (Optional) Dictionary, 异步HTTP请求的BODY内容，使用字典参数
        header - (Optional) Dictionary, 异步HTTP请求的HEADER内容，使用字典参数
        auth - (Optional) Dictionary, 异步HTTP请求的AUTH内容，使用字典参数
        timeout - int, 异步HTTP请求的超时设置，单位：秒

        Memo::
        """

    @abstractmethod
    def get(
            self, url, data, header, auth, timeout
    ) -> Union[ClientBackendResponse, Dict]:
        """
        AsyncHTTPClientBackend执行GET操作，使用异步方式实现，返回ClientBackendResponse或 Dict
        url - URL, HTTP请求的URL
        data - (Optional) Dictionary, 异步HTTP请求的BODY内容，使用字典参数
        header - (Optional) Dictionary, 异步HTTP请求的HEADER内容，使用字典参数
        auth - (Optional) Dictionary, 异步HTTP请求的AUTH内容，使用字典参数
        timeout - int, 异步HTTP请求的超时设置，单位：秒

        Memo::
        """

    @abstractmethod
    def put(
            self, url, data, header, auth, timeout
    ) -> Union[ClientBackendResponse, Dict]:
        """
        AsyncHTTPClientBackend执行PUT操作，使用异步方式实现，返回ClientBackendResponse或 Dict
        url - URL, HTTP请求的URL
        data - (Optional) Dictionary, 异步HTTP请求的BODY内容，使用字典参数
        header - (Optional) Dictionary, 异步HTTP请求的HEADER内容，使用字典参数
        auth - (Optional) Dictionary, 异步HTTP请求的AUTH内容，使用字典参数
        timeout - int, 异步HTTP请求的超时设置，单位：秒

        Memo::
        """

    @abstractmethod
    def post(
            self, url, data, header, auth, timeout
    ) -> Union[ClientBackendResponse, Dict]:
        """
        AsyncHTTPClientBackend执行POST操作，使用异步方式实现，返回ClientBackendResponse或 Dict
        url - URL, HTTP请求的URL
        data - (Optional) Dictionary, 异步HTTP请求的BODY内容，使用字典参数
        header - (Optional) Dictionary, 异步HTTP请求的HEADER内容，使用字典参数
        auth - (Optional) Dictionary, 异步HTTP请求的AUTH内容，使用字典参数
        timeout - int, 异步HTTP请求的超时设置，单位：秒

        Memo::
        """

    @abstractmethod
    def delete(
            self, url, data, header, auth, timeout
    ) -> Union[ClientBackendResponse, Dict]:
        """
        AsyncHTTPClientBackend执行DELETE操作，使用异步方式实现，返回ClientBackendResponse或 Dict
        url - URL, HTTP请求的URL
        data - (Optional) Dictionary, 异步HTTP请求的BODY内容，使用字典参数
        header - (Optional) Dictionary, 异步HTTP请求的HEADER内容，使用字典参数
        auth - (Optional) Dictionary, 异步HTTP请求的AUTH内容，使用字典参数
        timeout - int, 异步HTTP请求的超时设置，单位：秒

        Memo::
        """


class AsyncHTTPClient(Generic[ModelType]):
    DEFAULT_HTTP_REQUEST_TIMEOUT = 1 * 60

    resource_endpoint: str
    client_id: str
    client_secret: str
    http_backend: AsyncHTTPClientBackend

    def __init__(
            self,
            model: Type[ModelType],
            app: Any,
            http_backend: Union[str, Type[AsyncHTTPClientBackend]],
            resource_endpoint: str,
            client_id: Optional[str],
            client_secret: Optional[str],
            config: Union[Dict, Any] = None
    ):
        """
        __init__构造函数，使用参数创建一个AsyncHTTPClient实例对象，并返回
        model - Type[ModelType],
        http_backend - Union[str, AsyncHTTPClientBackend]，Backend的实现类，需要继承AsyncHTTPClientBackend接口
            可以使用str方式传入class名称，构造函数会根据str查找并自动解析响应的AsyncHTTPClientBackend
        resource_endpoint - str, 资源接入服务端的endpoint, 例：http://endpoint/api/v1
        client_id - str, client_id, 用于向资源接入服务端提供客户端ID标识。AsyncHTTPClient默认会将client_id用于HTTPBasicAuth
        client_secret - str, client_secret, 用于向资源接入服务端提供客户端的认证。
        Memo::
            1.使用str作为http_backend参数时，请使用完整的模块和类路径，当传入的http_backend无法被解析时会抛出异常
        Usage::
        """
        assert http_backend, "http_backend can not be empty"
        assert resource_endpoint, "resource_endpoint can not be empty"

        # 保留app的引用
        self._app_ref = app
        # 设置app
        self.setup_app(app)
        # 设置backend
        http_backend_instance = self.parse_backend_from_config(http_backend, config)
        self.http_backend_name = http_backend_instance.__class__.__name__
        self.http_backend = http_backend_instance

        self.resource_endpoint = resource_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.model = model
        self.config = config

    @property
    def app_ref(self):
        return self._app_ref

    def setup_app(self, app):
        """
        关联manager与app context上下文,当前manager对象的引用将被设置到`app.state.OMI_ASYNC_HTTP_CLIENT`
        """
        # 为app增加cache_manager属性
        if isinstance(app, object) and hasattr(app, "state"):
            state = getattr(app, "state")
            if state is not None and isinstance(state, object):
                if hasattr(state, "OMI_ASYNC_HTTP_CLIENT"):
                    # 如果上下文已经设置app，则取消设置
                    pass
                else:
                    app.state.OMI_ASYNC_HTTP_CLIENT = self
            else:
                pass

    def parse_backend_from_config(self, http_backend, config):
        """
        配置当前client的backend的实例
        """
        # 如果http_backend是str, 那么反射创建一个http_backend的instance
        if isinstance(http_backend, str):
            # alias
            http_backend_lower = http_backend.lower()
            if http_backend_lower in ["requestsclientbackend", "requests"]:
                http_backend = "omi_async_http_client.requests_backend.RequestsClientBackend"
            elif http_backend_lower in ["aiohttpclientbackend", "aiohttp"]:
                http_backend = "omi_async_http_client.aiohttp_backend.AioHttpClientBackend"
            elif http_backend_lower in ["httpxclientbackend", "httpx"]:
                # http_backend = "omi_async_http_client.httpx_backend.HttpxClientBackend"
                raise NotImplementedError("HttpxClientBackend is not implemented")
            elif http_backend_lower in ["fastapitestclientbackend", "fastapi_test_client"]:
                http_backend = "omi_async_http_client.fastapi_testclient_backend.FastAPITestClientBackend"
            else:
                pass
            name = http_backend.split('.')
            used = name.pop(0)
            try:
                found = __import__(used)
                # 查找模块下同名class_meta
                for frag in name:
                    used += '.' + frag
                    try:
                        # 使用getattr方式获取type
                        found = getattr(found, frag)
                    except AttributeError:
                        # 使用__import__导入type
                        __import__(used)
                        found = getattr(found, frag)
                # 实例化instance
                cache_backend_instance = found(client=self, config=config)
            except ImportError:
                raise ValueError('Cannot resolve http_backend type %s' % http_backend)
        elif isinstance(http_backend, AsyncHTTPClientBackend):
            # 设置client_ref
            http_backend.set_client_ref(self)
            # 设置config
            http_backend.setup_config(config)
            cache_backend_instance = http_backend
        else:
            raise ValueError(
                'http_backend type %s is not an instance of AsyncHTTPClientBackend ' % str(type(http_backend)))
        return cache_backend_instance

    def get_url(
            self,
            opt_id: Optional[Dict] = None,
            extra_params: Optional[Dict] = None,
            with_rnd: bool = False,
    ) -> str:
        """
        使用指定参数构建调用API的URL对象，返回URL类型对象，默认会将client_id放在url中
        opt_id - (Optional) Dictionary
                用于API调用的单个资源ID，传入的opt_id各个值会经过urlencode以后拼接在返回url中，
                对于数据库资源一般可以使用主键字段，可以是单一键，也可以是复合主键。
        extra_params - (Optional) Dictionary
                参与构建url的参数列表，传入的extra_params值会经过urlencode以后拼接在返回url中
        with_rnd - Bool , default = False,
                是否在url参数中增加rnd参数，默认不增加。
                用于请求时区别同一个资源URL的两次不同请求，参数的值默认使用8位字母和数字的组合
                random.sample(string.ascii_letters + string.digits, 8)
        Memo::
            对于，指定了ModelType的Client，会获取ModelType的api_name，prefix，suffix属性用于
            构造API调用用的URL， API将按"{prefix}{api_name}{suffix}规则构建，对于api_name，
            prefix，suffix中使用了占位符的情况，会使用extra_params中设定的参数值替换
            例如：api_name = foo/{placeholder}/bar,如果extra_params包含placeholder的mapping，
            则会将mapping的value替换，否则Raise KeyError

        Usage::
        #    >>> get_url(opt_id={"id_key1":"value"}, \
        #       extra_params={"placeholder":"value","param":"value"},\
        #       with_rnd=True)
        #    >>> http://{resource_endpoint}/{prefix}{api_name}{suffix}?id_key=value&placeholder=value&param=value
        """

        # 默认将client_id放在url中
        params = dict(
            {"client_id": self.client_id}
        )
        # 将opt_id的参数拆解后拼入param
        if opt_id is not None:
            params = {
                **params,
                **{
                    k: v for k, v in opt_id.items()
                    if v is not None and str(v) not in ["", "/", "?", "="]},  # 剔除"","/","?","="
            }
        # 将extra_param的参数拆解后拼入param
        if extra_params is not None:
            params = {
                **params,
                **{
                    k: v
                    for k, v in extra_params.items()
                    if v is not None and str(v) not in ["", "/", "?", "="]  # 剔除"","/","?","="
                },
            }

        # 设置设置前缀，后缀，从前面组合的param里面获取设置的值，补足相应的前后缀
        if self.model:
            api_name = getattr(self.model, "_api_name", "")
            # api_name不能为空
            assert api_name, "A api name can not be blank or nothing."
            # 使用params格式化
            api_name = api_name.format(**params)
            # 获取prefix
            prefix = getattr(self.model, "_api_prefix", "")
            prefix = prefix.format(**params)
            # 获取suffix
            suffix = getattr(self.model, "_api_suffix", "")
            suffix = suffix.format(**params)

            # api_name，prefix，suffix都不能以‘/’结尾
            assert not api_name.endswith("/"), "A api name must not end with '/'"
            assert not prefix.endswith("/"), "A api suffix must not end with '/'"
            assert not suffix.endswith("/"), "A api suffix must not end with '/'"

            # resource_endpoint不以“/”结尾而且不以“/” 开头 补一个"/"
            if self.resource_endpoint.endswith("/"):
                if prefix and prefix.startswith("/"):
                    prefix = prefix[1:]  # 剔除'/'
                else:
                    pass
            else:
                if prefix and not prefix.startswith("/"):
                    prefix = "/" + prefix
                else:
                    pass

            # 非"/"开头，补一个"/"
            if api_name != "" and not api_name.startswith("/"):
                api_name = "/" + api_name

            # 非空且非"/"开头，补一个"/"
            if suffix != "" and not suffix.startswith("/"):
                suffix = "/" + suffix

            api_path = f"{prefix}{api_name}{suffix}"
            # api_path = f"{self.model._api_prefix}/{self.model._api_name}/{self.model._api_suffix}"
        else:
            api_path = ""

        # 随机生成8位数字rnd,用于url
        if with_rnd:
            params["rnd"] = "".join(
                random.sample(string.ascii_letters + string.digits, 8)
            )
        url = f"{self.resource_endpoint}{api_path}?{urlencode(params)}"
        logger.info(f"<AsyncHTTPClient>:REQUEST_URL={str(url)}")
        return url

    def get_headers(self, extra_headers: Optional[Dict] = None) -> Dict:
        """使用指定参数构建调用API的HEADERS对象，返回Dict
        extra_headers - (Optional) Dictionary
                参与构建请求Header的参数列表，所有值都会mapping进返回Dict，只有None才会丢弃，空白字符""会保留
                根据HTTP协议的规则，传入的extra_headers值会根据设定的编码类型自动完成转码和编码操作
                如需传输urlencode以后结果，请自行调用后将结果传入
        Usage::
        #    >>> get_headers({"header_to_set1":"value1","header_to_set2":123,"header_to_set3":"",})
        #    >>> {
        #            "Content-Type": "application/json",
        #            "X_ClientId": self.client_id,
        #            "X_Client_Secret": self.client_secret,
        #            "header_to_set1":"value1",
        #            "header_to_set2":"value2",
        #            "header_to_set3":""
        #        }
        """
        # 默认将client_id放在X_ClientId中，client_secret放在X_Client_Secret中，使用application/json作为Content-Type
        headers = {
            "Content-Type": "application/json",
            "X_ClientId": self.client_id,
            "X_Client_Secret": self.client_secret,
        }
        if extra_headers is not None:
            headers = {
                **headers,
                **{k: v for k, v in extra_headers.items() if v is not None},
            }
        logger.info(f"<AsyncHTTPClient>:REQUEST_HEADERS={str(headers)}")
        return headers

    def get_auth(self, extra_auths: Optional[Dict] = None) -> Dict:
        """
        使用指定参数构建调用API的AUTH对象，返回Dict，默认使用client_id和client_secret用于生成用HTTPBasicAuth用的标准参数
        client_id将设置到username参数,client_secret将设置到password参数
        extra_auths - (Optional) Dictionary
                参与构建请求Auth的参数列表，所有值都会mapping进返回Dict，只有None才会丢弃，空白字符""会保留
        Memo::
            对于部分服务器端软件使用login而不是username的情况，此处需要根据实际使用extra_auths替换调整
        Usage::
        #    >>> get_auth({"auth_to_set1":"value1","auth_to_set2":123,"auth_to_set3":"",})
        #    >>> {
        #            "username": self.client_id,
        #            "password": self.client_secret
        #            "auth_to_set1":"value1",
        #            "auth_to_set2":"value2",
        #            "auth_to_set3":""
        #        }
        """
        # 默认使用client_id作为username，client_secret作为password，用于HTTPBasicAuth
        auth = {
            "username": self.client_id,
            "password": self.client_secret
        }
        # 增加extra_auths的值到Auth头部
        if extra_auths is not None:
            auth = {**auth, **{k: v for k, v in extra_auths.items() if v is not None}}
        logger.info(f"<AsyncHTTPClient>:REQUEST_AUTH={str(auth)}")
        return auth

    async def normal_post(
            self,
            obj_in: Union[ModelType, Dict],
            extra_params: Optional[Dict] = None,
            extra_headers: Optional[Dict] = None,
            extra_auths: Optional[Dict] = None,
            timeout=DEFAULT_HTTP_REQUEST_TIMEOUT,
    ) -> Optional[MessageModel]:
        try:
            logger.info(f"<AsyncHTTPClient>:REQUEST_BODY={str(obj_in)}")
            response = await self.http_backend.post(
                url=self.get_url(opt_id=None, extra_params=extra_params),
                data=obj_in,
                header=self.get_headers(extra_headers),
                auth=self.get_auth(extra_auths),
                timeout=timeout,
            )
            logger.info(f"<AsyncHTTPClient>:RESPONSE={str(response)}")
            if isinstance(response, Dict):
                # 获取响应代码
                status_code = response.get("status_code", 0)
                response_dict = response.get("response", None)
            else:
                status_code = getattr(response, "status_code", 0)
                response_dict = getattr(response, "response", None)

            if status_code == status_codes.OK:
                # 如果指定了opt_id,返回单个数据还是message？2选一
                # obj = self.model(**response_dict)
                obj = MessageModel(**response_dict)
                return obj
            else:
                raise HTTPException(status_code)
        except ValidationError as e:
            raise e
        except HTTPException as e:
            raise e
        finally:
            pass

    async def create(
            self,
            obj_in: Union[ModelType, Dict],
            extra_params: Optional[Dict] = None,
            extra_headers: Optional[Dict] = None,
            extra_auths: Optional[Dict] = None,
            extra_model: Type[ModelType] = None,
            timeout=DEFAULT_HTTP_REQUEST_TIMEOUT,
    ) -> Union[ModelType, MessageModel]:
        """
        调用远程Resource API，完成Create操作，返回Create完成后的对象，默认使用相同的model类型，Backend使用POST方式实现。
        obj_in->Dictionary or ModelType, not None，用于新增到远程资源的Model类型对象实例,不可为空
        extra_params - (Optional) Dictionary, 在http url parameters 中增加的相应的参数
        extra_headers - (Optional) Dictionary, 在http header 中增加的相应的参数
        extra_auths - (Optional) Dictionary, 在http auth 中增加的相应的参数
        extra_model - (Optional) Dictionary, 指定返回response需要转换的Model类型，如不指定按client初始化使用的model类型返回
        timeout - int, default = DEFAULT_HTTP_REQUEST_TIMEOUT

        Exceptions::
            ValidationError, Resource API调用发生验证错误时抛出
            HTTPAPIException，Resource API 调用发生业务性异常或错误时抛出，通常这类错误都会指定Trace_code,用于指定特定的处理逻辑
            HTTPException, Resource API 调用发生异常时抛出，通常这类错误都会指定status_code, 程序可以根据status_code进行处理
            Exception, Resource API调用过程中发生的其他异常
        Memo::

        Usage::
        """
        try:
            logger.info(f"<AsyncHTTPClient>:REQUEST_BODY={str(obj_in)}")
            # 发起post请求
            response = await self.http_backend.post(
                url=self.get_url(opt_id=None, extra_params=extra_params),
                data=obj_in,
                header=self.get_headers(extra_headers),
                auth=self.get_auth(extra_auths),
                timeout=timeout,
            )

            logger.info(f"<AsyncHTTPClient>:RESPONSE={str(response)}")

            if isinstance(response, Dict):
                # 获取响应代码
                status_code = response.get("status_code", 0)
                response_dict = response.get("response", None)
            elif isinstance(response, ClientBackendResponse):
                status_code = getattr(response, "status_code", 0)
                response_dict = getattr(response, "response", None)
            else:
                status_code = 0
                response_dict = None

            # 处理正确的响应内容
            if status_code in [status_codes.OK, status_codes.CREATED, status_codes.ACCEPTED]:
                # 如果额外指定了extra_model,返回转换过的extra_model类型，否则返回定义的类型
                if extra_model:
                    obj = extra_model(**response_dict)
                else:
                    obj = self.model(**response_dict)
                return obj
            else:
                raise HTTPException(status_code)
        except ValidationError as e:
            raise e
        except HTTPException as e:
            raise e
        finally:
            pass

    async def delete(
            self,
            opt_id: Dict,
            extra_params: Optional[Dict] = None,
            extra_headers: Optional[Dict] = None,
            extra_auths: Optional[Dict] = None,
            extra_model: Type[ModelType] = None,
            timeout=DEFAULT_HTTP_REQUEST_TIMEOUT,
    ) -> Union[ModelType, MessageModel]:
        """
        调用远程Resource API，完成Delete操作，返回Delete完成后的消息对象，Backend使用DELETE方式实现。
        opt_id->Dictionary not None，用于查找到唯一远程资源的ID值，如果是数据表应该是,不可为空
        extra_params - (Optional) Dictionary, 在http url parameters 中增加的相应的参数
        extra_headers - (Optional) Dictionary, 在http header 中增加的相应的参数
        extra_auths - (Optional) Dictionary, 在http auth 中增加的相应的参数
        extra_model - (Optional) Dictionary, 指定返回response需要转换的Model类型，如不指定按client初始化使用的model类型返回
        timeout - int, default = DEFAULT_HTTP_REQUEST_TIMEOUT

        Exceptions:
            ValidationError, Resource API调用发生验证错误时抛出
            HTTPAPIException，Resource API 调用发生业务性异常或错误时抛出，通常这类错误都会指定Trace_code,用于指定特定的处理逻辑
            HTTPException, Resource API 调用发生异常时抛出，通常这类错误都会指定status_code, 程序可以根据status_code进行处理
            Exception, Resource API调用过程中发生的其他异常
        Memo::

        Usage::
        """
        try:
            # 发起delete请求
            response = await self.http_backend.delete(
                url=self.get_url(opt_id=opt_id, extra_params=extra_params),
                data=None,
                header=self.get_headers(extra_headers),
                auth=self.get_auth(extra_auths),
                timeout=timeout,
            )

            logger.info(f"<AsyncHTTPClient>:RESPONSE={str(response)}")

            if isinstance(response, Dict):
                # 获取响应代码
                status_code = response.get("status_code", 0)
                response_dict = response.get("response", None)
            elif isinstance(response, ClientBackendResponse):
                status_code = getattr(response, "status_code", 0)
                response_dict = getattr(response, "response", None)
            else:
                status_code = 0
                response_dict = None

            if status_code == status_codes.OK:
                if extra_model:
                    obj = extra_model(**response_dict)
                else:
                    obj = self.model(**response_dict)
                return obj
            else:
                raise HTTPException(status_code)
        except HTTPException as e:
            raise e
        finally:
            pass

    async def retrieve(
            self,
            opt_id: Optional[Dict] = None,
            condition: Optional[Dict] = None,
            extra_params: Optional[Dict] = None,
            extra_headers: Optional[Dict] = None,
            extra_auths: Optional[Dict] = None,
            extra_model: Type[ModelType] = None,
            timeout=DEFAULT_HTTP_REQUEST_TIMEOUT,
            paging_model: Type[ModelType] = None,
    ) -> Union[ModelType, PagedModel, MessageModel]:
        """
        调用远程Resource API，完成Retrieve操作，返回Retrieve完成后的对象，可以是单个model，用户指定model，model列表或分类
        以后的model列表，Backend使用GET方式实现。
        opt_id->Dictionary not None，用于查找到唯一远程资源的ID值，如果是数据表应该是,不可为空
        condition - (Optional) Dictionary, 用于条件筛选的参数列表，
        extra_params - (Optional) Dictionary, 在http url parameters 中增加的相应的参数
        extra_headers - (Optional) Dictionary, 在http header 中增加的相应的参数
        extra_auths - (Optional) Dictionary, 在http auth 中增加的相应的参数
        extra_model - (Optional) Dictionary, 指定返回response需要转换的Model类型，如不指定按client初始化使用的model类型返回
        timeout - int, default = DEFAULT_HTTP_REQUEST_TIMEOUT

        Exceptions:
            ValidationError, Resource API调用发生验证错误时抛出
            HTTPAPIException，Resource API 调用发生业务性异常或错误时抛出，通常这类错误都会指定Trace_code,用于指定特定的处理逻辑
            HTTPException, Resource API 调用发生异常时抛出，通常这类错误都会指定status_code, 程序可以根据status_code进行处理
            Exception, Resource API调用过程中发生的其他异常
        Memo::
            返回的model类型对象的优先顺位
            self.model(指定opt_id) -> extra_model -> paging_model -> MessageModel
        Usage::
        """
        # 将条件拼接参数,剔除空白
        if condition is not None:
            extra_params = {
                **extra_params,
                **{k: v for k, v in condition.items() if v is not None},
            }

        try:
            # 发起get请求
            response = await self.http_backend.get(
                url=self.get_url(
                    opt_id=opt_id, extra_params=extra_params, with_rnd=True
                ),
                data=None,
                header=self.get_headers(extra_headers),
                auth=self.get_auth(extra_auths),
                timeout=timeout,
            )

            logger.info(f"<AsyncHTTPClient>:RESPONSE={str(response)}")

            if isinstance(response, Dict):
                # 获取响应代码
                status_code = response.get("status_code", 0)
                response_dict = response.get("response", None)
            elif isinstance(response, ClientBackendResponse):
                status_code = getattr(response, "status_code", 0)
                response_dict = getattr(response, "response", None)
            else:
                status_code = 0
                response_dict = None

            if status_code == status_codes.OK:
                if opt_id:
                    # 如果指定了opt_id,返回单个数据，否则返回分页数据
                    obj = self.model(**response_dict)
                elif extra_model:
                    # 如果指定了extra_model，则返回
                    obj = extra_model(**response_dict)
                elif paging_model:
                    # 如果指定了paging_model,返回分页模型数据，否则返回分页数据
                    obj = paging_model(**response_dict)
                else:
                    # 其他情况，返回消息model
                    obj = MessageModel(**response_dict)
                # else:
                #     # TODO 如果不指定paging_model,则自动返回一个PagedModel
                #     raise NotImplementedError
                #     obj = PagedModel.parse_obj(response_dict)
                #     items_type_name = str.lower(self.model.__name__)
                #     items_dict = response_dict.get(items_type_name, None)
                #     items = [
                #         self.model(**item) for item in items_dict if item is not None
                #     ]
                #     obj.__fields__[items_type_name] = items
                return obj
            else:
                raise HTTPException(status_code)
        except HTTPException as e:
            raise e
        finally:
            pass

    async def update(
            self,
            opt_id: Optional[Dict],
            obj_in: Union[ModelType, Dict],
            extra_params: Optional[Dict] = None,
            extra_headers: Optional[Dict] = None,
            extra_auths: Optional[Dict] = None,
            extra_model: Type[ModelType] = None,
            timeout=DEFAULT_HTTP_REQUEST_TIMEOUT,
            mult_update_model: Type[ModelType] = None,
    ) -> Union[ModelType, MessageModel]:
        """
        调用远程Resource API，完成Update操作，返回Update完成后的对象，可以是单个model，用户指定model，被update完成的model列表，
        Backend使用PUT方式实现。
        opt_id->Dictionary not None，用于查找到唯一远程资源的ID值，如果是数据表应该是,不可为空
        obj_in->Dictionary or ModelType, not None，用于新增到远程资源的Model类型对象实例,不可为空
        extra_params - (Optional) Dictionary, 在http url parameters 中增加的相应的参数
        extra_headers - (Optional) Dictionary, 在http header 中增加的相应的参数
        extra_auths - (Optional) Dictionary, 在http auth 中增加的相应的参数
        extra_model - (Optional) Dictionary, 指定返回response需要转换的Model类型，如不指定按client初始化使用的model类型返回
        timeout - int, default = DEFAULT_HTTP_REQUEST_TIMEOUT
        mult_update_model - ModelType, 指定用于返回的多条UPDATE结果的Model类型

        Exceptions::
           ValidationError, Resource API调用发生验证错误时抛出
           HTTPAPIException，Resource API 调用发生业务性异常或错误时抛出，通常这类错误都会指定Trace_code,用于指定特定的处理逻辑
           HTTPException, Resource API 调用发生异常时抛出，通常这类错误都会指定status_code, 程序可以根据status_code进行处理
           Exception, Resource API调用过程中发生的其他异常
        Memo::
            返回的model类型对象的优先顺位
            self.model -> extra_model -> mult_update_model -> MessageModel
        Usage::
        """
        try:
            logger.info(f"<AsyncHTTPClient>:REQUEST_BODY={str(obj_in)}")
            # 发起put请求
            response = await self.http_backend.put(
                url=self.get_url(opt_id=opt_id, extra_params=extra_params),
                data=obj_in,
                header=self.get_headers(extra_headers),
                auth=self.get_auth(extra_auths),
                timeout=timeout,
            )
            logger.info(f"<AsyncHTTPClient>:RESPONSE={str(response)}")
            # 获取响应代码

            if isinstance(response, Dict):
                # 获取响应代码
                status_code = response.get("status_code", 0)
                response_dict = response.get("response", None)
            elif isinstance(response, ClientBackendResponse):
                status_code = getattr(response, "status_code", 0)
                response_dict = getattr(response, "response", None)
            else:
                status_code = 0
                response_dict = None

            if status_code == status_codes.OK:
                if opt_id:
                    # 如果指定了opt_id,返回单个数据
                    obj = self.model(**response_dict)
                elif extra_model:
                    # 如果指定了extra_model,，否则返回分页数据
                    obj = extra_model(**response_dict)
                elif mult_update_model:
                    # 如果指定了mult_update_model,，否则返回分页数据
                    obj = mult_update_model(**response_dict)
                else:
                    # 其他情况，返回消息model
                    obj = MessageModel(**response_dict)
                return obj
            else:
                raise HTTPException(status_code)
        except HTTPException as e:
            raise e
        finally:
            pass


def api_client_builder(
        model: Type[ModelType],
        app=None,
        http_backend="",
        resource_endpoint: str = "",
        client_id: str = "",
        client_secret: str = "",
        config: Union[Dict, Any] = None
) -> AsyncHTTPClient:
    """
    使用参数创建一个AsyncHTTPClient实例对象，并返回
    默认使用AioHttpClientBackend作为Backend实现
    resource_endpoint - str, 资源接入服务端的endpoint, 例：http://endpoint/api/v1，
        默认会从settings中获取"DATABASE_SERVER_URL"属性，如果没有将raise异常，使用getattr(settings, "DATABASE_SERVER_URL", "")
    client_id - str, client_id, 用于向资源接入服务端提供客户端ID标识。AsyncHTTPClient默认会将client_id用于HTTPBasicAuth，
        默认会从settings中获取"SERVICE_CLIENT_ID"属性，如果没有设定将设置为空，使用getattr(settings, "SERVICE_CLIENT_ID", "")
    client_secret - str, client_secret, 用于向资源接入服务端提供客户端的认证。
        默认会从settings中获取"SERVICE_CLIENT_SECRET"属性，如果没有设定将设置为空，使用getattr(settings, "SERVICE_CLIENT_SECRET", "")

    Memo::
        
    Usage::
    """
    assert resource_endpoint, "resource_endpoint can not be empty"
    return AsyncHTTPClient(
        model=model,
        app=app,
        http_backend=http_backend,
        resource_endpoint=resource_endpoint,
        client_id=client_id,
        client_secret=client_secret,
        config=config
    )


APIClient = api_client_builder
