import tldextract
from sonicos_api import sonicOS as snwl
from fastapi import FastAPI, HTTPException
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
    response = snwl.getCFSLists(currentFwAddress, False)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("show_uri_list.html", {"request": request, "uriLists": response})

@app.get("/showcfslist/{name}")
def showList(request: Request, name: str = Path(...)):
    response = snwl.getSpecificCFSList(currentFwAddress, name, False)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("show_uri_list.html", {"request": request, "uriLists": response})

@app.post("/login")
def loginToAPI(request: Request, fwAddress: str = Form(...), fwUser: str = Form(...), fwPassword: str = Form(...)):
    global currentFwAddress
    currentFwAddress = fwAddress
    
    # protocol validation at firewall address
    if fwAddress.find("https://") == -1:
        fwAddress = ("https://" + fwAddress)
        currentFwAddress = fwAddress

    try:
        response = snwl.fwLogin(fwAddress, fwUser, fwPassword, False)
        print(response)
    except:
        raise HTTPException(403, "Erro ao conectar no firewall!")

    if response['status']['success'] == True:
        return RedirectResponse("/portal", status_code=303)
    else:
        return PlainTextResponse(f"Error: {response.text}")

@app.get("/logout")
def logoutFromAPI():
    response = snwl.fwLogout(currentFwAddress, False)

    if response.status_code == 200:
        return PlainTextResponse("Logout realizado com sucesso!")
    else:
        return PlainTextResponse(f"Error {response.text}")

@app.get("/addtolist")
def addToList(request: Request):
    response = snwl.getCFSLists(currentFwAddress, False)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("/add_to_list.html", {"request": request, "uriLists": response})

@app.post("/addtolist")
def addToList(request: Request, cfsListNames: str = Form(...), uriToAdd: str = Form(...)):
    
    # url validations: remove protocols and subdomains
    cleanUri = tldextract.extract(uriToAdd)
    uriToAdd = (cleanUri.domain + '.' + cleanUri.suffix)

    response = snwl.insertIntoCFSList(currentFwAddress, cfsListNames, uriToAdd, False)

    if response.status_code == 200:
       response = snwl.commitChanges(currentFwAddress, False)

    if response.status_code == 200:
        return RedirectResponse(url=f"/showcfslist/{cfsListNames}", status_code=303)
    else:
        return PlainTextResponse(f"Error {response.text}")

@app.get("/removefromlist")
def removeFromList(request: Request):
    response = snwl.getCFSLists(currentFwAddress, False)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("remove_from_list.html", {"request": request, "uriLists": response})

@app.post("/removefromlist")
def removeFromList(cfsListName: str = Form(...), uriToDel: str = Form(...)):
    
    # url validations: remove protocols and subdomains
    cleanUri = tldextract.extract(uriToDel)
    uriToDel = (cleanUri.domain + '.' + cleanUri.suffix)

    response = snwl.removeFromCFS(currentFwAddress, cfsListName, uriToDel, False)
    
    if response.status_code == 200:
       response = snwl.commitChanges(currentFwAddress, False)

    if response.status_code == 200:
        return RedirectResponse(url=f"/showcfslist/{cfsListName}", status_code=303)
    else:
        return PlainTextResponse(f"Error {response.text}")

@app.get("/configmode")
def preemptMode(request: Request):
    response = snwl.configMode(currentFwAddress, False)
    return PlainTextResponse(response.text)

@app.get("/portal")
def portal(request: Request):
    response = snwl.getFwInfo(currentFwAddress, False)
    currentFwName = response['firewall_name']

    return templates.TemplateResponse("portal.html", {"request": request, "currentFwName": currentFwName})