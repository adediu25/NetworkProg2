import socket
import json

class BulletinClient:
    def __init__(self):
        self.connection_socket = socket.socket()
        self.connected = False

    def __call__(self):
        terminate = False
        while not terminate:
            terminate = self.process_command(input("\nEnter a command: "))
            # response = json.loads(self.receive_response())
            # print(response)

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
            print(response)

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

        elif (split_command[0] == "%join"):
            message = {
                "command":"join",
                "body":""
            }

            self.send_request(message)

        elif (split_command[0] == "%post"):
            subject = ""
            body = ""
            
            for i, word in enumerate(split_command):
                if i == 0 or i == 1:
                    continue
                if word == "-b":
                    break
            
                subject += word + " "
            
            for word in split_command[i+1:]:
                body += word + " "

            self.post_message(subject[:-1], body[:-1])

        elif (split_command[0] == "%users"):
            message = {
                "command":"users",
                "body":""
            }

            self.send_request(message)

        elif (split_command[0] == "%message"):
            message_id = split_command[1]

            message = {
                "command":"message",
                "body":message_id
            }

            self.send_requeset(message)

        elif (split_command[0] == "%leave"):
            message = {
                "command":"leave",
                "body":""
            }

            self.send_request(message)

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


if __name__ == "__main__":
    print("Welcome!")
    b = BulletinClient()
    
    b()
    
    print("Goodbye!")

    # b.process_command("%post -s First Message -b Hello world!")
    # b.process_command("%message 1")