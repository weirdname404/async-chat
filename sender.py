import aiofiles
import argparse
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


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
    try:
        reader, writer = await asyncio.open_connection(host, port)
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
        logger.debug("Register session closed.")
    finally:
        writer.close()

    return user_token


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
    await _read_and_write(reader, writer, f"{msg}\n")


async def start_chat_session(host, port, token_file, username, text):
    user_token = await _get_user_token(token_file)

    if not user_token:
        user_token = await register_user(host, port, username, token_file)

    try:
        connection = await asyncio.open_connection(host, port)
        _, writer = connection
        # try to auth
        user_authorized = await authorize_user(connection, user_token)
        if not user_authorized:
            logger.info("INVALID TOKEN. Fix it or create new one.")
            return

        if text:
            await submit_message(connection, f"{text}\n")
            logger.info("Message was sent.")
            return

        # interactive mode
        while True:
            msg = input("Type message to send or 'q' to exit: ")
            if msg == 'q':
                break
            await submit_message(connection, f"{msg}\n")
    finally:
        writer.close()


if __name__ == "__main__":
    # logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='chat host')
    parser.add_argument('--port', help='chat port')
    parser.add_argument('--token', help='user token file')
    parser.add_argument('--text', help='text to send')
    parser.add_argument('--username', help='username to register')
    args = parser.parse_args()

    # default vars
    if (host := args.host) is None:
        host = "minechat.dvmn.org"
    if (port := args.port) is None:
        port = 5050
    if (token_file := args.token) is None:
        token_file = 'token.json'
    if (username := args.username) is None:
        username = "anonymous"

    text = args.text
    setup_text = (
        "Setup",
        f"Host: {host}",
        f"Port: {port}",
        f"Token File: {token_file}",
        f"Username: {username}",
        f"Text: {text if text else 'interactive'}\n"
    )
    logger.info("\n".join(setup_text))
    asyncio.run(start_chat_session(host, port, token_file, username, text))
