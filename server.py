import socketserver
import sys
import functions as response

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        message = self.request.recv(1024).strip().decode().split('\r\n')
        path = response.getRequestPath(message[0])
        
        print("REQUEST --- ", message)

        if path == "/":
            with open("index.html", "r") as file:
                r = file.read()
                self.request.sendall(response.buildResponse200("text/html", len(r), r))
        
        elif path == "/functions.js":
            with open("functions.js", "r") as file:
                r = file.read()
                self.request.sendall(response.buildResponse200("text/javascript", len(r), r))

        elif path == "/style.css":
            with open("style.css", "r") as file:
                r = file.read()
                self.request.sendall(response.buildResponse200("text/css", len(r), r))

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
                print("No image")
                self.request.sendall(response.buildResponse404("text/plain", "Content not found :("))


        elif path[0:6] == "/image":
            try:
                image = path[path.rfind('/'):]
                with open("image" + image, "rb") as file:
                    r = file.read()
                    self.request.sendall(response.buildResponseBinary("image/jpeg; charset=utf-8", r))
                    
            except FileNotFoundError:
                self.request.sendall(response.buildResponse404("text/plain", "Content not found :("))

        elif path == "/utf.txt":
            with open("utf.txt", "rb") as file:
                r = file.read()
                self.request.sendall(response.buildResponseBinary("text/plain; charset=utf-8", r))

        elif path == "/hello":
            message = "Welcome, World! :)"
            self.request.sendall(response.buildResponse200("text/plain", len(message), message))

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