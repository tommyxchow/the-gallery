# Homework 1 Report

For this assignment, I decided to use python's socket library rather than the socketserver framework shown in lecture. I believed that if I started from "scratch" and worked my way up through objectives, I'd gain an overall better understanding of the ins and outs of socket programming. In the end, this decision definitely paid off as it helped me clarify quite a bit of the mystery surrounding sockets and basic web programming. Although, in the future I'll likely switch to the sockerserver style shown in lecture for the multi-threading support mentioned by Jesse.

My homework consists of two python files:

- `server.py`, where all the sockets, connections, and messages are handled.
- `functions.py`, where there are a few separate helper functions that:
  - get the path from a request, and
  - build 200, 301, and 404 responses.

## server&#46;py

The layout/steps in this file consists of creating a socket, binding a host to a port in the socket, setting it to listen mode, and then entering a while loop. In this loop, the program accepts any incoming connections, decodes and organizes the request and its contents accordingly, sends back a response based on the received path, and finally closes the connection to get ready for the next connection.

## functions&#46;py

There are a couple of helper functions in this file. The first one, getRequestPath, accepts a GET request string as an argument and returns the path. The next three functions, buildResponse200, buildResponse301, and buildResponse404, accept arguments for the content and content type (or path only for the 301 redirect) to build the appropriate encoded response.
