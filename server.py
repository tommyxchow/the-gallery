import secrets
import socketserver
import functions as response
import random
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
    comments = {}
    uploadedImages = {}
    tokens = []
    client_sockets = []
    homeMessage = [None]
    loginToken = []
    

    def handle(self):
        # Receive the next message, decode, and split.
        req = self.request.recv(1024)
        message = req.decode().split('\r\n')

        # Get the request type & path
        requestLine = message[0].split(' ')
        requestType = requestLine[0]
        path = requestLine[1]

        mappings = response.formatRequest(message)

        if requestType == "POST":
            contentLength = int(mappings['Content-Length'])
            boundary = mappings['Content-Type'][1][mappings['Content-Type'][1].find('=')+1:]
            contentBuffer = bytes()


            # Keep receiving until we get all the content
            while len(contentBuffer) <= contentLength:
                if len(contentBuffer) > 0:
                    req = self.request.recv(1024)
                    contentBuffer += req
                elif '\r\n\r\n'.encode() in req and len(contentBuffer) == 0:
                    contentBuffer += req[req.find('\r\n\r\n'.encode())+2:]
                else:
                    req = self.request.recv(1024)

            contentBuffer = contentBuffer.strip()

            if path == "/comment":
                formValues = response.parseMultipart(contentBuffer, boundary)
                if formValues['token'] in self.tokens:
                    self.comments[formValues['name']] = formValues['comment']
                    self.tokens.remove(formValues['token'])
                    self.request.sendall(response.buildResponse301('/'))

            elif path == "/image-upload":
                data = response.parseMultipart(contentBuffer, boundary)
                if data['token'] in self.tokens:
                    self.uploadedImages[data['filename']] = data['name']
                    with open('image/' + data['filename'], "wb") as f:
                        f.write(data['upload'])
                    self.tokens.remove(data['token'])
                    self.request.sendall(response.buildResponse301('/'))

            elif path == '/register':
                formValues = response.parseMultipart(contentBuffer, boundary)
                username = formValues['username']
                password = formValues['password']

                if response.passwordCheck(password):

                    salt = bcrypt.gensalt()
                    password = bcrypt.hashpw(password.encode(), salt)
                    newUser = {'username': username, 'password': password, 'token': None}

                    self.users.insert_one(newUser)
                    
                    self.homeMessage[0] = 'Registered!'

                    self.request.sendall(response.buildResponse301('/'))
                else:
                    self.homeMessage[0] = 'Password not acceptable'
                    self.request.sendall(response.buildResponse301('/register'))


            elif path == '/login':
                formValues = response.parseMultipart(contentBuffer, boundary)

                username = formValues['username']
                password = formValues['password']

                getUser = self.users.find_one({'username': username})

                if getUser != None:
                    if bcrypt.checkpw(password.encode(), getUser['password']):
                        token = secrets.token_hex(22)
                        hashedToken = hashlib.sha256(token.encode()).hexdigest()
                        
                        self.loginToken.append(token)

                        self.users.update_one({'username': username}, {'$set': {'token': hashedToken}})


                        self.homeMessage[0] = f'You logged in as {username}'
                        self.request.sendall(response.buildResponse301('/'))
                    else:
                        self.homeMessage[0] = 'Login failed'
                        self.request.sendall(response.buildResponse301('/login'))
                else:
                    self.homeMessage[0] = 'User does not exist'
                    self.request.sendall(response.buildResponse301('/login'))


            self.request.sendall(response.buildResponse403("text/plain", "Invalid token!"))

        elif requestType == "GET":

            if path == "/":
                    
                setCookies = ''
                currentToken = None

                visited = None
                if 'Cookie' in mappings:
                    # If there is only a single cookie
                    if type(mappings['Cookie']) == str:
                        visited = mappings['Cookie'][mappings['Cookie'].find('=')+1:]
                    # If there are multiple cookies (a list of cookies)
                    else:
                        for cookie in mappings['Cookie']:
                            if 'visited' in cookie:
                                visited = cookie[cookie.find('=')+1:]
                            elif 'token' in cookie:
                                currentToken = cookie[cookie.find('=')+1:]
                        if visited == None:
                            setCookies = 'Set-Cookie: visited=true'
                else:
                    setCookies = 'Set-Cookie: visited=true'
                                
                welcome_message = 'Welcome!'
                if visited == 'true':
                    welcome_message = 'Welcome Back!'

                if self.loginToken:
                    setCookies = f'Set-Cookie: token={self.loginToken[0]}'
                    self.loginToken = []

                if currentToken:
                    hashedToken = hashlib.sha256(currentToken.encode()).hexdigest()
                    getUser = self.users.find_one({'token': hashedToken})
                    if getUser:
                        self.homeMessage[0] = f'You are logged in as {getUser["username"]}'
                    else:
                        self.homeMessage[0] = 'Invalid login token'


                htmlString = []
                with open("static/index.html", "r") as file:

                    r = file.readlines()

                    for line in r:
                        if line.find('{{welcome}}') != -1:
                            htmlString.append(f'<h1>{welcome_message}</h1>')

                        elif line.find("{{buttonLoop}}") != -1:
                            for imageName in self.uploadedImages:
                                if len(self.uploadedImages[imageName]) > 0:
                                    newButton = "<button id = {0} onclick = 'loadImage(id)'>{1}</button>".format(imageName, self.uploadedImages[imageName])
                                    htmlString.append(newButton)
                                else:
                                    newButton = "<button id = {0} onclick = 'loadImage(id)'>{1}</button>".format(imageName, imageName)
                                    htmlString.append(newButton)
                        elif line.find("{{commentLoop}}") != -1:
                            for name in self.comments:
                                newComment = "<p>{0} said {1}</p>".format(name, self.comments[name])
                                htmlString.append(newComment)
                        # Generate random token
                        elif line.find("token") != -1:
                            newToken = random.random()
                            self.tokens.append(str(newToken))
                            token = '<input hidden id="random-token" type="text" name="token" value={}>'.format(newToken)
                            htmlString.append(token)
                        elif '{{message}}' in line:
                            if self.homeMessage[0] != None:
                                htmlString.append(f'<h1>{self.homeMessage[0]}</h1><br>')
                                self.homeMessage[0] = None
                        else:
                            htmlString.append(line)

                buildString = "".join(htmlString)

                self.request.sendall(response.buildResponse200("text/html", len(buildString), buildString, setCookies))

            elif path =='/register':

                htmlString = []
                with open("static/register.html", "r") as file:
                    r = file.readlines()
                    for line in r:
                        if '{{message}}' in line:
                            if self.homeMessage[0] != None:
                                htmlString.append(f'<h1>{self.homeMessage[0]}</h1><br>')
                                self.homeMessage[0] = None
                        else:
                            htmlString.append(line)

                buildString = "".join(htmlString)
                self.request.sendall(response.buildResponse200("text/html", len(buildString), buildString))

            elif path == '/login':

                htmlString = []
                with open("static/login.html", "r") as file:
                    r = file.readlines()
                    for line in r:
                        if '{{message}}' in line:
                            if self.homeMessage[0] != None:
                                htmlString.append(f'<h1>{self.homeMessage[0]}</h1><br>')
                                self.homeMessage[0] = None
                        else:
                            htmlString.append(line)

                buildString = "".join(htmlString)
                self.request.sendall(response.buildResponse200("text/html", len(buildString), buildString))

            elif path == '/websocket':
                
                webSocketKey = mappings['Sec-WebSocket-Key'] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
                sha1Hash = hashlib.sha1(webSocketKey.encode()).digest()
                webSocketAccept = base64.b64encode(sha1Hash).decode()

                self.request.sendall(response.buildResponse101(webSocketAccept))

                self.client_sockets.append(self.request)

                for msg in self.collection.find({}, {'_id': False}):
                    self.request.sendall(response.buildWSFrame(json.dumps(msg).encode()))

                try:
                    while True:
                        received_data = self.request.recv(1024)

                        binaryList = []
                        
                        # Convert received message to binary
                        for i in received_data:
                            binaryList.append(format(i, 'b').zfill(8))

                        opcode = int(str(binaryList[0][4:]), 2)

                        # Only handle opcode 1
                        if opcode == 1:
                            # Get appropriate metadata
                            mask = int(binaryList[1][0])
                            maskingKey = None
                            payloadLength = int(str(binaryList[1][1:]), 2)
                            payloadData = ''.join(binaryList[6:])

                            # If the masking bit is set, get the masking key
                            if mask == 1:
                                maskingKey = ''.join(binaryList[2:6])

                            # If payload is 126, get the extended length, update masking key, update payload
                            if payloadLength == 126:
                                payloadLength == int(''.join(binaryList[2:4]), 2)
                                maskingKey = ''.join(binaryList[4:8])
                                payloadData = ''.join(binaryList[8:])

                            # Unmask the payload to get the binary representation of the message
                            # Can also get 4 bytes of the mask in an array and mod 4 for every byte
                            binaryPayload = ''
                            for i, elem in enumerate(payloadData):
                                maskIndex = i % 32
                                binaryPayload += str(int(maskingKey[maskIndex]) ^ int(elem))

                            # Convert the binary message to an encoded byte array
                            finalMessage = bytearray()
                            buffer = ''
                            n = 0
                            for i in binaryPayload:
                                buffer += i
                                n += 1
                                if n == 8:
                                    char = [int(buffer, 2)]
                                    # Escape any HTML characters
                                    if char[0] == 38:
                                        char = [38, 97, 109, 112]
                                    elif char[0] == 60:
                                        char = [38, 108, 116]
                                    elif char[0] == 62:
                                        char = [38, 103, 116]
                                    finalMessage.extend(char)
                                    n = 0
                                    buffer = ''

                            # Insert JSON message into the database
                            self.collection.insert_one(json.loads(finalMessage.decode()))

                            # Send the frame to each socket
                            for r in self.client_sockets:
                                r.sendall(response.buildWSFrame(finalMessage))

                except:
                    # Close the database and remove the connection
                    self.client.close()
                    self.client_sockets.remove(self.request)
                    pass

            elif path == "/functions.js":
                with open("functions.js", "r") as file:
                    r = file.read()
                    self.request.sendall(response.buildResponse200("text/javascript", len(r), r))

            elif path == "/style.css":
                with open("static/style.css", "r") as file:
                    r = file.read()
                    self.request.sendall(response.buildResponse200("text/css", len(r), r))

            elif path == "/utf.txt":
                with open("static/utf.txt", "rb") as file:
                    r = file.read()
                    self.request.sendall(response.buildResponseBinary("text/plain; charset=utf-8", r))

            elif path[0:7] == "/image/":
                try:
                    image = path[path.rfind('/'):]
                    with open("image" + image, "rb") as file:
                        r = file.read()
                        self.request.sendall(response.buildResponseBinary("image/jpeg", r))
                        
                except Exception:
                    self.request.sendall(response.buildResponse404("text/plain", "Image not found :("))

            elif path[0:8] == "/images?":

                try:
                    htmlString = []
                    keyValues = response.queryToDictionary(path)

                    with open("static/images.html", "r") as file:
                        r = file.readlines()
                        for line in r:
                            if line.find("{{name}}") != -1:
                                htmlString.append(line.replace("{{name}}", keyValues["name"][0]))
                            elif line.find("{{loop}}") != -1:
                                for image in keyValues["images"]:
                                    htmlString.append("<img src=/image/" + image + ".jpg >\n")
                            else:
                                htmlString.append(line)
                    
                    buildString = "".join(htmlString)

                    self.request.sendall(response.buildResponse200("text/html", len(buildString), buildString))

                except Exception:
                    self.request.sendall(response.buildResponse404("text/plain", "An image not found :("))

            elif path == "/hello":
                responseMessage = "Welcome, World! :)"
                self.request.sendall(response.buildResponse200("text/plain", len(responseMessage), responseMessage))

            # 301 Redirect
            elif path == "/hi":
                self.request.sendall(response.buildResponse301("/hello"))

            # Return 404
            else:
                self.request.sendall(response.buildResponse404("text/plain", "Content not found :("))


def main():
    host = "app"
    port = 8000

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
