import paramiko
from paramiko.server import ServerInterface
from .shells.base import HoneypotShell


class FunnypotInterface(ServerInterface):

    def check_auth_password(self, username, password):
        print('AUTH: {}:{}'.format(username, password))
        self.username = username
        self.password = password
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        print('Channel: {}'.format(kind))
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        else:
            return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        self.shell = HoneypotShell(channel, self.username)
        self.shell.start()
        return True

    def check_channel_shell_request(self, channel):
        return True

    def get_banner(self):
        return ('Welcome, bitch\r\n', 'en-US')