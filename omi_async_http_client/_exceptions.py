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
