# The Gallery

![Screenshot](/image/screenshot.jpg)

The Gallery is, quite literally, a basic web application.

Aside from Python's [socketserver](https://docs.python.org/3/library/socketserver.html) to handle TCP connections, this project was accomplished with **zero frameworks** and only the absolutely necessary libraries ([bcrypt](https://pypi.org/project/bcrypt/) for password-hashing and [pymongo](https://pymongo.readthedocs.io/en/stable/) for MongoDB). This decision was made in an effort to learn the foundations and ins-and-outs of certain protocols and backend web development.

This also means that

- building HTTP Responses (101, 200, 301, 403, 404, and binary),
- parsing HTTP headers and multipart/form-data encoding,
- the WebSocket handshake and parsing and building WebSocket frames,
- server-side rendering of HTML web pages,
- storing and sending cookies and tokens,

and more were all completed manually (with much help from RFCs).

## Features

The Gallery consists of the following features:

- **Image Uploads**: Upload images to be displayed through a button on the homepage (multipart/form-data).
- **Commenting**: Post public comments through a form (multipart/form-data).
- **Chat**: A live persistent chat that allows you to communicate with other users (WebSockets, MongoDB).
- **Authentication**: Register and login with token-based authentication (bcrypt).

## Additional Info

The `reports` folder contains reports of my progress and thought process but some parts describing the code may outdated.

Much of the code and features are rudimentary and can be **heavily** improved upon , but I've decided to leave it as is in order to work on other more meaningful projects.

The project can be deployed locally using with Docker using `docker-compose up --build` and then navigating to <http://localhost:8080>

Thank you for reading!
