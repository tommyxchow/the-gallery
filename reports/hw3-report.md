# Homework 3 Report

## Objective 1

I used the provided form HTML inside my homepage(index.html). In server&#46;py, I created a new if statement to catch the POST request. To get the content length and boundary, I created a function in functions&#46;py called "formatRequest" which takes the request, parses the headers appropriately, and returns a dictionary of headers to values.

To get the entire form, I have a while-loop which keeps receiving the bytes and adds them into a buffer. Once the content length matches the buffer length, the while-loop stops.

In functions&#46;py, I have a function called "parseMultipart" which takes the buffer and boundary and parses the multipart/form-data block. This returns a dictionary of form input names to their respective values.

I escape the HTML, I have a function called "escapeHTML" that simply takes a string and replaces the important HTML characters.

## Objective 2

To host all the comments, I have them already stored in a dictionary of names to comments. Once the homepage loads, I loop through the dictionary and put the comments in the HTML line-by-line under the comments section.

The HTML is already escaped when the comments are stored.

## Objective 3

I used the provided HTML form for image uploads in my homepage. I use the same parsing function from objective 1 to get the filename, binary image, and caption. I then write the image into the image folder, which contains all the public images that can be accessed by /image/<image_name>.jpg.

To prevent users from accessing files from other directories, I have conditionals and presets that only allow files to be accessed from the image folder (the python file open has "image/" that prepends the image name). Furthermore, if a user requests a url like /image/~/.ssh/id_rsa, I only look past the right-most "/" for the image name, so the resulting request will be /image/id_rsa. Obviously, this file won't exist on the system so a 404 will be returned.

## Objective 4

To host all the images, I have the uploaded images stored in a dictionary of filename to caption. In the HTML template, I add all the captions as buttons and associate each button with the filename. When the button is clicked, the "loadImage" function in functions.js loads the image from the /image path.

Any captions also have their HTML escaped already inside the "parseMultipart" function.

## Bonus Objective

Every time the homepage is loaded, a random float is generated as the token. This token is then stored into a list containing all valid tokens. When an image or comment is submitted, the token is checked against the valid tokens, proceeding if it is in the list and returning an error if it is not.
