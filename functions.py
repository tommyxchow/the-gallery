import random
import json


# Response builders
def buildResponse200(mimeType, length, content, options=''):
    if options != '':
        options += '\r\n'
    httpResponse = f'HTTP/1.1 200 OK\r\nContent-Type: {mimeType}\r\nContent-Length: {length}\r\n{options}X-Content-Type-Options: nosniff\r\n\r\n{content}'

    return httpResponse.encode()


def buildResponse301(path):
    httpResponse = f'HTTP/1.1 301 Moved Permanently\r\nLocation: {path}\r\nX-Content-Type-Options: nosniff\r\n\r\n'

    return httpResponse.encode()


def buildResponse403(mimeType, errorMessage):
    httpResponse = f'HTTP/1.1 403 Forbidden\r\nContent-Type: {mimeType}\r\nContent-Length: {len(errorMessage)}\r\nX-Content-Type-Options: nosniff\r\n\r\n{errorMessage}\r\n\r\n'

    return httpResponse.encode()


def buildResponse404(mimeType, errorMessage):
    httpResponse = f'HTTP/1.1 404 Not Found\r\nContent-Type: {mimeType}\r\nContent-Length: {len(errorMessage)}\r\nX-Content-Type-Options: nosniff\r\n\r\n{errorMessage}\r\n\r\n'

    return httpResponse.encode()


def buildResponseBinary(mimeType, bArray):
    httpResponse = f'HTTP/1.1 200 OK\r\nContent-Type: {mimeType}\r\nContent-Length: {len(bArray)}\r\nX-Content-Type-Options: nosniff\r\n\r\n'

    httpResponse = httpResponse.encode() + bArray

    return httpResponse


def buildResponse101(webSocketAccept):
    httpResponse = f'HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Accept:{webSocketAccept}\r\n\r\n'

    return httpResponse.encode()


# Response parsers
def formatRequest(requestArray):
    kv = {}
    for i in range(1, len(requestArray)):
        keyEnd = requestArray[i].decode().find(':')
        key = requestArray[i].decode()[0:keyEnd]
        if not key:
            kv['buffer'] = b'\r\n'.join(requestArray[i+1:])
            break
        value = requestArray[i].decode()[keyEnd+2:]

        if ';' in value:
            value = value.split(';')
        kv[key] = value
    return kv


def parseMultipart(buffer, boundary):
    boundary = '--' + boundary
    splitted = buffer.split('\r\n'.encode())
    keys = ['name', 'comment', 'username', 'password', 'token']

    kv = {}

    for i, line in enumerate(splitted):
        if line == boundary.encode():

            headers = splitted[i+1].decode().split('; ')
            for pair in headers:
                if ':' in pair:
                    key = pair[:pair.find(':')]
                    value = pair[pair.find(':')+2:]

                    kv[key] = value

                elif '=' in pair:
                    name = pair.split('=')[1].strip('"')

                    if name == 'upload':
                        # Put binary image into the dict
                        start = buffer.index('\r\n\r\n'.encode()) + 4
                        end = buffer.index(('\r\n' + boundary).encode())
                        kv[name] = buffer[start:end]

                        # Get content type into dict
                        contentType = splitted[i+2].decode()
                        contentType = contentType.split(': ')
                        kv[contentType[0]] = contentType[1]

                    elif name in keys:
                        kv[escapeHTML(name)] = escapeHTML(splitted[i+3].decode())

                    else:
                        key = pair[:pair.find('=')]
                        kv[key] = name

    return kv


# String escaping
def escapeHTML(string):
    newString = string.replace('&', '&amp')
    newString = newString.replace('<', '&lt')
    newString = newString.replace('>', '&gt')

    return newString


# Password verifier
def passwordCheck(password: str):
    specialCharacters = " !\'#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
    if not password:
        return False
    if not password[0].isupper():
        return False
    if len(password) < 8:
        return False
    if password.isupper():
        return False
    if password.islower():
        return False
    if not any(x.isdigit() for x in password):
        return False
    if not any(x in specialCharacters for x in password):
        return False
    return True


# HTML file rendering helper
def renderPage(page, self, MyTCPHandler, welcomeMessage=None):
    if page == 'home':
        htmlString = []
        with open('static/index.html', 'r') as file:

            r = file.readlines()

            for line in r:
                if '{{welcome}}' in line:
                    htmlString.append(f'<h1>{welcomeMessage}</h1>')

                elif '{{buttonLoop}}' in line:
                    for imageName in self.uploadedImages:
                        if len(self.uploadedImages[imageName]) > 0:
                            newButton = f'<button id={imageName} onclick="loadImage(id)">{self.uploadedImages[imageName]}</button>'
                            htmlString.append(newButton)
                        else:
                            newButton = f'<button id = {imageName} onclick = "loadImage(id)">{imageName}</button>'
                            htmlString.append(newButton)
                elif '{{commentLoop}}' in line:
                    for pair in self.comments:
                        newComment = f'<p>{pair[0]}: {pair[1]}</p>'
                        htmlString.append(newComment)
                # Generate random token
                elif 'token' in line:
                    newToken = random.random()
                    self.tokens.append(str(newToken))
                    token = f'<input hidden id="random-token" type="text" name="token" value={newToken}>'
                    htmlString.append(token)
                elif '{{message}}' in line:
                    if self.homeMessage:
                        htmlString.append(f'<h1>{self.homeMessage}</h1><br>')
                        MyTCPHandler.homeMessage = ''
                else:
                    htmlString.append(line)

        buildString = ''.join(htmlString)

        return buildString

    elif page == 'register' or page == 'login':
        htmlString = []
        with open(f'static/{page}.html', 'r') as file:
            r = file.readlines()
            for line in r:
                if '{{message}}' in line:
                    if self.homeMessage:
                        htmlString.append(f'<h1>{self.homeMessage}</h1><br>')
                        MyTCPHandler.homeMessage = ""
                else:
                    htmlString.append(line)

        buildString = ''.join(htmlString)

        return buildString


# WebSocket helpers
def buildWSFrame(payload):
    responseFrame = bytearray()
    payloadLength = len(payload)

    responseFrame.append(129)

    # For payload less than 126, just append the length
    if payloadLength < 126:
        responseFrame.append(len(payload))

    # For payload greater than 125, append the 2 length bytes
    else:
        responseFrame.append(126)
        binaryLength = format(len(payload), 'b').zfill(16)
        byte1 = binaryLength[0:8]
        byte2 = binaryLength[8:]

        responseFrame.append(int(byte1, 2))
        responseFrame.append(int(byte2, 2))

    # Append message byte array
    responseFrame += payload

    return responseFrame


def socketConnection(self):
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
                    r.sendall(buildWSFrame(finalMessage))

    except Exception:
        # Close the database and remove the connection
        self.client.close()
        self.client_sockets.remove(self.request)
        pass
