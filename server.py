import socket
import threading
import json

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

    def remove_user(self, username:str) -> None:
        for board in self.message_boards:
            for name in board.users:
                if name == username:
                    board.users.remove(name)
                    break

    def check_unique_username(self, username:str) -> bool:
        for connection in self.connections:
            if connection.username == username:
                return False
        
        return True

    def __call__(self):
        self.server_socket.listen()

        while True:
            connection_socket, address = self.server_socket.accept()
            
            # print(self.connections[0])

            client_req = ClientRequest(connection_socket, self)
            self.connections.append(client_req)
            thread = threading.Thread(target=client_req)
            thread.start()

class ClientRequest:
    def __init__(self, sock, server):
        self.conn_sock = sock
        self.serv = server
        self.username = ""

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
            
            print(command)
            response_code, response_body = self.execute_request(command, body)
            self.send_response(response_code, response_body)

            if command == "exit":
                terminate = True
                       

    def execute_request(self, command:str, body:str) -> (str, str):
        if command == "exit":
            self.serv.remove_user(self.username)
            self.serv.remove_connection(self)
            self.conn_sock.close()
            return ("0", "")
        elif command == "choose username":
            if self.serv.check_unique_username(body):
                self.username = body
                return ("0", "")
            else:
                return ("1", f"Username {body} already exists.")
        elif command == "join":
            ...
        elif command == "users":
            ...
        elif command == "post":
            ...
        elif command == "message":
            ...
        elif command == "leave":
            ...
    
    def send_response(self, code:str, body:str) -> None:
        message = {
            "code":code,
            "body":body
        }
        self.conn_sock.send(json.dumps(message).encode("ascii"))

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