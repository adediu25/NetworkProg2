import socket
import json

class BulletinClient:
    def __init__(self):
        self.connection_socket = socket.socket()
        self.connected = False
        self.joined_public = False
        self.joined_groups = [False]*5
        self.group_names = []
        # client maintains lists of users and messages that it currently knows of
        self.public_messages = []
        self.public_users = []
        self.private_messages = [[]]*5
        self.private_users = [[]]*5

    def __call__(self):
        terminate = False

        # continuously prompt user for command until client exits program
        while not terminate:
            terminate = self.process_command(input("\nEnter a command: "))

            # if user has joined public group, check for updates with server
            if self.joined_public:
                self.check_public_updates()

            # TODO: add private group updates

    # Processes given command and executes appropriate action 
    # return True if exiting program, else False
    def process_command(self, command:str) -> bool:
        split_command = command.split()
        
        # return if invalid command format
        if (command[0] != '%'):
            print("Invalid command: commands must begin with '%'")
            return False

        # print error if user tries to use a command other than connect
        # without first being connected to a server
        if (split_command[0] != '%connect' and not self.connected):
            print("Error: not connected to a server yet")
            return False

        # return true if given exit command
        if (split_command[0] == "%exit"):
            message = {
                "command":"exit",
                "body":""
            }

            self.send_request(message)

            response = json.loads(self.receive_response())
            print(response["body"])

            # close connection with server
            self.connection_socket.close()

            return True

        # process all other commands
        if (split_command[0] == "%connect"):
            # TODO: check invalid command format
            
            # get address and port number from command line
            addr = split_command[1] 
            port = int(split_command[2])
            
            # try connecting to server
            try:
                self.connection_socket.connect((addr, port))
                self.connected = True
            except:
                print("Error connecting to server")
                return False

            # if connection is successful, prompt for username
            username = input("Enter a username for the server: ")
            self.choose_username(username)

            self.display_groups()

        elif (split_command[0] == "%join"):
            if self.joined_public:
                print("Already in public group!")
                return False

            message = {
                "command":"join",
                "body":""
            }

            # send request to join and receive response
            self.send_request(message)
            response = json.loads(self.receive_response())
            body = response["body"]

            # display users belonging to joined group
            print("Joined public board. Users belonging to group:")
            for user in body["users"]:
                print(user)
            self.public_users = body["users"]

            # display last 2 messages from board
            print("Messages posted to board:")
            for mes in body["messages"]:
                print(mes)
            self.public_messages = body["messages"]

            self.joined_public = True

        elif (split_command[0] == "%post"):
            subject = ""
            body = ""
            
            # TODO: add error checking

            # parse command for subject and body
            for i, word in enumerate(split_command):
                if i == 0 or i == 1:
                    continue
                if word == "-b":
                    break
            
                subject += word + " "
            
            for word in split_command[i+1:]:
                body += word + " "

            self.post_message(subject[:-1], body[:-1])
            response = json.loads(self.receive_response())
            print(response["body"])

        elif (split_command[0] == "%users"):
            message = {
                "command":"users",
                "body":""
            }

            self.send_request(message)
            response = json.loads(self.receive_response())
            print("Users in public group:")
            for user in response["body"]:
                print(user)

        elif (split_command[0] == "%message"):
            message_id = split_command[1]

            message = {
                "command":"message",
                "body":message_id
            }

            self.send_request(message)

            # receive response and display message subject and body
            response = json.loads(self.receive_response())
            print(f"Subject: {response['body']['subject']}\nBody: {response['body']['body']}")

        elif (split_command[0] == "%leave"):
            message = {
                "command":"leave",
                "body":""
            }

            self.send_request(message)

            response = json.loads(self.receive_response())
            # display error if command fails
            if response["code"] != "0":
                print(f"Error: {response['body']}")
            # clear out lists of users and messages for group
            else:
                print(response["body"])
                self.public_messages = []
                self.public_users = []
                self.joined_public = False

        elif (split_command[0] == "%groups"):
            self.display_groups()

        elif split_command[0] == "%groupjoin":
            group_identity = split_command[1]

            # error checking if given ID
            if group_identity.isnumeric():
                # display error if invalid ID
                if int(group_identity) > 5 or int(group_identity) < 1:
                    print("Error: invalid group ID")
                    return False
                # display error if already joined group with given ID
                if self.joined_groups[int(group_identity)-1]:
                    print(f"Already in group {group_identity}!")
                    return False
            # error checking if given name
            else:
                # display error if invalid name
                if group_identity not in self.group_names:
                    print("Error: invalid group name")
                    return False
                # display error if already joined group with given name
                id_num = self.group_names.index(group_identity)
                if self.joined_groups[id_num]:
                    print(f"Already in group {group_identity}!")
                    return False

            # send server request
            request = {
                "command":"groupjoin",
                "body":group_identity
            }

            self.send_request(request)

            response = json.loads(self.receive_response())
            body = response["body"]

            if response["code"] == "0":
                print(f"Joined group {group_identity}. Users belonging to group:")
                for user in body["users"]:
                    print(user)
                self.private_users[body["group_id"]] = body["users"]

                print("Messages posted to board:")
                for mes in body["messages"]:
                    print(mes)
                self.private_messages[body["group_id"]] = body["messages"]

                self.joined_groups[body["group_id"]] = True

        elif split_command[0] == "%grouppost":
            ...
        
        elif split_command[0] == "%groupusers":
            ...

        elif split_command[0] == "%groupleave":
            ...

        elif split_command[0] == "%groupmessage":
            ...
        
        else:
            print("Invalid command: command not recognized")

        return False

    # Sends username to server until a valid one is chosen
    def choose_username(self, username:str):
        # construct and send protocol message
        message = {
            "command":"choose username",
            "body":username
        }
        self.send_request(message)

        # receive response 
        response = json.loads(self.receive_response())

        # Ask user for username again if not valid/unique and
        # recursively call this function.
        if response["code"] == "1":
            print("Error: username is not unique")
            new_username = input("Enter a username: ")
            self.choose_username(new_username)
        else:
            print(f"Welcome {username}!")

    # posts a message with given subject and body to public board
    def post_message(self, subject:str, body:str):
        message = {
                "command":"post",
                "body": {
                    "subject":subject,
                    "body":body
                }
            }
        
        self.send_request(message)
    
    # convert json representation of protocol message to string
    # and send it to server
    def send_request(self, message:dict):
        #print(message)
        self.connection_socket.send(json.dumps(message).encode("ascii"))

    # receive response from server and return as string
    def receive_response(self) -> str:
        return self.connection_socket.recv(1024).decode("ascii")

    # this function checks for updates to public group users and messages
    def check_public_updates(self):
        
        # send request to check updates on known users and messages
        request = {
            "command":"public_updates",
            "body":{
                "client_user_list":self.public_users,
                "client_message_list":self.public_messages
            }
        }

        self.send_request(request)
        # print(request)

        response = json.loads(self.receive_response())
        # print(response)

        usrs_joined = response["body"]["joined"]
        usrs_left = response["body"]["left"]
        new_messages = response["body"]["new_messages"]

        # display any updates to user
        if len(usrs_joined) != 0:
            print("Users joined public group:")
            for usr in usrs_joined:
                print(usr)
                self.public_users.append(usr)
        if len(usrs_left) != 0:
            print("Users left public group:")
            for usr in usrs_left:
                print(usr)
                self.public_users.remove(usr)
        if len(new_messages) != 0:
            print("New messages in public group:")
            for msg in new_messages:
                print(msg)
                self.public_messages.append(msg)
            
    def display_groups(self):
        request = {
            "command":"groups",
            "body":""
        }

        self.send_request(request)
        response = json.loads(self.receive_response())

        body = response["body"]

        print("Private groups available to join on server:")
        for i in range(len(body["ids"])):
            print(f"ID: {body['ids'][i]} Name: {body['names'][i]}")

        self.group_names = body["names"]


if __name__ == "__main__":
    print("Welcome!")
    b = BulletinClient()
    
    b()
    
    print("Goodbye!")

    # b.process_command("%post -s First Message -b Hello world!")
    # b.process_command("%message 1")