import asyncio
import logging
import aiofiles
import argparse
from datetime import datetime as dt

logger = logging.getLogger(__name__)
data_format = "[%d.%m.%y %H:%M]"


async def listen(host, port, file):
    if file is None:
        file = 'out.log'
    reader, writer = await asyncio.open_connection(host, port)
    logger.info(f"STARTS TO LISTEN {host}:{port}")
    while True:
        data = await reader.readline()
        async with aiofiles.open(file, 'a') as f:
            date = dt.now().strftime(data_format)
            await f.write(f"{date} {data.decode()}")
        await asyncio.sleep(0)


if __name__ == "__main__":
    # logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='foo help')
    parser.add_argument('--port', help='foo help')
    parser.add_argument('--out', help='foo help')
    args = parser.parse_args()
    asyncio.run(listen(args.host, args.port, args.out))
