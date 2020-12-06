from socket import socket
from threading import Thread
from sys import exit, argv


class Chat:
    def __init__(self, host='127.0.0.1', port=5555):
        self._socket = socket()
        try:
            self._socket.connect((host, port))
        except ConnectionRefusedError:
            print("Connection refused")
            exit()
        self._working = True
        self._messageHandler = None

        self._username = "anonymous"

        self._getMessageThread = Thread(target=self._getMessage, daemon=True)
        self._getMessageThread.start()

    def messageHandler(self):
        def decorator(func):
            self._messageHandler = func
            return func
        return decorator

    def _getMessage(self):
        while self._working:
            try:
                msg = self._socket.recv(1024).decode('utf-8')
            except:
                continue
            if self._messageHandler is not None:
                self._messageHandler(msg)

    def sendMessage(self, msg):
        self._socket.sendall(f"{self._username}: {msg}".encode('utf-8'))

    def setUserName(self, name):
        self._username = name

    def close(self):
        self._working = False
        self._socket.close()


host = None
port = None
if (l := len(argv)) > 1:
    host = argv[1]
elif l > 2:
    try:
        port = int(argv[2])
    except ValueError:
        print("Port must be a number")
        exit()

chat = None
if host is not None and port is not None:
    chat = Chat(host, port)
elif host is not None:
    chat = Chat(host)
elif port is not None:
    chat = Chat(port=port)
else:
    chat = Chat()


@chat.messageHandler()
def printer(msg):
    print(f"\033[s\n\033[1A\033[1L{msg}\033[u\033[1B", end="")


def getUserName():
    colour_template = "\033[1;{}m{}\033[0m"
    username = input(colour_template.format(32, "Your name: "))

    colors = [
        colour_template.format(colour[1], colour[0])
        for colour in zip(
            ("Black", "Red", "Green", "Yellow", "Blue", "Purple", "Cyan", "White"),
            range(30, 38)
        )
    ]

    for i, c in enumerate(colors):
        print(i, c)

    while True:
        try:
            colour = int(
                input(f"\r\n\b{colour_template.format(32, 'Pick a colour:')} ")
            ) + 30
            break
        except ValueError:
            print("Colour must be an integer between 0 and 7")
    username = colour_template.format(colour, username)
    return username


def close():
    global running
    chat.close()
    exit()


def commandProcessor(command):
    return {
        "!exit": close,
    }.get(command, False)


username = getUserName()
chat.setUserName(username)

while True:
    msg = input(f"{username}: ")
    if func := commandProcessor(msg):
        func()
    try:
        chat.sendMessage(msg)
    except:
        print("Connection Refused")
        commandProcessor("!exit")()
