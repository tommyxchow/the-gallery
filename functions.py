def getRequestPath(requestString):
    end = requestString.rfind(' ')
    return requestString[4: end]

#encode string into a byte array and ship it
def buildResponse200(mimeType, length, content):
    httpResponse = "HTTP/1.1 200 OK\r\nContent-Type: {}\r\nContent-Length: {}\r\nX-Content-Type-Options: nosniff\r\n\r\n{}".format(mimeType, length, content)

    return httpResponse.encode()

def buildResponse301(path):
    httpResponse = "HTTP/1.1 301 Moved Permanently\r\nLocation: {}\r\nX-Content-Type-Options: nosniff\r\n\r\n".format(path)

    return httpResponse.encode()

def buildResponse404(mimeType, errorMessage):
    httpResponse = "HTTP/1.1 404 Not Found\r\nContent-Type: {}\r\nContent-Length: {}\r\nX-Content-Type-Options: nosniff\r\n\r\n{}\r\n\r\n".format(mimeType, len(errorMessage), errorMessage)

    return httpResponse.encode()

def buildResponseBinary(mimeType, bArray):
    httpResponse = "HTTP/1.1 200 OK\r\nContent-Type: {}\r\nContent-Length: {}\r\nX-Content-Type-Options: nosniff\r\n\r\n".format(mimeType, len(bArray))

    httpResponse = httpResponse.encode() + bArray

    return httpResponse

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