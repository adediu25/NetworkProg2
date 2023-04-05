# Running The Project

The only requirement for running is Python 3. All the packages used are in the standard library.

## Server

`python /path/to/server.py`

The server will run continuously until the executable is interrupted.

Note: Use backslashes if on Windows. Also, the command `python` may be different on your machine, it may be `python3` or you may need to call the python executable directly from where it is installed on the machine.

## Client

`python /path/to/server.py`

The client program will be running and prompt for commands in the terminal. 

Note: Use backslashes if on Windows. Also, the command `python` may be different on your machine, it may be `python3` or you may need to call the python executable directly from where it is installed on the machine.

# Commands

## %connect

Connect to a server at given address and port

Usage: `%connect <address> <port>`

## %join

Join the public message board

Usage: `%join`

Protocol Response Message body:

```json
{
    "users": "<users in group>",
    "messages": "<last two messages on board>"
}
```

## %post

Usage: `%post -s <message subject> -b <message body>`

Protocol Request Message body:

```json
{
    "subject": "<subject line>",
    "body": "<message body>"
}
```

## %users

Retreive list of all users in public group

Usage: `%users`

## %leave

Leave public group

Usage: `%leave`

## %message

Retreive the message with the given ID from the public board

Usage: `%message <message id>`

Protocol Response Message body:

```json
{
    "subject": "<subject line>",
    "body": "<message id>"
}
```

## %exit

Disconnect from server and end client program

Usage: `%exit`

# Response codes

- 0: success
- 1: username not unique
- 2: not in group
- 999: disconnecting

# Protocol Message Formats

## Request

```json
{
    "command": "<command>",
    "body": "<payload>"
}
```

## Response

```json
{
    "response_code": "<code>",
    "body": "<payload>"
}
```