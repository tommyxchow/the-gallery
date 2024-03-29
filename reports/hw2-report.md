# Homework 2 Report

## Objective 1

Files are index.html, style.css, and functions.js located in the root
directory (different from sample site for bonus).

I added the appropriate statements to handle the path to these files
in server&#46;py. I open, read, and send a 200 response that contains the
appropriate mime type, length, and contents.

## Objective 2

Provided utf.txt file is located in the root directory.

To handle the utf-8 encodings, I created a new function in functions&#46;py
named "buildResponseBinary". This function builds a response, encodes it,
and appends the binary array content to the end.

## Objective 3

Provided images located in the image folder.

In server&#46;py I set an elif statement to catch /image/ in the path and get the
requested image. I then respond with the requested image and return an error
if it doesn't exist.

Like in objective 2, using the buildResponseBinary function in functions&#46;py
I build the response and append the binary array image and send it.

## Objective 4

In server&#46;py, I set an elif statement to catch /images? in the path. In
functions&#46;py I have a function "queryToDictionary" that reads the query
string and parses the key values into a dictionary.

I created images.html, which is a simple html template that has a name
placeholder and a loop area to signify where to place the images.

As the html file is read, the placeholders and images are inserted
into the appropriate areas using find and replace. The final html
will be added to and stored into the htmlString array, which will
be joined into a string sent as the response.

## Bonus Objective

I created a new index.html which shows a small art gallery. There are buttons
which allow the user to click and display a desired image.

In functions.js I have a function "loadImage" that gets the id of the desired
image and puts it in the main view.

In style.css, I assigned custom colors to each element like the buttons.
I created a border for the image, and added a gap between the buttons
and pictures.
