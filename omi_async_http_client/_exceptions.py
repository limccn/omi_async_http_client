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

from typing import Any

from ._status_code import status_codes


class HTTPException(Exception):
    def __init__(
            self, status_code: int = 500, trace_code: int = 199, detail: Any = None,
            headers: dict = None
    ) -> None:
        self.status_code = status_code
        self.trace_code = trace_code
        if detail is None:
            detail = status_codes.get_reason_phrase(status_code)
        self.detail = detail
        self.headers = headers

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r},trace_code={self.trace_code!r},detail={self.detail!r})"


def http_exception_decorator(**kwargs):
    def decorator(cls):
        for key, val in kwargs.items():
            if val is not None:
                setattr(cls, key, val)  # key -> _key for internal use
        return cls

    return decorator
