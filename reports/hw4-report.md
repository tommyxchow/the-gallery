# Homework 4 Report

WebSocket: lines 103-187

Client/Request Data Structure: line 21

Database Initialization: lines 12-15

## Objective 1

### Files: functions.js

For objective 1, I simply added the provided code on lines 1-2.

### Files: server&#46;py, functions&#46;py

On line 103, I created a path for '/websocket'. On lines 105 to 107, I generated the WebSocket accept using Python's hashlib and base64 library.

On lines 33-35 In functions&#46;py, I created the function 'buildResponse101' that takes a WebSocket accept key and builds a 101 (WebSocket) response with the connection, upgrade, and key headers.

Finally on line 109, I send the 101 response and the connection is established.

## Objective 2

### Files: functions.js

I added the provided JavaScript code on lines 1-36.

### Files: sever&#46;py, functions&#46;py

I created while loop that starts on line 118. The code in this block essentially:

1. Gets the 1024 received bytes and converts it into a binary array
2. Gets the mask, masking key, payload length, and payload data by slicing
3. Loops through the binary payload and unmasks each bit
4. Loops through the unmasked payload, escapes HTML, and converts to an encoded byte array
5. Stores the message in the database
6. Builds the WebSocket frame and sends it to every stored connection.

To keep track of all the clients, in line 111 I add the request info to an array in line 21. Therefore, the message can be sent to every client in the list. If the client closes the tab, they are removed from the list on line 186 in the except block.

To build a frame, I created the function 'buildWSFrame' in functions&#46;py on lines 117-143. This function takes the payload, gets its length, sets all the appropriate bits, and returns the byte array to respond with.

## Objectives 3 and 4

### Files: server&#46;py

For the database, I used mongoDB by installing the community edition and importing pymongo. When the WebSocket connection is initialized, on lines 114-115 I loop through all the messages in the database and send them to the client, allowing the client to see all past messages.

To store the messages in the database, I add the JSON formatted message to the database on line 176.

### Files: Dockerfile, docker-compose.yml, requirements.txt

In my docker compose file, I followed the lecture example, adding mongoDB and the app itself. I also added the provided docker compose wait in the dockerfile.

In order to have pymongo work in the container, I created the requirements.txt file and added pymongo to it. Then in the dockerfile, I added the command to install all the dependencies in requirements.txt.

## Bonus objective was not done
