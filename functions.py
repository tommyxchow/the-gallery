# encode string into a byte array and ship it
def buildResponse200(mimeType, length, content, options=''):
    if options != '':
        options += '\r\n'
    httpResponse = f'HTTP/1.1 200 OK\r\nContent-Type: {mimeType}\r\nContent-Length: {length}\r\n{options}X-Content-Type-Options: nosniff\r\n\r\n{content}'

    return httpResponse.encode()


def buildResponse301(path):
    httpResponse = "HTTP/1.1 301 Moved Permanently\r\nLocation: {}\r\nX-Content-Type-Options: nosniff\r\n\r\n".format(path)

    return httpResponse.encode()


def buildResponse403(mimeType, errorMessage):
    httpResponse = "HTTP/1.1 403 Forbidden\r\nContent-Type: {}\r\nContent-Length: {}\r\nX-Content-Type-Options: nosniff\r\n\r\n{}\r\n\r\n".format(mimeType, len(errorMessage), errorMessage)

    return httpResponse.encode()


def buildResponse404(mimeType, errorMessage):
    httpResponse = "HTTP/1.1 404 Not Found\r\nContent-Type: {}\r\nContent-Length: {}\r\nX-Content-Type-Options: nosniff\r\n\r\n{}\r\n\r\n".format(mimeType, len(errorMessage), errorMessage)

    return httpResponse.encode()


def buildResponseBinary(mimeType, bArray):
    httpResponse = "HTTP/1.1 200 OK\r\nContent-Type: {}\r\nContent-Length: {}\r\nX-Content-Type-Options: nosniff\r\n\r\n".format(mimeType, len(bArray))

    httpResponse = httpResponse.encode() + bArray

    return httpResponse

def buildResponse101(webSocketAccept):
    httpResponse = "HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Accept:{}\r\n\r\n".format(webSocketAccept)
    return httpResponse.encode()


def queryToDictionary(path):
    if path.find("=") != -1:
        kv = {}
        split = path[path.find("?")+1:].split("&")
        for pair in split:
            splitEquals = pair.split("=")
            for keyValue in splitEquals:
                splitPlus = keyValue.split("+")
                kv[splitEquals[0]] = splitPlus

        return kv


def formatRequest(requestArray):
    kv = {}
    for i in range(1, len(requestArray)):
        keyEnd = requestArray[i].find(":")
        key = requestArray[i][0:keyEnd]
        value = requestArray[i][keyEnd+2:]

        if ';' in value:
            value = value.split(';')
        kv[key] = value
    return kv


def escapeHTML(string):
    newString = string.replace('&', '&amp')
    newString = newString.replace('<', '&lt')
    newString = newString.replace('>', '&gt')

    return newString


def escapeDIR(string):
    newString = string.replace('.', '')
    newString = newString.replace('/', '')
    newString = newString.replace('~', '')

    return newString


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
                    name = pair[pair.find('=')+1:].strip('"')

                    if name == "upload":
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

def buildWSFrame(payload):
    responseFrame = bytearray()
    payloadLength = len(payload)
    print(payloadLength)

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

    print(len(responseFrame))

    return responseFrame

def passwordCheck(password: str):
    specialCharacters = " !\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
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