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

from typing import Dict, Union, Any

from pydantic import BaseModel, PositiveInt


# class BaseRequestModel(BaseModel):
#     def __init__(self, api_name: str, api_prefix: str, api_suffix: str):
#         super().__init__()
#         self._api_name = api_name
#         self._api_prefix = api_prefix
#         self._api_suffix = api_suffix
#         pass

#     @property
#     def api_name(self):
#         return self._api_name

#     @api_name.setter
#     def api_name(self, value: str):
#         # 如果设置的api值为空，将class名作为资源名称使用
#         if value is None or value == "":
#             value = str.lower(self.__class__.__name__)
#         self._api_name = value

#     @property
#     def api_prefix(self):
#         return self.api_prefix

#     @api_prefix.setter
#     def api_prefix(self, value: str):
#         assert value != "/", "A api prefix can not be '/', use blank '' or assign nothing"
#         assert value.startswith("/"), "A api prefix must start with '/'"
#         assert not value.endswith("/"), "A api prefix must not end with '/'"
#         # 去除 /
#         if value is None or value == "/":
#             value = ""
#         self._api_prefix = value

#     @property
#     def api_suffix(self):
#         return self.api_suffix

#     @api_suffix.setter
#     def api_suffix(self, value: str):
#         assert value != "/", "A api suffix can not be '/', use blank '' or assign nothing"
#         assert not value.startswith("/"), "A api suffix must start with '/'"
#         assert value.endswith("/"), "A api suffix must not end with '/'"
#         # 去除 /
#         if value is None or value == "/":
#             value = ""
#         self._api_suffix = value

class PagedModel(BaseModel):
    status: str
    page: PositiveInt
    has_next: bool
    total_pages: PositiveInt
    count: PositiveInt


class MessageModel(BaseModel):
    code: PositiveInt
    message: str
    detail: Union[Dict, Any]


def real_api_request_model(**kwargs):
    def decorator(cls):
        for key, val in kwargs.items():
            if val is not None:
                setattr(cls, "_" + key, val)  # key -> _key for internal use
        return cls

    return decorator


RequestModel = real_api_request_model
api_request_model = real_api_request_model
