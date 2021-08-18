from requests.api import get
from starlette.responses import PlainTextResponse, RedirectResponse
from sonicOS import * 
from fastapi import FastAPI
from fastapi.params import Form
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="views")

sonicIP = "192.168.1.250"

@app.get("/")
def index(request: Request):
    response = getCFSLists(sonicIP)
    return templates.TemplateResponse("index.html", {"request": request, "uriLists": response})

@app.get("/showcfslists")
def showLists(request: Request):
    response = getCFSLists(sonicIP)

    if type(response) == int:
        return PlainTextResponse(f"Error {response}")
    else:
        return templates.TemplateResponse("show_uri_list.html", {"request": request, "uriLists": response})

@app.get("/login")
def loginToAPI(): 
    response = login(sonicIP)
    if response.status_code == 200:
        return PlainTextResponse("Logado com sucesso!")
    else:
        return PlainTextResponse(f"Error: {response.text}")

@app.get("/logout")
def logoutFromAPI():
    response = logout(sonicIP)

    if response == 200:
        return PlainTextResponse("Logout realizado com sucesso!")
    else:
        return PlainTextResponse(f"Error {response}")

@app.post("/addtolist")
def form_post(request: Request, cfsListNames: str = Form(...), uriToAdd: str = Form(...)):
    response = insertIntoCFS(sonicIP, cfsListNames, uriToAdd)

    if response.status_code == 200:
       response = commitChanges(sonicIP)

    if response.status_code == 200:
        return PlainTextResponse("Liberação realizada com sucesso!")
    else:
        return PlainTextResponse(f"Error {response.text}")

@app.get("/configmode")
def preemptMode(request: Request):
    response = configMode(sonicIP)
    return PlainTextResponse(response.text)

