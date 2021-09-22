import tldextract
from sonicOS import * 
from fastapi import FastAPI, HTTPException
from fastapi.params import Form, Path
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse, RedirectResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="views")

origins = [
    "http://localhost:3000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/showcfslists")
def showLists(request: Request):
    response = getCFSLists(currentFwAddress)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return response

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
    
    # protocol validation at firewall address
    if fwAddress.find("https://") == -1:
        fwAddress = ("https://" + fwAddress)
        currentFwAddress = fwAddress

    try:
        response = login(fwAddress, fwUser, fwPassword)
    except:
        raise HTTPException(403, "Erro ao conectar no firewall!")

    if response.status_code == 200:
        return response.json
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
        return templates.TemplateResponse("/add_to_list.html", {"request": request, "uriLists": response})

@app.post("/addtolist")
def addToList(request: Request, cfsListNames: str = Form(...), uriToAdd: str = Form(...)):
    
    # url validations: remove protocols and subdomains
    cleanUri = tldextract.extract(uriToAdd)
    uriToAdd = (cleanUri.domain + '.' + cleanUri.suffix)

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
    
    # url validations: remove protocols and subdomains
    cleanUri = tldextract.extract(uriToDel)
    uriToDel = (cleanUri.domain + '.' + cleanUri.suffix)

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