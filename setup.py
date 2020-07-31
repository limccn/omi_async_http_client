#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "omi_async_http_client",
    version = "0.1.4",
    keywords = ("http_client","aio","async","asyncio"),
    description = "An async http client implemented with [asyncio] and backends",
    long_description = "An async http client implemented with [asyncio] and backends, \
                        Supports both sync and async model to send http requests,\
                        The sync client is implemented with [requests] \
                        The async client is implemented with [aiohttp] and [httpx] client. \
                        ",
    license = "Apache License 2.0",

    url="https://github.com/limccn/omi_async_http_client",
    author = "limccn",
    author_email = "limccn@me.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["pydantic"]
)