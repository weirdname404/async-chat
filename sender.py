import aiofiles
import argparse
import asyncio
import logging
import json
from utils import reconnect, timeout

logger = logging.getLogger(__name__)
setup_text = """
Host: {}
Port: {}
Token File: {}
Username: {}
Text: {}
"""


@timeout(5)
async def _read_and_write(reader, writer, msg):
    logger.debug((await reader.readline()).decode())
    writer.write(f"{msg}\n".encode())
    await writer.drain()


async def _get_user_token(token_file):
    user_token = None
    try:
        async with aiofiles.open(token_file) as f:
            user_data = json.loads(await f.read())
        # extract token
        user_token = user_data['account_hash']
        logger.info("User token file was found.")
    except FileNotFoundError:
        logger.info("User token file was not found.")

    return user_token


async def register_user(host, port, username, token_file):
    logger.debug("Trying to open register connection...")
    reader, writer = await asyncio.open_connection(host, port)
    try:
        # skip welcome_text
        await _read_and_write(reader, writer, "")
        # send username
        await _read_and_write(reader, writer, username)

        user_data = (await reader.readline()).decode()
        logger.debug(f"Received {user_data}")
        user_data_dict = json.loads(user_data)
        user_token = user_data_dict['account_hash']
        # save token
        async with aiofiles.open(token_file, 'w') as f:
            await f.write(user_data)
            logger.info("User token file was created.")

        logger.info("User was registered.")
        return user_token

    except asyncio.exceptions.TimeoutError:
        logger.info("Connection lost.")
    finally:
        writer.close()
        logger.debug("Register session closed.")


async def authorize_user(connection, user_token):
    reader, writer = connection
    # read welcome text and send user_token
    await _read_and_write(reader, writer, user_token)

    response = (await reader.readline()).decode()
    logger.debug(f"Received {response}")
    user_data = json.loads(response)

    if user_data:
        logger.info("User was authorized.")
        return True
    logger.info("User was not authorized.")
    return False


async def submit_message(connection, msg):
    reader, writer = connection
    msg = msg.replace('\n', '\\n')
    await _read_and_write(reader, writer, f"{msg}\n")


@reconnect
async def start_chat_session(host, port, token_file, username, text):
    user_token = await _get_user_token(token_file)

    if not user_token:
        user_token = await register_user(host, port, username, token_file)

    logger.info("Trying to open chat connection...")
    connection = await asyncio.open_connection(host, port)
    try:
        _, writer = connection
        # try to auth
        user_authorized = await authorize_user(connection, user_token)
        if not user_authorized:
            logger.info("INVALID TOKEN. Fix it or create new one.")
            return

        if text and text != 'interactive':
            await submit_message(connection, text)
            logger.info("Message was sent.")
            return

        # interactive mode
        while True:
            msg = input("Type message to send or 'q' to exit: ")
            if msg == 'q':
                break
            await submit_message(connection, msg)
    except asyncio.exceptions.TimeoutError:
        logger.info("Connection lost.")
    finally:
        writer.close()
        logger.debug("Chat session closed.")


if __name__ == "__main__":
    # logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host', default="minechat.dvmn.org", help='chat host'
    )
    parser.add_argument(
        '--port', default=5050, type=int, help='chat port'
    )
    parser.add_argument(
        '--token', default='token.json', help='user token file'
    )
    parser.add_argument(
        '--text', default='interactive', help='text to send'
    )
    parser.add_argument(
        '--username', default="anonymous", help='username to register'
    )
    parser.add_argument(
        '--debug', action='store_true', help='debug mode'
    )
    args = parser.parse_args()
    # debug mode
    if args.debug:
        logger.setLevel(logging.DEBUG)

    args = (args.host, args.port, args.token, args.username, args.text)

    logger.info(setup_text.format(*args))
    asyncio.run(start_chat_session(*args))
