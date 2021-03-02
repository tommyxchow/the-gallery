test = "/images?images=cat+kitten+dog&name=Mitch"
htmlString = []

split = test[test.find("?")+1:].split("&")
print(split)
print(split[0].split('='))
print(split[0].split('+'))

htmlString.append("<html>")

#get name
for pair in split:
    if pair.find("name") == 0:
        name = pair[pair.find("=")+1:]
        htmlString.append("<h1>" + name + "</h1>")

#get pics
for pair in split:
    if pair.find("images") == 0:
        requestedImages = pair[pair.find("=")+1:].split("+")

        for image in requestedImages:
            htmlString.append("<img src=image/" + image + ".jpg />")

htmlString.append("</html>")

