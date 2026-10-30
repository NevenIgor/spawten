"""Helpers for running synchronous Django ORM code outside the event loop."""
import asyncio
from functools import partial


async def run_sync(func, *args, **kwargs):
    """Execute a blocking (ORM) callable in the default thread pool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))
