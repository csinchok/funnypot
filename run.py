import argparse
import paramiko
import signal
import socket
import threading

from funnypot.interface import FunnypotInterface


def main():

    parser = argparse.ArgumentParser(description='Run a honeypot')
    parser.add_argument(
        '-a', '--address', dest='address', action='store', nargs='?',
        default='0.0.0.0', help='specify the address to bind to')
    parser.add_argument(
        '-p', '--port', dest='port', action='store', default=9090, nargs='?',
        type=int, help='specify the port to bind to (default: 9090)')
    parser.add_argument(
        '-c', '--connections', dest='connections', action='store',
        default=100, nargs='?', type=int,
        help='specify the max number of concurrent connections')

    options = parser.parse_args()

    paramiko.Transport.load_server_moduli()
    host_key = paramiko.rsakey.RSAKey.generate(1024)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

    try:
        server_socket.bind((options.address, options.port))
    except OSError as e:
        print('Cannot bind to socket: already in use')
        return

    server_socket.listen(options.connections)

    def handler(*args):
        server_socket.close()
    signal.signal(signal.SIGINT, handler)

    connections = []

    while True:

        try:
            conn, addr = server_socket.accept()
        except InterruptedError:
            break
        except OSError:
            break  # The socket closed...

        try:
            client_address = conn.getpeername()[0]
        except OSError:
            conn.close()
            print('Could not get peer name')
            continue

        transport = paramiko.Transport(conn)
        transport.add_server_key(host_key)
        server = FunnypotInterface()

        event = threading.Event()
        connections.append((transport, event))
        transport.start_server(server=server, event=event)


if __name__ == '__main__':
    main()
