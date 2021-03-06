from typing import Optional
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
    username: Optional[str]
    fwID: Optional[str]
    fwIndex: Optional[str]

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

class RedirectException(Exception):
    def __init__(self, name: str):
        self.name = name

verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=RedirectException("name")
)

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="views")

@app.exception_handler(RedirectException)
async def redirect_exception_handler(request: Request, exc: RedirectException):
    return RedirectResponse("/", status_code=301)

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

@app.get("/showcfslists", dependencies=[Depends(cookie)])
def showLists(request: Request, session_data: SessionData = Depends(verifier)):
    fwCredentials = db.firewallsCollection.find_one({'_id': ObjectId(session_data.fwID)})
    fwAddress = fwCredentials['fwAddress'][session_data.fwIndex] + ":" + fwCredentials['fwPort']
    response = snwl.getCFSLists(fwAddress, False)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("show_uri_list.html", {"request": request, "uriLists": response})

@app.get("/showcfslist/{name}", dependencies=[Depends(cookie)])
def showList(request: Request, name: str = Path(...), session_data: SessionData = Depends(verifier)):
    fwCredentials = db.firewallsCollection.find_one({'_id': ObjectId(session_data.fwID)})
    fwAddress = fwCredentials['fwAddress'][session_data.fwIndex] + ":" + fwCredentials['fwPort']
    response = snwl.getSpecificCFSList(fwAddress, name, False)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("show_uri_list.html", {"request": request, "uriLists": response})

@app.post("/login")
async def loginToPortal(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    username = username.lower()
    searchUser = db.usersCollection.find_one({'username': username})

    async def create_session(name: str, response: Response):
        session = uuid4()
        data = SessionData(username=name)

        await backend.create(session, data)
        cookie.attach_to_response(response, session)

        return f"created session for {name}"

    if not searchUser:
        return PlainTextResponse("Usu??rio n??o encontrado!")
    
    hasher = PasswordHasher()
    try: 
        hasher.verify(searchUser['password'], password)
    except:
        return PlainTextResponse("Usu??rio ou senha incorreta")

    await create_session(username, response)
    return RedirectResponse("/portal", status_code=301, headers=response.headers)

@app.post("/fwlogin", dependencies=[Depends(cookie)])
async def loginToAPI(request: Request, res: Response, fwList: str = Form(...), session_data: SessionData = Depends(verifier), session_id: UUID = Depends(cookie)):

    fw = db.firewallsCollection.find_one({'_id': ObjectId(fwList)})
    index = -1
    for address in fw['fwAddress']:
        try:
            index = index + 1
            fwAddress = address + ":" + fw['fwPort']
            fwUser = fw['fwUser']
            fwPassword = fw['fwPassword']

            # protocol validation at firewall address
            if fwAddress.find("https://") == -1:
                fwAddress = ("https://" + fwAddress)

            response = snwl.fwLogin(fwAddress, fwUser, fwPassword, False)

            if response['status']['success'] == True:
                session_data.fwID = fwList
                session_data.fwIndex = index

                await backend.update(session_id, session_data)
                return RedirectResponse("/portal", status_code=301, headers=res.headers)
        except:
            continue
    raise HTTPException(403, "Erro ao conectar no firewall!")

@app.get("/logout", dependencies=[Depends(cookie)])
def logoutFromAPI(res: Response, session_data: SessionData = Depends(verifier)):
    fwCredentials = db.firewallsCollection.find_one({'_id': ObjectId(session_data.fwID)})
    fwAddress = fwCredentials['fwAddress'][session_data.fwIndex] + ":" + fwCredentials['fwPort']
    response = snwl.fwLogout(fwAddress, False)
    
    if response['status']['success'] == True:

        return RedirectResponse("/portal", status_code=301, headers=res.headers)

@app.get("/addtolist", dependencies=[Depends(cookie)])
def addToList(request: Request, session_data: SessionData = Depends(verifier)):
    fwCredentials = db.firewallsCollection.find_one({'_id': ObjectId(session_data.fwID)})
    fwAddress = fwCredentials['fwAddress'][session_data.fwIndex] + ":" + fwCredentials['fwPort']
    response = snwl.getCFSLists(fwAddress, False)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response.text}")
    else:
        return templates.TemplateResponse("/add_to_list.html", {"request": request, "uriLists": response['content_filter']})

