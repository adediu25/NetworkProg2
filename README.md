# Project Authors

Alex Dediu and Sara Marijolovic

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

## %post

Usage: `%post -s <message subject> -b <message body>`

## %users

Retreive list of all users in public group

Usage: `%users`

Protocol Response Message body: list object of all users

## %leave

Leave public group

Usage: `%leave`

## %message

Retreive the message with the given ID from the public board

Usage: `%message <message id>`

## %exit

Disconnect from server and end client program

Usage: `%exit`

## %groups

Display list of private groups available on the server

Usage: `%groups`

## %groupjoin

Join a private group by given group ID or name

Usage: `%groupjoin <group ID or name>`

User has the choice of giving a group name or a group ID number in the command

## %grouppost

Post a message to a given private board. Must first join the board.

Usage: `%grouppost <group ID or name> -s <message subject> -b <message body>`

User has the choice of giving a group name or a group ID number in the command

## %groupusers

List users in given private group

Usage: `%groupusers <group ID or name>`

User has the choice of giving a group name or a group ID number in the command

## %groupleave

Leave given private group. User must currently in group

Usage: `%groupleave <group ID or name>`

User has the choice of giving a group name or a group ID number in the command

## %groupmessage

Retrieve a message posted to a private board. Must be in private group and message ID must exist.

Usage: `%groupleave <group ID or name> <messgae ID>`

User has the choice of giving a group name or a group ID number in the command

# Response codes

- 0: success
- 1: username not unique
- 2: not in group
- 3: already in group
- 999: disconnecting

# Protocol Message Formats

## Request

The body/payload can be a single object, or it can also be a json object if multiple items need to be sent.

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

# Project Challenges

The only real challenge encountered was dealing with notifying the client when a user joins one of their groups or posts a message or leaves. The issue is that our client program blocks while waiting for the user to enter a command, so it cannot receive a response from the server with an update. The solution devised was to check with the server for any updates for every iteration of the client program. The client program keeps track of all the users and messages it knows about, then will check against what is true on the server. If there are any updates, the client program will display them to the user and update its own database. Obviously this solution is not optimal because updates are not received/displayed in real time. We could not think of any better solution.

Another roadblock was dealing with ensuring usernames are unique without making the user input the connect command everytime they do not choose a unique user name. The solution was to put the client and server into an infinite loop that breaks only once the user chooses a good username. The client program send the desired username to the server, the server checks uniqueness and relays the success or failure to the client. The client will reprompt the user for another username and send it to the server on failure.
