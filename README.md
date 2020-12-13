# async-chat

Includes two scripts that help to work with a chat.

## `reader.py`

Connects to a chat websocket and writes data flow in the output file.

**Reader** has following _optional_ arguments:

- `--host` - the host reader should listen to;
- `--port` - the port reader should listen to;
- `--out` - output file name.

By default, there is working example that doesn't require any arguments.

## `sender.py`

Connects to a chat websocket via registering or authorizing a user. Allows user to send messages in the chat.

**Sender** has following _optional_ arguments:

- `--host` - the host sender should connect to;
- `--port` - the port sender should connect to;
- `--token` - json file with user token (if there is no such file, new one will be created);
- `--username` - username that user want to register;
- `--text` - the text that user wants to send to the chat. (Otherwise, interactive mode will be enabled.)

By default, there is working example that doesn't require any arguments.

### Requirements

- [poetry](https://python-poetry.org/)
- python 3.8+

### How to start

```bash
poetry shell
poetry install
```

Start Reader

```bash
python reader.py
```

Start Sender

```bash
python sender.py
```
