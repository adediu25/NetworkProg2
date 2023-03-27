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

    def main(self):
        port = 6969

        server_socket = socket.socket()
        server_socket.bind(('', port))

        server_socket.listen()

        while True:
            connection_socket, address = server_socket.accept()
            
            # print(self.connections[0])

            client_req = ClientRequest(connection_socket)
            self.connections.append(client_req)
            thread = threading.Thread(target=client_req)
            thread.start()

class ClientRequest:
    def __init__(self, sock):
        self.conn_sock = sock
        self.username = ""

    def __call__(self):
        self.process_request()

    def process_request(self):
        req_message = self.conn_sock.recv(1024).decode("ascii")
        print(req_message)
        req_json = json.loads(req_message)

    def main(self):
        while True:
            print("poo")

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