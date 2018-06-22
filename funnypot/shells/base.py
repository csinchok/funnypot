import select
import threading
import time


class HoneypotShell(threading.Thread):

    def __init__(self, channel, username):
        super().__init__()
        self.channel = channel
        self.username = username

    def get_banner(self):
        return (
            'Hello, {username}. You are now connected to a honeypot\r\n'
        ).format(username=self.username)

    def process_command(self, command):
        return 'Hmmmm, I don\'t understand\r\n'

    def run(self):

        newline = b'\r'
        prompt = '$ '

        self.channel.sendall(self.get_banner())
        self.channel.sendall(prompt)
        buffer = b''
        while True:
            r, _, _ = select.select([self.channel], [], [])
            recieved = r[0].recv(256)
            buffer += recieved

            self.channel.sendall(recieved)

            while newline in buffer:
                self.channel.sendall('\n')
                command, buffer = buffer.split(newline, 1)

                print(command)

                if command == b'exit':
                    self.channel.close()
                    break

                output = self.process_command(command)
                self.channel.sendall(output)
                self.channel.sendall(prompt)
