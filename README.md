# Commands

## %connect

Connect to a server at given address and port

Usage: `%connect <address> <port>`

## %join

Join the public message board

Usage: `%join`

## %post

Usage: `%post -s <message subject> -b <message body>`

Protocol Message body:

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

Protocol Message body:

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
- 

# Protocol Message Formats

## Request

```json
{
    "command": "<command>",
    "body": "<payload>"
}
```

## Resoponse

```json
{
    "response_code": "<code>",
    "body": "<payload>"
}
```