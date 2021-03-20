import socketserver
import sys
import functions as response

class MyTCPHandler(socketserver.BaseRequestHandler):

    #TO DO: do CSS and HTMl image formatting and captions. Test putting HTML inside the caption input. Double check security inputs. 
    #Fix the for loop caption handling stuff. (When uploading multiple images with no caption, weird things happen)

    comments = {}
    uploadedImages = {}

    def handle(self):
        req = self.request.recv(1024)
        message = req.decode().split('\r\n')
        print(message[0])

        path = response.getRequestPath(message[0])
        requestLine = message[0].split(' ')
        requestType = requestLine[0]

        mappings = response.formatRequest(message)

        if requestType == "POST":
                contentLength = int(mappings['Content-Length'])
                boundary = mappings['Content-Type'][mappings['Content-Type'].find('=')+1:]
                contentBuffer = bytes()

                #Keep recieving until we get all the content
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

                    self.comments[formValues['name']] = formValues['comment']

                    self.request.sendall(response.buildResponse301('/'))

                elif path == "/image-upload":

                    data = response.parseMultipart(contentBuffer, boundary)
                    
                    self.uploadedImages[data['filename']] = data['name']

                    with open('image/' + data['filename'] + '.jpg', "wb") as f:
                        f.write(data['upload'])
                    
                    self.request.sendall(response.buildResponse301('/'))
                    


        elif requestType == "GET":
        
            if path == "/":

                htmlString = []
                with open("index.html", "r") as file:
                    r = file.readlines()

                    for line in r:
                        if line.find("{{buttonLoop}}") != -1:
                            for imageName in self.uploadedImages:
                                newButton = "<button id = {} onclick = 'loadImage(id)'>{}</button>".format(imageName, imageName)
                                htmlString.append(newButton)
                        elif line.find("{{commentLoop}}") != -1:
                            for name in self.comments:
                                newComment = "<p>{} said {}</p>".format(name, self.comments[name])
                                htmlString.append(newComment)
                        else:
                            htmlString.append(line)

                buildString = "".join(htmlString)

                self.request.sendall(response.buildResponse200("text/html", len(buildString), buildString))  
            
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
                        
                except FileNotFoundError:
                    self.request.sendall(response.buildResponse404("text/plain", "Content not found :("))

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

                except FileNotFoundError:
                    self.request.sendall(response.buildResponse404("text/plain", "Content not found :("))

            elif path == "/hello":
                responseMessage = "Welcome, World! :)"
                self.request.sendall(response.buildResponse200("text/plain", len(responseMessage), responseMessage))

            #301 Redirect
            elif path == "/hi":
                self.request.sendall(response.buildResponse301("/hello"))

            #Return 404
            else:
                self.request.sendall(response.buildResponse404("text/plain", "Content not found :("))

def main():
    host = "0.0.0.0"
    port = 8000

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()