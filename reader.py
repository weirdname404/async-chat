import asyncio
import logging
import aiofiles
import argparse
from datetime import datetime as dt

logger = logging.getLogger(__name__)
data_format = "[%d.%m.%y %H:%M]"
setup_text = """
Host: {}
Port: {}
Outfile: {}
"""


async def readline(reader):
    return await reader.readline()


async def listen(host, port, file, timeout=5):
    if file is None:
        file = 'out.log'
    reader, writer = await asyncio.open_connection(host, port)
    logger.info(f"STARTS TO LISTEN {host}:{port}")
    async with aiofiles.open(file, 'a') as f:
        try:
            while True:
                data = await asyncio.wait_for(readline(reader), timeout=timeout)
                data = data.decode()
                logger.info(data)
                date = dt.now().strftime(data_format)
                await f.write(f"{date} {data}")
        except asyncio.exceptions.TimeoutError:
            logger.info("Connection lost.")
        finally:
            writer.close()
            logger.debug("Reader session closed.")


if __name__ == "__main__":
    # logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host', default="minechat.dvmn.org", help='host listen to'
    )
    parser.add_argument(
        '--port', default=5000, type=int, help='port'
    )
    parser.add_argument(
        '--out', default='chat.history', help='output file name'
    )
    parser.add_argument(
        '--debug', action='store_true', help='debug mode'
    )
    args = parser.parse_args()
    # debug mode
    if args.debug:
        logger.setLevel(logging.DEBUG)

    args = (args.host, args.port, args.out)

    logger.info(setup_text.format(*args))
    asyncio.run(listen(*args))
