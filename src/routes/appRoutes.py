from starlette.responses import PlainTextResponse, RedirectResponse
from sonicOS import * 
from fastapi import FastAPI
from fastapi.params import Form, Path
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="views")

fwAddress = "192.168.1.250"

@app.get("/")
def index(request: Request):
    response = getCFSLists(fwAddress)
    return templates.TemplateResponse("index.html", {"request": request, "uriLists": response})

@app.get("/showcfslists")
def showLists(request: Request):
    response = getCFSLists(fwAddress)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("show_uri_list.html", {"request": request, "uriLists": response})

@app.get("/showcfslist/{name}")
def showList(request: Request, name: str = Path(...)):
    response = getSpecificCFSList(fwAddress, name)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("show_uri_list.html", {"request": request, "uriLists": response})

@app.post("/login")
def loginToAPI(request: Request, fwAddress: str = Form(...), fwUser: str = Form(...), fwPassword: str = Form(...)): 
    response = login(fwAddress, fwUser, fwPassword)
    if response.status_code == 200:
        return PlainTextResponse("Logado com sucesso!")
    else:
        return PlainTextResponse(f"Error: {response.text}")

@app.get("/logout")
def logoutFromAPI():
    response = logout(fwAddress)

    if response.status_code == 200:
        return PlainTextResponse("Logout realizado com sucesso!")
    else:
        return PlainTextResponse(f"Error {response.text}")

@app.post("/addtolist")
def addToList(request: Request, cfsListNames: str = Form(...), uriToAdd: str = Form(...)):
    # remove protocol from urls
    if uriToAdd.find("htt") != -1:
        cleanUri = uriToAdd.split('//')
        if cleanUri[0].find('http') != -1:
            cleanUri.pop(0)
            uriToAdd = ".".join(cleanUri)

    # remove www subdomain from urls
    if uriToAdd.find('ww') != -1:
        cleanUri = uriToAdd.split('.')
        if cleanUri[0].find('ww') != -1:
            cleanUri.pop(0)
            uriToAdd = ".".join(cleanUri)

    response = insertIntoCFS(fwAddress, cfsListNames, uriToAdd)

    if response.status_code == 200:
       response = commitChanges(fwAddress)

    if response.status_code == 200:
        return RedirectResponse(url=f"/showcfslist/{cfsListNames}", status_code=303)
    else:
        return PlainTextResponse(f"Error {response.text}")

@app.post("/removefromlist")
def removeFromList(cfsListName: str = Form(...), uriToDel: str = Form(...)):
    # remove protocol from urls
    if uriToDel.find("htt") != -1:
        cleanUri = uriToDel.split('//')
        if cleanUri[0].find('http') != -1:
            cleanUri.pop(0)
            uriToDel = ".".join(cleanUri)

    # remove www subdomain from urls
    if uriToDel.find('ww') != -1:
        cleanUri = uriToDel.split('.')
        if cleanUri[0].find('ww') != -1:
            cleanUri.pop(0)
            uriToDel = ".".join(cleanUri)

    response = removeFromCFS(fwAddress, cfsListName, uriToDel)
    
    if response.status_code == 200:
       response = commitChanges(fwAddress)

    if response.status_code == 200:
        return RedirectResponse(url=f"/showcfslist/{cfsListName}", status_code=303)
    else:
        return PlainTextResponse(f"Error {response.text}")

@app.get("/configmode")
def preemptMode(request: Request):
    response = configMode(fwAddress)
    return PlainTextResponse(response.text)
