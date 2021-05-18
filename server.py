import secrets
import socketserver
import functions as helpers
import hashlib
import base64
import pymongo
import json
import bcrypt


class MyTCPHandler(socketserver.BaseRequestHandler):

    # Initialize the database
    client = pymongo.MongoClient('mongo')
    db = client['websocket']
    collection = db['chat']
    users = db['users']

    # Initialize data structures
    comments = []
    uploadedImages = {}
    tokens = []
    client_sockets = []
    homeMessage = ''
    loginToken = []

    def handle(self):
        # Receive the next message, decode, and split it into an array.
        req = self.request.recv(2048)
        message = req.split('\r\n'.encode())

        # Retrieve the request type and request path.
        requestLine = message[0].decode().split(' ')
        requestType = requestLine[0]
        path = requestLine[1]

        mappings = helpers.formatRequest(message)

        if requestType == 'POST':
            contentLength = int(mappings['Content-Length'])
            boundary = mappings['Content-Type'][1].split('=')[1]
            contentBuffer = mappings['buffer']

            # Keep receiving bytes and add them to the buffer until we get all the content.
            while len(contentBuffer) < contentLength:
                if len(contentBuffer) > 0:
                    req = self.request.recv(1024)
                    contentBuffer += req
                elif '\r\n\r\n'.encode() in req and len(contentBuffer) == 0:
                    contentBuffer += req[req.find('\r\n\r\n'.encode())+2:]
                else:
                    req = self.request.recv(1024)

            formValues = helpers.parseMultipart(contentBuffer, boundary)

            if path == '/comment':
                if formValues['token'] not in self.tokens:
                    self.request.sendall(helpers.buildResponse403('text/plain', 'Invalid token!'))
                    return
                self.comments.append((formValues['name'], formValues['comment']))
                self.tokens.remove(formValues['token'])
                self.request.sendall(helpers.buildResponse301('/'))

            elif path == '/image-upload':
                if formValues['token'] not in self.tokens:
                    self.request.sendall(helpers.buildResponse403('text/plain', 'Invalid token!'))
                    return
                self.uploadedImages[formValues['filename']] = formValues['name']
                with open('image/' + formValues['filename'], 'wb') as f:
                    f.write(formValues['upload'])
                self.tokens.remove(formValues['token'])
                self.request.sendall(helpers.buildResponse301('/'))

            elif path == '/register':
                username = formValues['username']
                password = formValues['password']

                if self.users.count_documents({'username': username}) == 0:
                    if helpers.passwordCheck(password) and self.users.count_documents({'username': username}) == 0:
                        salt = bcrypt.gensalt()
                        password = bcrypt.hashpw(password.encode(), salt)
                        newUser = {'username': username, 'password': password, 'token': None}
                        self.users.insert_one(newUser)
                        MyTCPHandler.homeMessage = 'Registered!'
                        self.request.sendall(helpers.buildResponse301('/'))
                    else:
                        MyTCPHandler.homeMessage = 'Password not acceptable'
                        self.request.sendall(helpers.buildResponse301('/register'))
                else:
                    MyTCPHandler.homeMessage = 'User already registered'
                    self.request.sendall(helpers.buildResponse301('/register'))

            elif path == '/login':
                username = formValues['username']
                password = formValues['password']

                getUser = self.users.find_one({'username': username})

                if getUser:
                    if bcrypt.checkpw(password.encode(), getUser['password']):
                        token = secrets.token_hex(22)
                        hashedToken = hashlib.sha256(token.encode()).hexdigest()

                        self.loginToken.append(token)

                        self.users.update_one({'username': username}, {'$set': {'token': hashedToken}})

                        MyTCPHandler.homeMessage = f'You are logged in as {username}'
                        self.request.sendall(helpers.buildResponse301('/'))
                    else:
                        MyTCPHandler.homeMessage = 'Login failed'
                        self.request.sendall(helpers.buildResponse301('/login'))
                else:
                    MyTCPHandler.homeMessage = 'User does not exist'
                    self.request.sendall(helpers.buildResponse301('/login'))

        elif requestType == 'GET':
            if path == '/':
                setCookies = ''
                currentToken = None

                visitedBefore = None
                if 'Cookie' in mappings:
                    # If there is only a single cookie
                    if type(mappings['Cookie']) == str:
                        visitedBefore = mappings['Cookie'][mappings['Cookie'].find('=')+1:]
                    # If there are multiple cookies (a list of cookies)
                    else:
                        for cookie in mappings['Cookie']:
                            if 'visited' in cookie:
                                visitedBefore = cookie[cookie.find('=')+1:]
                            elif 'token' in cookie:
                                currentToken = cookie[cookie.find('=')+1:]
                        if not visitedBefore:
                            setCookies = 'Set-Cookie: visited=true'
                else:
                    setCookies = 'Set-Cookie: visited=true'

                welcomeMessage = 'Welcome!'
                if visitedBefore == 'true':
                    welcomeMessage = 'Welcome Back!'

                if self.loginToken:
                    setCookies = f'Set-Cookie: token={self.loginToken[0]}'
                    currentToken = self.loginToken[0]
                    self.loginToken = []

                if currentToken and not self.homeMessage:
                    hashedToken = hashlib.sha256(currentToken.encode()).hexdigest()
                    getUser = self.users.find_one({'token': hashedToken})
                    if getUser:
                        MyTCPHandler.homeMessage = f'You are logged in as {getUser["username"]}'
                    else:
                        MyTCPHandler.homeMessage = 'Invalid login token'

                home = helpers.renderPage('home', self, MyTCPHandler, welcomeMessage)

                self.request.sendall(helpers.buildResponse200('text/html', len(home), home, setCookies))

            elif path == '/register':
                register = helpers.renderPage('register', self, MyTCPHandler)
                self.request.sendall(helpers.buildResponse200('text/html', len(register), register))

            elif path == '/login':
                login = helpers.renderPage('login', self, MyTCPHandler)
                self.request.sendall(helpers.buildResponse200('text/html', len(login), login))

            elif path == '/websocket':
                # WebSocket handshake
                webSocketKey = mappings['Sec-WebSocket-Key'] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
                sha1Hash = hashlib.sha1(webSocketKey.encode()).digest()
                webSocketAccept = base64.b64encode(sha1Hash).decode()

                self.request.sendall(helpers.buildResponse101(webSocketAccept))
                self.client_sockets.append(self.request)

                for msg in self.collection.find({}, {'_id': False}):
                    self.request.sendall(helpers.buildWSFrame(json.dumps(msg).encode()))

                helpers.socketConnection(self)

            elif path[0:7] == '/image/':
                try:
                    image = path[path.rfind('/'):]
                    with open('image' + image, 'rb') as file:
                        r = file.read()
                        self.request.sendall(helpers.buildResponseBinary('image/jpeg', r))

                except Exception:
                    self.request.sendall(helpers.buildResponse404('text/plain', 'Image not found :('))

            elif path == '/functions.js':
                with open('functions.js', 'r') as file:
                    r = file.read()
                    self.request.sendall(helpers.buildResponse200('text/javascript', len(r), r))

            elif path == '/style.css':
                with open('static/style.css', 'r') as file:
                    r = file.read()
                    self.request.sendall(helpers.buildResponse200('text/css', len(r), r))

            elif path == '/utf.txt':
                with open('static/utf.txt', 'rb') as file:
                    r = file.read()
                    self.request.sendall(helpers.buildResponseBinary('text/plain; charset=utf-8', r))

            else:
                self.request.sendall(helpers.buildResponse404('text/plain', 'Content not found :('))


def main():
    host = 'app'
    port = 8000

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
