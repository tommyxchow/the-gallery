# Homework 5 Report

## Objective 1

When the user requests the home page (line 127), I check the headers to see if there is a cookie header available. To determine whether a user has visited the page before, I read and send the "visited=true" cookie.

If there are no cookies, the welcome message is set to the default "Welcome" message, and the "visited=true" cookie is set on the next response. If the "visited=true" cookie was received in the request, the welcome message is set to "Welcome Back!". This cookie will stay for all subsequent requests, so the user will receive the return message as long as the cookie exists.

## Objective 2 & 3

For the login and register forms, I used the multipart encoding since I already had all the relevant functions to parse it from previous homeworks.

When the user registers, the post request is sent to "/request" (line 74). Once received, the values are parsed and the username/password is retrieved, which are then stored into the "user" collection through MongoDB. The passwords are salted and hashed through the bcrypt library.

When the user logs in, the inputted username and password are parsed (line 95).
Then, I pull the record matching the username from MongoDB. If either there is no matching record or if bcrypt determines the provided password is invalid, an error message is displayed and the user is redirected.

## Objective 4

Whenever a user logs in, I use Python's "secrets" library to generate a random token of length 22 (line 105). This token is then hashed using SHA-256 and stored with the user in MongoDB. Then the user is redirected to the home page, where their token is set as a cookie. Now that the cookie is set, the user is authenticated and logged in for every subsequent request.

Every time the user visits the home page, the token is read from the cookie header.If the hashed version of this token matches the hashed version in the database, the name of the user with the associated token is displayed.

## Bonus

To check the passwords, I created a password checking function in "functions&#46;py" (line 151). This functions takes in a password and checks against all of the provided requirements. For the additional criteria, I chose to require that the first letter in the password is a capitalized letter.

When the password is parsed from the register form, the function is used to check the password. If the function returns False, the password does not meet the criteria and an error message will be shown.