@app.post("/addtolist", dependencies=[Depends(cookie)])
async def addToList(request: Request, cfsListNames: str = Form(...), uriToAdd: str = Form(...), mode: str = Form(...), session_data: SessionData = Depends(verifier)):
    fwCredentials = db.firewallsCollection.find_one({'_id': ObjectId(session_data.fwID)})
    fwAddress = fwCredentials['fwAddress'][session_data.fwIndex] + ":" + fwCredentials['fwPort']

    if mode == 'domain':
        # url validations: remove protocols and subdomains
        cleanUri = tldextract.extract(uriToAdd)
        uriToAdd = (cleanUri.domain + '.' + cleanUri.suffix)
        response = snwl.insertIntoCFSList(fwAddress, cfsListNames, uriToAdd, False)
    else:
        response = snwl.insertIntoCFSList(fwAddress, cfsListNames, uriToAdd, False)
        
    if response['status']['success'] == True:
       response = snwl.commitChanges(fwAddress, False)

    if response['status']['success'] == True:
        return RedirectResponse(url=f"/showcfslist/{cfsListNames}", status_code=303)
    else:
        return PlainTextResponse(f"Error {response}")

@app.get("/removefromlist", dependencies=[Depends(cookie)])
def removeFromList(request: Request, session_data: SessionData = Depends(verifier)):
    fwCredentials = db.firewallsCollection.find_one({'_id': ObjectId(session_data.fwID)})
    fwAddress = fwCredentials['fwAddress'][session_data.fwIndex] + ":" + fwCredentials['fwPort']
    response = snwl.getCFSLists(fwAddress, False)

    if hasattr(response, "status_code") == True:
        return PlainTextResponse(f"Error {response}")
    else:
        return templates.TemplateResponse("remove_from_list.html", {"request": request, "uriLists": response['content_filter']})

@app.post("/removefromlist", dependencies=[Depends(cookie)])
def removeFromList(cfsListName: str = Form(...), uriToDel: str = Form(...), session_data: SessionData = Depends(verifier)):
    fwCredentials = db.firewallsCollection.find_one({'_id': ObjectId(session_data.fwID)})
    fwAddress = fwCredentials['fwAddress'][session_data.fwIndex] + ":" + fwCredentials['fwPort']

    response = snwl.removeFromCFS(fwAddress, cfsListName, uriToDel, False)
    
    if response['status']['success'] == True:
       response = snwl.commitChanges(fwAddress, False)

    if response['status']['success'] == True:
        return RedirectResponse(url=f"/showcfslist/{cfsListName}", status_code=303)
    else:
        return PlainTextResponse(f"Error {response}")

@app.get("/portal", dependencies=[Depends(cookie)])
def portal(request: Request, session_data: SessionData = Depends(verifier)):
    userDocument = db.usersCollection.find_one({'username': session_data.username})
    userCompanyID = userDocument['companyID']
    isSuperAdmin = False

    if userDocument['group'] == 'superadmin':
        isSuperAdmin = True

    if userDocument['group'] == 'admin' or userDocument['group'] == 'superadmin':
        fwList = db.firewallsCollection.find({})
    else:
        fwList = db.firewallsCollection.find({'companyID': userCompanyID})

    if session_data.fwID != None:
        connectedFw = db.firewallsCollection.find_one({'_id': ObjectId(session_data.fwID)})
        fwCommonName = connectedFw['fwCommonName']
        return templates.TemplateResponse("portal.html", {"request": request, "fwList": fwList, "fwCommonName": fwCommonName, "isSuperAdmin": isSuperAdmin})
    else:
        return templates.TemplateResponse("portal.html", {"request": request, "fwList": fwList, "isSuperAdmin": isSuperAdmin})

@app.get("/configmode", dependencies=[Depends(cookie)])
def configmode(request: Request, session_data: SessionData = Depends(verifier)):
    fwCredentials = db.firewallsCollection.find_one({'_id': ObjectId(session_data.fwID)})
    fwAddress = fwCredentials['fwAddress'] + ":" + fwCredentials['fwPort']

    response = snwl.configMode(fwAddress, False)

