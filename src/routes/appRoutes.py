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
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/showcfslists")
def showLists(request: Request):
    uriLists = getCFSLists(sonicIP)
    return templates.TemplateResponse("show_uri_list.html", {"request": request, "uriLists": uriLists})

@app.post("/login")
def loginToAPI(): 
    login(sonicIP)

@app.post("/insertcfs/")
def form_post(request: Request, cfsProfile: str = Form(...), uriToAdd: str = Form(...)):
    insertIntoCFS(sonicIP, cfsProfile, uriToAdd)
    commitChanges(sonicIP)
    return PlainTextResponse("Liberação realizada com sucesso!")
