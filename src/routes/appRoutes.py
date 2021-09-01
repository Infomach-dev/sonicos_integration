from sonicOS import * 
from validations import removeProtocols, removeWWW
from fastapi import FastAPI
from fastapi.params import Form, Path
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import PlainTextResponse, RedirectResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="views")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/showcfslists")
def showLists(request: Request):
    response = getCFSLists(currentFwAddress)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("show_uri_list.html", {"request": request, "uriLists": response})

@app.get("/showcfslist/{name}")
def showList(request: Request, name: str = Path(...)):
    response = getSpecificCFSList(currentFwAddress, name)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("show_uri_list.html", {"request": request, "uriLists": response})

@app.post("/login")
def loginToAPI(request: Request, fwAddress: str = Form(...), fwUser: str = Form(...), fwPassword: str = Form(...)):
    global currentFwAddress
    currentFwAddress = fwAddress
    
    fwAddress = removeProtocols(fwAddress)
    fwAddress = removeWWW(fwAddress)

    response = login(fwAddress, fwUser, fwPassword)
    if response.status_code == 200:
        return RedirectResponse("/portal", status_code=303)
    else:
        return PlainTextResponse(f"Error: {response.text}")

@app.get("/logout")
def logoutFromAPI():
    response = logout(currentFwAddress)

    if response.status_code == 200:
        return PlainTextResponse("Logout realizado com sucesso!")
    else:
        return PlainTextResponse(f"Error {response.text}")

@app.get("/addtolist")
def addToList(request: Request):
    response = getCFSLists(currentFwAddress)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("/cfsoptions.html", {"request": request, "uriLists": response})

@app.post("/addtolist")
def addToList(request: Request, cfsListNames: str = Form(...), uriToAdd: str = Form(...)):
    
    uriToAdd = removeProtocols(uriToAdd)
    uriToAdd = removeWWW(uriToAdd)

    response = insertIntoCFS(currentFwAddress, cfsListNames, uriToAdd)

    if response.status_code == 200:
       response = commitChanges(currentFwAddress)

    if response.status_code == 200:
        return RedirectResponse(url=f"/showcfslist/{cfsListNames}", status_code=303)
    else:
        return PlainTextResponse(f"Error {response.text}")

@app.get("/removefromlist")
def removeFromList(request: Request):
    response = getCFSLists(currentFwAddress)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("remove_from_list.html", {"request": request, "uriLists": response})

@app.post("/removefromlist")
def removeFromList(cfsListName: str = Form(...), uriToDel: str = Form(...)):
    
    uriToDel = removeProtocols(uriToDel)
    uriToDel = removeWWW(uriToDel)

    response = removeFromCFS(currentFwAddress, cfsListName, uriToDel)
    
    if response.status_code == 200:
       response = commitChanges(currentFwAddress)

    if response.status_code == 200:
        return RedirectResponse(url=f"/showcfslist/{cfsListName}", status_code=303)
    else:
        return PlainTextResponse(f"Error {response.text}")

@app.get("/configmode")
def preemptMode(request: Request):
    response = configMode(currentFwAddress)
    return PlainTextResponse(response.text)

@app.get("/portal")
def portal(request: Request):
    response = getFwInfo(currentFwAddress)
    currentFwName = response['firewall_name']

    return templates.TemplateResponse("portal.html", {"request": request, "currentFwName": currentFwName})