# Admin routes -------------------------------------------------------------------------
@app.get("/admin", dependencies=[Depends(cookie)])
def admin(request: Request, session_data: SessionData = Depends(verifier)):
    userDocument = db.usersCollection.find_one({'username': session_data.username})
    userGroups = userDocument['group']

    if userGroups != "superadmin":
        return PlainTextResponse("Seu usu??rio n??o ?? admin!")
    else:
        return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/adduser", dependencies=[Depends(cookie)])
def addUser(request: Request, session_data: SessionData = Depends(verifier)):
    userDocument = db.usersCollection.find_one({'username': session_data.username})
    userGroups = userDocument['group']

    companies = db.companiesCollection.find({})

    if userGroups != "superadmin":
        return PlainTextResponse("Seu usu??rio n??o ?? admin!")
    else:
        return templates.TemplateResponse("adduser.html", {"request": request, "companies": companies})

@app.post("/adduser", dependencies=[Depends(cookie)])
def addUser(request: Request, res: Response, companyID: str = Form(...), name: str = Form(...), username: str = Form(...), password: str = Form(...), group: str = Form(...), session_data: SessionData = Depends(verifier)):
    userDocument = db.usersCollection.find_one({'username': session_data.username})
    userGroups = userDocument['group']

    if userGroups != "superadmin":
        return PlainTextResponse("Seu usu??rio n??o ?? admin!")
    else:
        validateUser = db.usersCollection.find_one({"username": username})
        if validateUser:
            return PlainTextResponse("Usu??rio j?? existe! Escolha outro por favor")
        else:
            hasher = PasswordHasher()
            password = hasher.hash(password)

            db.usersCollection.insert_one({'companyID': companyID, 'name': name, 'username': username, 'password': password, 'group': group})
            return RedirectResponse("/portal", status_code=301, headers=res.headers)

@app.get("/addcompany", dependencies=[Depends(cookie)])
def addCompany(request: Request, session_data: SessionData = Depends(verifier)):
    userDocument = db.usersCollection.find_one({'username': session_data.username})
    userGroups = userDocument['group']

    if userGroups != "superadmin":
        return PlainTextResponse("Seu usu??rio n??o ?? admin!")
    else:
        return templates.TemplateResponse("addcompany.html", {"request": request})

@app.post("/addcompany", dependencies=[Depends(cookie)])
def addCompany(request: Request, res: Response, companyName: str = Form(...), companyCNPJ: str = Form(...), session_data: SessionData = Depends(verifier)):
    userDocument = db.usersCollection.find_one({'username': session_data.username})
    userGroups = userDocument['group']

    if userGroups != "superadmin":
        return PlainTextResponse("Seu usu??rio n??o ?? admin!")
    else:
        countCompanies = db.companiesCollection.count_documents({})
        companyID = str((countCompanies + 1))
        searchCNPJ = db.companiesCollection.find_one({'companyCNPJ': companyCNPJ})
    
    if searchCNPJ:
        return PlainTextResponse("Essa empresa j?? foi cadastrada!")
    else:
        db.companiesCollection.insert_one({'companyID': companyID, 'companyName': companyName, 'companyCNPJ': companyCNPJ})
        return RedirectResponse("/portal", status_code=301, headers=res.headers)

@app.get("/addfirewall", dependencies=[Depends(cookie)])
def addFirewall(request: Request, session_data: SessionData = Depends(verifier)):
    userDocument = db.usersCollection.find_one({'username': session_data.username})
    userGroups = userDocument['group']

    if userGroups != "superadmin":
        return PlainTextResponse("Seu usu??rio n??o ?? admin!")
    else:
        companies = db.companiesCollection.find({})
        return templates.TemplateResponse("/addfirewall.html", {'request': request, 'companies': companies})

@app.post("/addfirewall", dependencies=[Depends(cookie)])
def addFirewall(request: Request, res: Response, companyID: str = Form(...), fwCommonName: str = Form(...), address: list = Form(...), port: str = Form(...), user: str = Form(...), password: str = Form(...), session_data: SessionData = Depends(verifier)):
    userDocument = db.usersCollection.find_one({'username': session_data.username})
    userGroups = userDocument['group']

    if userGroups != "superadmin":
        return PlainTextResponse("Seu usu??rio n??o ?? admin!")
    else:    
        db.firewallsCollection.insert_one({'fwAddress': address, 'fwPort': port, 'fwUser': user, 'fwPassword': password, 'companyID': companyID, 'fwCommonName': fwCommonName})
        return RedirectResponse("/portal", status_code=301, headers=res.headers)