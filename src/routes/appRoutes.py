from pymongo import response
import requests
import tldextract
from db import main as db
from argon2 import PasswordHasher
from bson.objectid import ObjectId
from sonicos_api import sonicOS as snwl
from fastapi import FastAPI, HTTPException
from fastapi.params import Form, Path
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import PlainTextResponse, RedirectResponse

from pydantic import BaseModel
from fastapi import HTTPException, FastAPI, Response, Depends
from uuid import UUID, uuid4

from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters


class SessionData(BaseModel):
    username: str


cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)
backend = InMemoryBackend[UUID, SessionData]()


class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True


verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="views")

@app.post("/create_session/{name}")
async def create_session(name: str, response: Response):

    session = uuid4()
    data = SessionData(username=name)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return f"created session for {name}"


@app.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data


@app.post("/delete_session")
async def del_session(response: Response, session_id: UUID = Depends(cookie)):
    await backend.delete(session_id)
    cookie.delete_from_response(response)
    return "deleted session"

# -------------------------------------------------------------------------------------------------------

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
async def loginToPortal(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    searchUser = db.usersCollection.find_one({'username': username})

    async def create_session(name: str, response: Response):
        session = uuid4()
        data = SessionData(username=name)

        await backend.create(session, data)
        cookie.attach_to_response(response, session)

        return f"created session for {name}"

    if not searchUser:
        return PlainTextResponse("Usuário não encontrado!")
    
    hasher = PasswordHasher()
    try: 
        hasher.verify(searchUser['password'], password)
    except:
        return PlainTextResponse("Usuário ou senha incorreta")

    await create_session(username, response)
    return RedirectResponse("/portal", status_code=301, headers=response.headers)
    # return PlainTextResponse(f"Sessão criada para {username}!")


@app.post("/fwlogin")
def loginToAPI(request: Request, _id: str = Form(...)):

    fw = db.firewallsCollection.find_one({'_id': ObjectId(_id)})
    fwAddress = fw['fwAddress'] + ":" + fw['fwPort']
    fwUser = fw['fwUser']
    fwPassword = fw['fwPassword']

    # protocol validation at firewall address
    if fwAddress.find("https://") == -1:
        fwAddress = ("https://" + fwAddress)

    try:
        response = snwl.fwLogin(fwAddress, fwUser, fwPassword, False)
    except:
        raise HTTPException(403, "Erro ao conectar no firewall!")

    if response['status']['success'] == True:
        return RedirectResponse("/portal", status_code=303)
    else:
        return PlainTextResponse(f"Error: {response}")

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
    fwList = db.firewallsCollection.find({'companyID': '1'})

    return templates.TemplateResponse("portal.html", {"request": request, "fwList": fwList})