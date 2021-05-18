# The Gallery

The Gallery is a **deceptively basic** web application that consists of the following features:

- **Image Uploads**: Upload images to be displayed through a button on the homepage (multipart/form-data).
- **Commenting**: Post public comments through a form (multipart/form-data).
- **Chat**: A live persistent chat that allows you to communicate with other users (WebSockets, MongoDB).
- **Authentication**: Register and login with token-based authentication (bcrypt).

The Gallery is also the culmination of a series of homework assignments I completed during Spring 2021 in the course [CSE 312](https://cse312.com) at the University at Buffalo.

## Deceptive...?

Aside from Python's socketserver to handle TCP connections, this project was accomplished with **zero frameworks** and minimal necessary libraries. This decision was made in an effort to learn the ins-and-outs of certain protocols and backend web development.

This also means that

- Building HTTP Responses (101, 200, 301, 403, 404, binary)
- Parsing HTTP headers and multipart/form-data encoding
- WebSocket handshake, parsing and building WebSocket frames
- Server-side rendering of HTML web pages
- Storing and sending cookies and tokens

And more were all completed manually (with much help from RFCs).

## Additional Info

The reports folder contains reports of my progress and thought process but many parts describing the code are outdated.

Much of the code and features are rudimentary and can be greatly improved upon, but I've decided to leave it as is in an effort to work on other projects.

The project can be deployed locally using with Docker using `docker-compose up --build` and then navigating to <http://localhost:8080>

Thank you for reading!
