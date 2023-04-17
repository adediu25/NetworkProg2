import socket
import threading
import json
from datetime import date

# this class will be used to create objects that represent
# a message posted to a board with given attributes
class PostedMessage:
    def __init__(self, message_id:int, sender:str, subject:str, body:str):
        self.message_id = message_id
        self.sender = sender
        self.post_date = date.today()
        self.subject = subject
        self.body = body

# this class creates objects that represent a messsage board
# earch board will have individual ids, names, messages, and users
class MessageBoard:
    def __init__(self, grp_id: int, grp_name: str):
        self.group_id = grp_id
        self.group_name = grp_name
        self.message_id_counter = 0
        self.messages = []
        self.users = []

# this is the main class which runs the server and accepts connections
class BulletinServer:
    def __init__(self, port_num):       
        self.connections = []
        self.message_boards = []
        self.port = port_num
        self.server_socket = socket.socket()
        self.server_socket.bind(("",self.port))

    # adds the list of MessageBoard objects to the server
    # should be used once after initializing server object
    def add_boards(self, boards: list[MessageBoard]):
        for board in boards:    
            self.message_boards.append(board)

    # removes socket object from connections when client disconnects
    def remove_connection(self, conn) -> None:
        if conn in self.connections:
            self.connections.remove(conn)
        #TODO: remove given connection object from self.connections
    
    # adds given user to specified board, defaults to public board
    # returns two most recent messages on board
    def add_user_to_board(self, user:str, public=True, group_id=None, group_name=None) -> list:
        if public:
            self.message_boards[0].users.append(user)
            return self.message_boards[0].messages[-2:]

        # TODO: add handling for part 2
        else:
            if group_id is not None:
                self.message_boards[group_id].users.append(user)
                return self.message_boards[group_id].messages[-2:]
            else:
                ...


    # returns list of users in given group, defaults to public group
    def get_group_users(self, public=True, group_id=None, group_name=None) -> list:
        if public:
            return self.message_boards[0].users
        # TODO: add handling for part 2
        else:
            if group_id is not None:
                return self.message_boards[group_id].users
            else:
                ...

    # remove given user from given group, defaults to public group
    def remove_user_from_group(self, user:str, public=True, group_id=None, group_name=None) -> None:
        if public:
            self.message_boards[0].users.remove(user)
        # TODO: add handling for part 2
        else:
            if group_id is not None:
                self.message_boards[group_id].users.remove(user)
            else:
                ...

    # removes given user from every board on the server
    # this is used if client disconnects without
    # leaving groups
    def remove_user(self, username:str) -> None:
        for board in self.message_boards:
            if username in board.users:
                board.users.remove(username)
    
    # checks uniqueness of given username among usernames of connected users
    def check_unique_username(self, username:str) -> bool:
        for connection in self.connections:
            if connection.username == username:
                return False
        
        return True

    # Posts the message to the given board and sets all attributes of the message
    # defaults to public board
    def post_message_to_board(
        self, user:str, subject:str, body:str, public=True, group_id=None, group_name=None) -> None:
        if public:
            self.message_boards[0].messages.append(
                PostedMessage(self.message_boards[0].message_id_counter, user, subject, body)
            )
            self.message_boards[0].message_id_counter += 1
        # TODO: add handling for part 2
        else:
            if group_id is not None:
                self.message_boards[group_id].messages.append(
                    PostedMessage(self.message_boards[group_id].message_id_counter, user, subject, body)
                )
                self.message_boards[group_id].message_id_counter += 1
            else:
                pass

    # returns message subject and body by given message id from given group
    # defaults to public board
    def get_message_from_board(self, message_id:str, public=True, group_id=None, group_name=None) -> dict:
        if public:
            for message in self.message_boards[0].messages:
                if str(message.message_id) == message_id:
                    return {
                        "subject":message.subject,
                        "body":message.body
                    }
        # TODO: add handling for part 2
        else:
            if group_id is not None:
                for message in self.message_boards[group_id].messages:
                    if str(message.message_id) == message_id:
                        return {
                            "subject":message.subject,
                            "body":message.body
                        }
            else:
                pass

    # This function is serves the purpose of sending updates to the client
    # including users that joined or left a group and new messages posted to a boards
    # The function takes a list of users and messages from the client that the client
    # has knowledge of on its end. The function will check for differences and return 
    # 3 lists of new users, users that left, and new messages
    # Checks for updates in specified board, defaults to public board
    def check_updates(self, usrs:list, msgs:list, public=True, group_id=None, group_name=None) -> (list,list,list):
        users_joined = []
        users_left = []
        messages_added = []

        if public:
            for user in self.message_boards[0].users:
                if user not in usrs:
                    users_joined.append(user)
            
            for user in usrs:
                if user not in self.message_boards[0].users:
                    users_left.append(user)

            if len(msgs) < len(self.message_boards[0].messages):
                new_messages = self.message_boards[0].messages[len(msgs):]
                for message in new_messages:
                    messages_added.append(f"Message ID: {message.message_id}, Sender: {message.sender}, Post Date: {message.post_date}, Subject: {message.subject}")

            return users_joined, users_left, messages_added

        # TODO: add handling for part 2
    
    # returns lists of private group ids and names
    def get_groups(self) -> (list,list):
        ids = []
        names = []

        # iterate through boards but skip first as it is the public one
        for group in self.message_boards[1:]:
            ids.append(group.group_id)
            names.append(group.group_name)

        return ids, names

    def __call__(self):
        self.server_socket.listen()

        while True:
            connection_socket, address = self.server_socket.accept()
            
            client_req = ClientRequest(connection_socket, self)
            self.connections.append(client_req)
            thread = threading.Thread(target=client_req)
            thread.start()

