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

class BulletinServer:
    def __init__(self, port_num):       
        self.connections = []
        self.message_boards = []
        self.port = port_num
        self.server_socket = socket.socket()
        self.server_socket.bind(("",self.port))

    def add_boards(self, boards: list[MessageBoard]):
        for board in boards:    
            self.message_boards.append(board)

    def remove_connection(self, conn) -> None:
        pass
        #TODO: remove given connection object from self.connections
    
    # adds given user to specified board, defaults to public board
    # returns two most recent messages on board
    def add_user_to_board(self, user:str, public=True, group_id=None, group_name=None) -> list:
        if public:
            self.message_boards[0].users.append(user)
            return self.message_boards[0].messages[-2:]

        # TODO: add handling for part 2
    
    # returns list of users in given group, defaults to public group
    def get_group_users(self, public=True, group_id=None, group_name=None) -> list:
        users = []

        if public:
            return self.message_boards[0].users
        # TODO: add handling for part 2
        
        return users

    # remove given user from given group, defaults to public group
    def remove_user_from_group(self, user:str, public=True, group_id=None, group_name=None) -> None:
        if public:
            self.message_boards[0].users.remove(user)
        # TODO: add handling for part 2

    # removes given user from every board on the server
    # this is used if client disconnects without
    # leaving groups
    def remove_user(self, username:str) -> None:
        for board in self.message_boards:
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

    def process_request(self) -> None:
        terminate = False

        while not terminate:
            req_message = self.conn_sock.recv(1024).decode("ascii")
            print(req_message)
            request_json = json.loads(req_message)

            command = request_json["command"]
            body = request_json["body"]
            
            response_code, response_body = self.execute_request(command, body)
            self.send_response(response_code, response_body)

            if command == "exit":
                terminate = True
                self.conn_sock.close()

    def execute_request(self, command:str, body:str or dict) -> (str, str or dict):
        if command == "exit":
            self.serv.remove_user(self.username)
            self.serv.remove_connection(self)
            return ("999", "Disconnecting, goodbye!")
        elif command == "choose username":
            if self.serv.check_unique_username(body):
                self.username = body
                return ("0", "Username accepted")
            else:
                return ("1", f"Username {body} already exists.")
        elif command == "join":
            # TODO: add error handling
            self.active_group_names.append("public")
            self.active_group_ids.append("0")

            messages = self.serv.add_user_to_board(self.username)
            users = self.serv.get_group_users()

            users_str = ""
            for user in users:
                users_str += f"{user}\n"

            messages_str = ""
            for message in messages:
                messages_str += f"Message ID: {message.message_id}, Sender: {message.sender}, Post Date: {message.post_date}, Subject: {message.subject}\n"
            
            response_body = {
                "users": users_str,
                "messages": messages_str
            }

            return ("0", response_body)
        elif command == "users":
            users = self.serv.get_group_users()
            return ("0", users)
        elif command == "post":
            subject = body["subject"]
            body = body["body"]

            self.serv.post_message_to_board(self.username, subject, body)

            return("0", "Message was posted!")
        elif command == "message":
            ...
        elif command == "leave":
            # return an error if client is not in the public group yet
            if "0" not in self.active_group_ids:
                return ("2", "You cannot leave the group because are not in the group")
            else:
                self.serv.remove_user_from_group(self.username)
                self.active_group_ids.remove("0")
                self.active_group_names.remove("public")
                return ("0", "Left public group")
    
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
            MessageBoard(1, 'a'),
            MessageBoard(2, 'b'),
            MessageBoard(3, 'c'),
            MessageBoard(4, 'd'),
            MessageBoard(5, 'e')
        ]
    )

    server()