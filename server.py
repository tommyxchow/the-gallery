import socketserver
import functions as response
import random
import hashlib
import base64


class MyTCPHandler(socketserver.BaseRequestHandler):

    comments = {}
    uploadedImages = {}
    tokens = []
    # clients = []
    client_sockets = []

    def handle(self):
        # Recieve the next message, decode, and split.
        req = self.request.recv(1024)
        message = req.decode().split('\r\n')

        # Get the request type & path
        requestLine = message[0].split(' ')
        requestType = requestLine[0]
        path = requestLine[1]

        mappings = response.formatRequest(message)

        if requestType == "POST":
            contentLength = int(mappings['Content-Length'])
            boundary = mappings['Content-Type'][mappings['Content-Type'].find('=')+1:]
            contentBuffer = bytes()

            # Keep recieving until we get all the content
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

            self.request.sendall(response.buildResponse403("text/plain", "Invalid token!"))

        elif requestType == "GET":

            if path == "/":
                htmlString = []
                with open("index.html", "r") as file:
                    r = file.readlines()

                    for line in r:
                        if line.find("{{buttonLoop}}") != -1:
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
                        else:
                            htmlString.append(line)

                buildString = "".join(htmlString)

                self.request.sendall(response.buildResponse200("text/html", len(buildString), buildString))  

            elif path == '/websocket':
                
                webSocketKey = mappings['Sec-WebSocket-Key'] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
                sha1Hash = hashlib.sha1(webSocketKey.encode()).digest()
                webSocketAccept = base64.b64encode(sha1Hash).decode()

                self.request.sendall(response.buildResponse101(webSocketAccept))

                # client_id = self.client_address[0] + ':' + str(self.client_address[1])
                # self.clients.append(client_id)

                req = self.request
                self.client_sockets.append(req)
                print(self.client_sockets)

                try:
                    while True:
                        recieved_data = self.request.recv(1024)
                        print(recieved_data)

                        binaryList = []
                        
                        for i in recieved_data:
                            v = format(i, 'b').zfill(8)
                            binaryList.append(v)

                        finBit = binaryList[0][0]
                        print('FINBIT IS: ', finBit)
                        opcode = int(str(binaryList[0][4:]), 2)

                        if opcode == 1:
                            mask = int(binaryList[1][0])
                            maskingKey = None
                            payloadLength =int(str(binaryList[1][1:]), 2)
                            payloadData = ''.join(binaryList[6:])

                            if mask == 1:
                                maskingKey = ''.join(binaryList[2:6])

                            if payloadLength == 126:
                                print("PAYLOAD 126")
                                payloadLength == int(''.join(binaryList[2:4]), 2)
                                maskingKey = ''.join(binaryList[4:8])
                                payloadData = ''.join(binaryList[8:])
                            
                            elif payloadLength == 127:
                                print("PAYLOAD 127")
                                payloadLength = int(''.join(binaryList[2:10]), 2)
                                maskingKey = ''.join(binaryList[10:14])
                                payloadData = ''.join(binaryList[14:])

                            print('PAYLOAD LENGTH:', payloadLength)

                            # Can also get 4 bytes of the mask in an array and mod 4 for every byte
                            binaryPayload = ''
                            for i, elem in enumerate(payloadData):
                                maskIndex = i % 32
                                binaryPayload += str(int(maskingKey[maskIndex]) ^ int(elem))                            
                            
                            finalMessage = bytearray()
                            buffer = ''
                            n = 0
                            for i in binaryPayload:
                                buffer += i
                                n += 1
                                # Test for not divisible by 8
                                if n == 8:
                                    finalMessage.append(int(buffer, 2))
                                    n = 0
                                    buffer = ''
                                    
                            # for i in finalMessage:
                            #     print(format(i, 'b').zfill(8), end='')
                            
                            responseFrame = bytearray()

                            responseFrame.append(129)

                            print(len(finalMessage))

                            if payloadLength < 126:
                                responseFrame.append(len(finalMessage))
                                responseFrame += finalMessage
                            
                            elif payloadLength == 126:
                                responseFrame.append(126)
                                binaryLength = format(len(finalMessage), 'b').zfill(16)
                                byte1 = binaryLength[0:8]
                                byte2 = binaryLength[8:]

                                responseFrame.append(int(byte1, 2))
                                responseFrame.append(int(byte2, 2))
                                responseFrame += finalMessage


                            print("RESPONSE FRAME: ", responseFrame)
                            print('\n')

                            for r in self.client_sockets:
                                r.request.sendall(responseFrame)

                except:
                    pass

                

            
            elif path == "/functions.js":
                with open("functions.js", "r") as file:
                    r = file.read()
                    self.request.sendall(response.buildResponse200("text/javascript", len(r), r))

            elif path == "/style.css":
                with open("style.css", "r") as file:
                    r = file.read()
                    self.request.sendall(response.buildResponse200("text/css", len(r), r))

            elif path == "/utf.txt":
                with open("utf.txt", "rb") as file:
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

                    with open("images.html", "r") as file:
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
    host = "0.0.0.0"
    port = 8000

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
