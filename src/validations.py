# remove protocols from URLs
def removeProtocols(string: str):
    if string.find("htt") != -1:
        cleanUri = string.split('//')
        if cleanUri[0].find('http') != -1:
            cleanUri.pop(0)
            string = ".".join(cleanUri)
            return string

# remove www subdomain from urls
def removeWWW(string: str):
    if string.find('ww') != -1:
        cleanUri = string.split('.')
        if cleanUri[0].find('ww') != -1:
            cleanUri.pop(0)
            string = ".".join(cleanUri)
            return string