from threading import Thread
from socket import socket


class User:
    def __init__(self, connection: socket):
        self._connection = connection

    def sendMessage(self, msg: str) -> None:
        self._connection.sendall(msg.encode('utf-8'))

    def getMessage(self) -> str:
        return self._connection.recv(1024).decode('utf-8')

    def closeConnection(self):
        self._connection.close()


connectedUsers = []


class ConnectUsers(Thread):
    def __init__(self, socket: socket, messageHandler):
        Thread.__init__(self)
        self._socket = socket
        self._messageHandler = messageHandler

    def run(self):
        while True:
            conn, _ = self._socket.accept()
            user = User(conn)
            connectedUsers.append(user)
            self._messageHandler.addUser(user)


class MessageHandler:
    def addUser(self, user):
        thread = Thread(target=self._messageHandler, args=(user,))
        thread.start()

    def removeUser(self, user):
        user.closeConnection()
        if user in connectedUsers:
            connectedUsers.remove(user)

    def _messageHandler(self, user: User):
        while True:
            try:
                msg = user.getMessage()
            except:
                self.removeUser(user)
                break

            for userConnection in connectedUsers:
                if user == userConnection:
                    continue
                try:
                    userConnection.sendMessage(msg)
                except:
                    self.removeUser(userConnection)


class Chat(Thread):
    def __init__(self, host='0.0.0.0', port=5555, max_users=20):
        Thread.__init__(self)
        self._socket = socket()
        self._socket.bind((host, port))
        self._socket.listen(max_users)

        self._messageHandler = MessageHandler()
        self._connectUsers = ConnectUsers(self._socket, self._messageHandler)

    def run(self):
        self._connectUsers.start()
        while True:
            pass

    def __del__(self):
        self._socket.close()


chat = Chat()
chat.start()
