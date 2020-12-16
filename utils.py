import asyncio
import logging
import socket

logger = logging.getLogger(__name__)


def timeout(n):
    def wrapper(func):
        async def wrapped(*args):
            async def _func(*args):
                return await func(*args)

            return await asyncio.wait_for(_func(*args), n)
        return wrapped
    return wrapper


def reconnect(func):
    async def wrapper(*args):
        while True:
            try:
                await func(*args)
            except socket.error:
                logger.info("Network is unreachable.")
                await asyncio.sleep(1)
    return wrapper
