newHTML = []
images = ["cat", "dog", "sheep"]

with open("images.html", "r") as file:
    r = file.readlines()
    for line in r:
        if line.find("{{name}}") != -1:
            newHTML.append(line.replace("{{name}}", "Mitch"))
        elif line.find("{{loop}}") != -1:
            for image in images:
                newHTML.append("<img src=" + image + ">\n")
        else:
            newHTML.append(line)


print("".join(newHTML))