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
    def __init__(self):       
        self.connections = []
        self.message_boards = []

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

    def main(self):
        port = 6969

        server_socket = socket.socket()
        server_socket.bind(('', port))

        server_socket.listen()

        while True:
            connection_socket, address = server_socket.accept()
            
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

    def process_request(self):
        terminate = False

        while not terminate:
            req_message = self.conn_sock.recv(1024).decode("ascii")
            print(req_message)
            request_json = json.loads(req_message)

            command = request_json["command"]
            body = request_json["body"]
            
            print(command)
            response_code, response_body = self.execute_request(command, body)

            if command == "exit":
                terminate = True       

    def execute_request(self, command:str, body:str) -> (str, str):
        if command == "exit":
            self.serv.remove_user(self.username)
            # TODO: remove user from all boards and connection list
        elif command == "choose username":
            if self.serv.check_unique_username(body):
                self.username = body
                return ("0", "")
            else:
                return ("1", f"Username {body} already exists.")
        elif command == "join":
            ...
        

if __name__ == "__main__":
    server = BulletinServer()

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

    server.main()