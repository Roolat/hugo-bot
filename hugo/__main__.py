"""
The MIT License (MIT)

Copyright (c) 2017-2018 Nariman Safiulin

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging
from typing import Sequence, Callable, Union, Any

from concord import __version__
from concord.client import Client
from concord.constants import EventType
from concord.context import Context
from concord.ext.base import Command, EventTypeFilter, EventNormalization
from concord.extension import Extension
from concord.middleware import Middleware, MiddlewareResult, chain_of

from concord.ext.audio import AudioExtension
from concord.ext.player import PlayerExtension
from concord.ext.stats import StatsExtension


logging.basicConfig(level=logging.DEBUG)


class CheckMiddleware(Middleware):
    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:
        return MiddlewareResult.OK


class RootMiddleware(Middleware):
    CHECK = chain_of(
        [
            CheckMiddleware(),
            EventTypeFilter(EventType.MESSAGE),
            EventNormalization(),
        ]
    )

    MW = chain_of(
        [
            Command(r"\$", prefix=True),
            EventTypeFilter(EventType.MESSAGE),
            EventNormalization(),
        ]
    )

    async def run(
        self, *args, ctx: Context, next: Callable, **kwargs
    ) -> Union[MiddlewareResult, Any]:
        result = await self.CHECK.run(*args, ctx=ctx, next=next, **kwargs)

        if self.is_successful_result(result):
            return await self.MW.run(*args, ctx=ctx, next=next, **kwargs)
        else:
            return await next(*args, ctx=ctx, **kwargs)


class RootExtension(Extension):
    NAME = "Root"
    DESCRIPTION = "Hugo Bot root extension"
    VERSION = __version__

    def __init__(self):
        super().__init__()
        self._client_middleware = [RootMiddleware()]

    @property
    def client_middleware(self) -> Sequence[Middleware]:
        return self._client_middleware


client = Client()
client.extension_manager.register_extension(RootExtension)
client.extension_manager.register_extension(StatsExtension)
client.extension_manager.register_extension(AudioExtension)
client.extension_manager.register_extension(PlayerExtension)
client.run(BOT_API_KEY)
