import socket

class BulletinClient:
    def __init__(self):
        self.connection_socket = socket.socket()

    def connect_to_server(self, addr, port):
        self.connection_socket.connect((addr, port))

    def disconnect_from_server(self):
        self.connection_socket.close()

    # return True if exiting program, else False
    def process_command(self, command:str):
        split_command = command.split()
        
        # return if invalid command format
        if (command[0] != '%'):
            print("Invalid command: commands must begin with '%'")
            return False

        # return true if given exit command
        if (split_command[0] == "%exit"):
            return True

        # process all other commands
        if (split_command[0] == "%connect"):
            self.connection_socket.connect((split_command[1], int(split_command[2])))
            username = input("Enter a username for the server: ")
            self.choose_username(username)

        elif (split_command[0] == "%join"):
            message = {
                "command":"join",
                "body":""
            }

            self.send_message(message)

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

            self.send_message(message)

        elif (split_command[0] == "%message"):
            message_id = split_command[1]

            message = {
                "command":"message",
                "body":message_id
            }

            self.send_message(message)

        elif (split_command[0] == "%leave"):
            message = {
                "command":"leave",
                "body":""
            }

            self.send_message(message)

        else:
            print("Invalid command: command not recognized")

        return False

    def choose_username(self, username:str):
        ...

    def post_message(self, subject:str, body:str):
        message = {
                "command":"post",
                "body": {
                    "subject":subject,
                    "body":body
                }
            }
        
        self.send_message(message)
    
    def send_message(self, message):
        print(message)


if __name__ == "__main__":
    print("Welcome!")
    b = BulletinClient()
    
    terminate = False
    while not terminate:
        terminate = b.process_command(input("Enter a command: "))
    
    print("Goodbye!")

    # b.process_command("%post -s First Message -b Hello world!")
    # b.process_command("%message 1")