# this class handles each connection thread that is accepted by the server
class ClientRequest:
    def __init__(self, sock, server):
        self.conn_sock = sock
        self.serv = server
        self.username = ""
        self.active_group_names = []
        self.active_group_ids = []

    def __call__(self):
        self.process_request()

    # processes request received from client connection
    def process_request(self) -> None:
        terminate = False

        # continuously process requests until client disconnects
        while not terminate:
            req_message = self.conn_sock.recv(1024).decode("ascii")
            print(req_message)
            request_json = json.loads(req_message)

            command = request_json["command"]
            body = request_json["body"]
            
            # execute the received command and send response
            response_code, response_body = self.execute_request(command, body)
            self.send_response(response_code, response_body)

            if command == "exit":
                terminate = True
                self.conn_sock.close()

    # execute corresponding actions for request
    # returns response code and response body for client
    def execute_request(self, command:str, body:str or dict) -> (str, str or dict):
        if command == "exit":
            # remove user and connection when client exits
            self.serv.remove_user(self.username)
            self.serv.remove_connection(self)
            return ("999", "Disconnecting, goodbye!")
        elif command == "choose username":
            # return success if username is unique
            if self.serv.check_unique_username(body):
                self.username = body
                return ("0", "Username accepted")
            # else return error to client
            else:
                return ("1", f"Username {body} already exists.")
        elif command == "join":
            # return an error if client is joining when they are already in
            if "0" in self.active_group_ids:
                return("3", "You are already in the group")

            # add public group to active memberships for client
            self.active_group_names.append("public")
            self.active_group_ids.append("0")

            # add user to board and get last 2 messages
            messages = self.serv.add_user_to_board(self.username)
            # get users in group
            users = self.serv.get_group_users()

            messages_list = []
            for message in messages:
                messages_list.append(f"Message ID: {message.message_id}, Sender: {message.sender}, Post Date: {message.post_date}, Subject: {message.subject}")
            
            response_body = {
                "users": users,
                "messages": messages_list
            }

            # sends group users and messages to client in response
            return ("0", response_body)
        elif command == "users":
            # get users from server
            users = self.serv.get_group_users()
            return ("0", users)
        elif command == "post":
            subject = body["subject"]
            msg_body = body["body"]

            # post message to server
            self.serv.post_message_to_board(self.username, subject, msg_body)

            return("0", "Message was posted!")
        elif command == "message":
            # get message from server
            message = self.serv.get_message_from_board(body)
            return ("0", message)
        elif command == "leave":
            # return an error if client is not in the public group yet
            if "0" not in self.active_group_ids:
                return ("2", "You cannot leave the group because are not in the group")
            else:
                # remove client from public group
                self.serv.remove_user_from_group(self.username)
                self.active_group_ids.remove("0")
                self.active_group_names.remove("public")
                return ("0", "Left public group")
        elif command == "public_updates":
            curr_users = body["client_user_list"]
            curr_messages = body["client_message_list"]

            users_joined, users_left, messages_added = self.serv.check_updates(curr_users, curr_messages)

            response_body = {
                "joined":users_joined,
                "left":users_left,
                "new_messages":messages_added
            }

            return ("0", response_body)
        elif command == "groups":
            ids, names = self.serv.get_groups()

            response_body = {
                "ids":ids,
                "names":names
            }

            return ("0", response_body)

        elif command == "groupjoin":
            group_identity = body

            if group_identity.isnumeric():
                grp_id = int(group_identity)
                grp_name = self.serv.message_boards[grp_id].group_name
            else:
                grp_name = group_identity
                for idx, group in enumerate(self.serv.message_boards):
                    if group.group_name == grp_name:
                        grp_id = idx
                
            messages = self.serv.add_user_to_board(self.username, public=False, group_id=grp_id)
            
            self.active_group_names.append(grp_name)
            self.active_group_ids.append(str(grp_id))

            users = self.serv.get_group_users(public=False, group_id=grp_id)

            messages_list = []
            for message in messages:
                messages_list.append(f"Message ID: {message.message_id}, Sender: {message.sender}, Post Date: {message.post_date}, Subject: {message.subject}")
            
            response_body = {
                "group_id": grp_id,
                "group_name": grp_name,
                "users": users,
                "messages": messages_list
            }

            return ("0", response_body)
        
        elif command == "grouppost":
            group_identity = body["group_identity"]
            subject = body["subject"]
            msg_body = body["body"]

            if group_identity.isnumeric():
                grp_id = int(group_identity)
                grp_name = self.serv.message_boards[grp_id].group_name
            else:
                grp_name = group_identity
                for idx, group in enumerate(self.serv.message_boards):
                    if group.group_name == grp_name:
                        grp_id = idx
        
            self.serv.post_message_to_board(self.username, subject, msg_body, public=False, group_id=grp_id)

            return("0", "Message was posted!")

        elif command == "groupusers":
            group_identity = body

            if group_identity.isnumeric():
                grp_id = int(group_identity)
                grp_name = self.serv.message_boards[grp_id].group_name
            else:
                grp_name = group_identity
                for idx, group in enumerate(self.serv.message_boards):
                    if group.group_name == grp_name:
                        grp_id = idx
            
            users = self.serv.get_group_users(public=False, group_id=grp_id)

            response_body = {
                "users":users,
                "group_id":grp_id,
                "group_name":grp_name
            }

            return ("0", response_body)
        
        elif command == "groupleave":
            group_identity = body

            if group_identity.isnumeric():
                grp_id = int(group_identity)
                grp_name = self.serv.message_boards[grp_id].group_name
            else:
                grp_name = group_identity
                for idx, group in enumerate(self.serv.message_boards):
                    if group.group_name == grp_name:
                        grp_id = idx

            self.active_group_names.remove(grp_name)
            self.active_group_ids.remove(str(grp_id))     

            self.serv.remove_user_from_group(self.username, public=False, group_id=grp_id)

            response_body = {
                "group_id":grp_id,
                "group_name":grp_name
            }

            return ("0", response_body)       

        elif command == "groupmessage":
            group_identity = body["group_identity"]
            msg_id = body["message_id"]

            if group_identity.isnumeric():
                grp_id = int(group_identity)
                grp_name = self.serv.message_boards[grp_id].group_name
            else:
                grp_name = group_identity
                for idx, group in enumerate(self.serv.message_boards):
                    if group.group_name == grp_name:
                        grp_id = idx

            message = self.serv.get_message_from_board(msg_id, public=False, group_id=grp_id)

            return ("0", message)
    
    # construct protocol message with given code and body
    # and send the response to the client
    def send_response(self, code:str, body:str) -> None:
        message = {
            "code":code,
            "body":body
        }
        
        self.conn_sock.send(json.dumps(message).encode("ascii"))
        print(message)

if __name__ == "__main__":
    server_port = 6969
    
    server = BulletinServer(server_port)

    server.add_boards(
        [
            MessageBoard(0, "public"),
            MessageBoard(1, 'Cats'),
            MessageBoard(2, 'Dogs'),
            MessageBoard(3, 'School'),
            MessageBoard(4, 'Cars'),
            MessageBoard(5, 'Food')
        ]
    )

    server()